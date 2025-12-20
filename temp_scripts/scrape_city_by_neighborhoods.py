"""Final scraper: Query city by neighborhoods.

Uses neighborhood mapping to scrape all listings for a city.
Can work with:
1. Direct neighborhood file (all_tel_aviv_neighborhoods.json)
2. City-to-neighborhoods mapping (city_to_neighborhoods.json)
"""
import json
import time
from datetime import datetime
from pathlib import Path
from scraper.api_client import Yad2ApiClient
from scraper.config import ScraperConfig
from scraper.parser import ListingParser
from scraper.exporter import ParquetExporter

# Tel Aviv city names (as they appear in API)
TEL_AVIV_NAMES = ["תל אביב יפו", "תל אביב"]


def load_neighborhoods_for_city(city_name: str):
    """
    Load neighborhood IDs for a given city.
    
    Tries multiple methods:
    1. city_to_neighborhoods.json (if exists)
    2. Direct neighborhood file (all_tel_aviv_neighborhoods.json)
    3. tel_aviv_neighborhoods.json (if exists)
    """
    neighborhoods = {}
    
    # Load from data/mappings/ directory
    from pathlib import Path
    
    # Get project root (where this script is located)
    script_dir = Path(__file__).parent
    mappings_dir = script_dir / "data" / "mappings"
    
    city_map_path = mappings_dir / "city_to_neighborhoods.json"
    details_path = mappings_dir / "neighborhood_details.json"
    
    # Method 1: Try city_to_neighborhoods.json (primary method)
    try:
        with open(city_map_path, "r", encoding="utf-8") as f:
            city_map = json.load(f)
        if city_name in city_map:
            nids = city_map[city_name]
            # Load details from neighborhood_details.json
            try:
                with open(details_path, "r", encoding="utf-8") as f2:
                    details = json.load(f2)
                neighborhoods = {int(nid): details[str(nid)] for nid in nids if str(nid) in details}
            except FileNotFoundError:
                # Just use IDs without details
                neighborhoods = {int(nid): {"name": f"Neighborhood {nid}"} for nid in nids}
            print(f"Loaded {len(neighborhoods)} neighborhoods from {city_map_path}")
            return neighborhoods
    except FileNotFoundError:
        pass
    
    raise FileNotFoundError("No neighborhood mapping file found!")


def scrape_city_by_neighborhoods(city_name: str, city_id: int = None):
    """
    Scrape all listings for a city by querying each neighborhood.
    
    Args:
        city_name: City name in Hebrew (e.g., "תל אביב יפו")
        city_id: Optional city ID (defaults to looking up from config)
    """
    print("=" * 70)
    print(f"Scraping {city_name} by Neighborhoods")
    print("=" * 70)
    
    # Load neighborhoods
    try:
        neighborhoods = load_neighborhoods_for_city(city_name)
    except FileNotFoundError as e:
        print(f"\nERROR: {e}")
        print("\nPlease run build_neighborhood_city_map.py first to create mapping files")
        return None
    
    print(f"\nFound {len(neighborhoods)} neighborhoods for {city_name}")
    
    # Get city ID if not provided
    if city_id is None:
        config = ScraperConfig()
        try:
            city_id = config.get_city_id(city_name)
        except ValueError:
            # Try common Tel Aviv IDs
            if city_name in TEL_AVIV_NAMES:
                city_id = 5000
            else:
                print(f"ERROR: Could not determine city ID for {city_name}")
                return None
    
    print(f"Using city ID: {city_id}")
    
    # Initialize components
    config = ScraperConfig()
    client = Yad2ApiClient(config)
    parser = ListingParser()
    exporter = ParquetExporter()
    
    print("\nInitializing session...")
    client.init_session()
    
    all_listings = {}  # url -> Listing (for deduplication)
    stats = {
        "total_requests": 0,
        "total_listings": 0,
        "city_listings": 0,
        "errors": 0,
        "neighborhoods_processed": 0,
    }
    
    print(f"\nQuerying {len(neighborhoods)} neighborhoods...")
    print("=" * 70)
    
    # Query each neighborhood
    for idx, (nid, info) in enumerate(sorted(neighborhoods.items()), 1):
        neighborhood_name = info.get("name", f"Neighborhood {nid}")
        expected_count = info.get("tel_aviv_listings", info.get("total_listings", 0))
        
        try:
            url = f"https://gw.yad2.co.il/realestate-feed/forsale/map?city={city_id}&neighborhood={nid}"
            response = client.session.get(url, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            markers = data.get("data", {}).get("markers", [])
            listings = parser.parse_map_response(data)
            
            stats["total_requests"] += 1
            stats["total_listings"] += len(listings)
            
            # Deduplicate by URL
            new_count = 0
            for listing in listings:
                if listing.url not in all_listings:
                    all_listings[listing.url] = listing
                    new_count += 1
                    # Count city listings
                    if listing.city in TEL_AVIV_NAMES or listing.city == city_name:
                        stats["city_listings"] += 1
            
            status = "OK" if new_count > 0 else "SKIP"
            print(f"  [{idx}/{len(neighborhoods)}] ID {nid}: {neighborhood_name}")
            print(f"    -> {len(listings)} listings, +{new_count} new [{status}]")
            
            stats["neighborhoods_processed"] += 1
            
        except Exception as e:
            stats["errors"] += 1
            print(f"  [{idx}/{len(neighborhoods)}] ID {nid}: ERROR - {e}")
        
        time.sleep(0.2)  # Rate limiting
    
    print("\n" + "=" * 70)
    print("SCRAPING COMPLETE")
    print("=" * 70)
    print(f"Total API requests: {stats['total_requests']}")
    print(f"Neighborhoods processed: {stats['neighborhoods_processed']}")
    print(f"Total listings scraped: {stats['total_listings']}")
    print(f"Unique listings: {len(all_listings)}")
    print(f"City listings ({city_name}): {stats['city_listings']}")
    print(f"Errors: {stats['errors']}")
    print("=" * 70)
    
    if all_listings:
        # Export to Parquet using new structure: {city_name}/{YYYYMMDD}_{city_name}.parquet
        listings_list = list(all_listings.values())
        output_path = exporter.export(
            listings_list,
            output_path="",  # Ignored when using structured mode
            city_name=city_name,
            base_output_path=config.output_path,
            date=datetime.now(),
        )
        print(f"\nExported to: {output_path}")
        
        # Show statistics
        print("\n" + "=" * 70)
        print("Final Statistics:")
        print("=" * 70)
        
        # City distribution
        from collections import Counter
        city_counts = Counter(listing.city for listing in listings_list)
        print(f"\nCity distribution:")
        for city, count in city_counts.most_common(10):
            print(f"  {city}: {count} listings ({count/len(listings_list)*100:.1f}%)")
        
        # Sample listings
        print("\nSample listings:")
        for listing in listings_list[:5]:
            price_str = f"{listing.price:,} ILS" if listing.price else "Price N/A"
            print(f"  - {listing.city} - {listing.neighborhood}: {listing.address}, "
                  f"{listing.rooms} rooms, {price_str}")
        
        return output_path
    else:
        print("\nNo listings found!")
        return None
    
    client.close()


def main():
    """Main function - scrape Tel Aviv by neighborhoods."""
    city_name = "תל אביב יפו"  # Can be changed to any city
    output_path = scrape_city_by_neighborhoods(city_name)
    
    if output_path:
        print(f"\nSUCCESS: Successfully scraped {city_name}")
        print(f"  Output file: {output_path}")
    else:
        print(f"\nFAILED: Failed to scrape {city_name}")


if __name__ == "__main__":
    main()


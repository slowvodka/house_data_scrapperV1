"""
Command Line Interface for Yad2 Real Estate Scraper.

Provides CLI commands to scrape cities and list available cities.
"""

import argparse
import json
import sys
from pathlib import Path
from typing import List, Optional

from scraper.api_client import Yad2ApiClient
from scraper.config import ScraperConfig
from scraper.exporter import ParquetExporter
from scraper.parser import ListingParser

# Path to mappings directory
MAPPINGS_DIR = Path(__file__).parent.parent / "data" / "mappings"
CITY_TO_NEIGHBORHOODS_FILE = MAPPINGS_DIR / "city_to_neighborhoods.json"
NEIGHBORHOOD_DETAILS_FILE = MAPPINGS_DIR / "neighborhood_details.json"

# Tel Aviv city names (as they appear in API)
TEL_AVIV_NAMES = ["תל אביב יפו", "תל אביב"]

# English to Hebrew city name mapping
# This allows CLI to accept English names and convert them internally
ENGLISH_TO_HEBREW_CITY_MAP = {
    # Major cities
    "tel aviv": "תל אביב יפו",
    "tel-aviv": "תל אביב יפו",
    "tel_aviv": "תל אביב יפו",
    "telaviv": "תל אביב יפו",
    "jerusalem": "ירושלים",
    "haifa": "חיפה",
    "beer sheva": "באר שבע",
    "beersheba": "באר שבע",
    "beer-sheva": "באר שבע",
    "rishon lezion": "ראשון לציון",
    "petah tikva": "פתח תקווה",
    "petah-tikva": "פתח תקווה",
    "ashdod": "אשדוד",
    "netanya": "נתניה",
    "holon": "חולון",
    "bnei brak": "בני ברק",
    "bnei-brak": "בני ברק",
    "ramat gan": "רמת גן",
    "ramat-gan": "רמת גן",
    "ramatgan": "רמת גן",
    "givatayim": "גבעתיים",
    "ashkelon": "אשקלון",
    "rehovot": "רחובות",
    "bat yam": "בת ים",
    "bat-yam": "בת ים",
    "batyam": "בת ים",
    "herzliya": "הרצליה",
    "kfar saba": "כפר סבא",
    "kfar-saba": "כפר סבא",
    "modiin": "מודיעין",
    "raanana": "רעננה",
    "nazareth": "נצרת",
    # Common variations
    "ta": "תל אביב יפו",
    "tlv": "תל אביב יפו",
}


def normalize_city_name(city_name: str) -> str:
    """
    Normalize city name: convert English to Hebrew if needed.
    
    Args:
        city_name: City name in English or Hebrew.
        
    Returns:
        Hebrew city name.
        
    Raises:
        KeyError: If city name not found in mapping or English map.
    """
    # Check if it's already Hebrew (contains Hebrew characters)
    # Hebrew Unicode range: \u0590-\u05FF
    has_hebrew = any('\u0590' <= char <= '\u05FF' for char in city_name)
    
    if has_hebrew:
        # Already Hebrew, return as-is
        return city_name
    
    # Try English-to-Hebrew mapping (case-insensitive)
    city_lower = city_name.lower().strip()
    
    if city_lower in ENGLISH_TO_HEBREW_CITY_MAP:
        return ENGLISH_TO_HEBREW_CITY_MAP[city_lower]
    
    # Not found in English map, try direct lookup (maybe it's a Hebrew name without Hebrew chars?)
    # Or raise error
    raise KeyError(
        f"City '{city_name}' not found.\n"
        f"Available English names: {', '.join(sorted(set(ENGLISH_TO_HEBREW_CITY_MAP.keys())))}\n"
        f"Or use Hebrew names directly."
    )


def load_neighborhoods_for_city(city_name: str) -> dict:
    """
    Load neighborhood IDs for a given city.
    
    Args:
        city_name: City name in Hebrew.
        
    Returns:
        Dictionary mapping neighborhood ID to neighborhood info.
        
    Raises:
        FileNotFoundError: If mapping files don't exist.
        KeyError: If city not found in mappings.
    """
    if not CITY_TO_NEIGHBORHOODS_FILE.exists():
        raise FileNotFoundError(
            f"Mapping file not found: {CITY_TO_NEIGHBORHOODS_FILE}\n"
            "Please ensure city_to_neighborhoods.json exists in data/mappings/"
        )
    
    with open(CITY_TO_NEIGHBORHOODS_FILE, "r", encoding="utf-8") as f:
        city_map = json.load(f)
    
    if city_name not in city_map:
        available = ", ".join(sorted(city_map.keys()))
        raise KeyError(
            f"City '{city_name}' not found in mappings.\n"
            f"Available cities: {available}"
        )
    
    nids = city_map[city_name]
    
    # Load details from neighborhood_details.json if available
    neighborhoods = {}
    if NEIGHBORHOOD_DETAILS_FILE.exists():
        try:
            with open(NEIGHBORHOOD_DETAILS_FILE, "r", encoding="utf-8") as f:
                details = json.load(f)
            neighborhoods = {
                int(nid): details[str(nid)] 
                for nid in nids 
                if str(nid) in details
            }
        except (json.JSONDecodeError, KeyError):
            pass
    
    # Fallback: create basic entries
    if not neighborhoods:
        neighborhoods = {int(nid): {"name": f"Neighborhood {nid}"} for nid in nids}
    
    return neighborhoods


def scrape_city(city_name: str, city_id: Optional[int] = None, verbose: bool = False) -> Optional[Path]:
    """
    Scrape all listings for a city by querying each neighborhood.
    
    Args:
        city_name: City name in English or Hebrew (e.g., "tel aviv" or "תל אביב יפו").
        city_id: Optional city ID (defaults to looking up from config).
        verbose: If True, show detailed progress output.
        
    Returns:
        Path to created Parquet file, or None if scraping failed.
    """
    # Normalize city name (convert English to Hebrew if needed)
    try:
        city_name_hebrew = normalize_city_name(city_name)
    except KeyError as e:
        print(f"\nERROR: {e}")
        return None
    
    if verbose:
        print("=" * 70)
        print(f"Scraping {city_name_hebrew} by Neighborhoods")
        if city_name != city_name_hebrew:
            print(f"(Input: {city_name})")
        print("=" * 70)
    
    # Load neighborhoods
    try:
        neighborhoods = load_neighborhoods_for_city(city_name_hebrew)
    except (FileNotFoundError, KeyError) as e:
        print(f"\nERROR: {e}")
        return None
    
    if verbose:
        print(f"\nFound {len(neighborhoods)} neighborhoods for {city_name_hebrew}")
    
    # Get city ID if not provided
    if city_id is None:
        config = ScraperConfig()
        try:
            city_id = config.get_city_id(city_name_hebrew)
        except ValueError:
            # Try common Tel Aviv IDs
            if city_name_hebrew in TEL_AVIV_NAMES:
                city_id = 5000
            else:
                print(f"ERROR: Could not determine city ID for {city_name_hebrew}")
                return None
    
    if verbose:
        print(f"Using city ID: {city_id}")
    
    # Initialize components
    config = ScraperConfig()
    client = Yad2ApiClient(config)
    parser = ListingParser()
    exporter = ParquetExporter()
    
    if verbose:
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
    
    if verbose:
        print(f"\nQuerying {len(neighborhoods)} neighborhoods...")
        print("=" * 70)
    
    # Query each neighborhood
    import time
    for idx, (nid, info) in enumerate(sorted(neighborhoods.items()), 1):
        neighborhood_name = info.get("name", f"Neighborhood {nid}")
        
        try:
            url = f"https://gw.yad2.co.il/realestate-feed/forsale/map?city={city_id}&neighborhood={nid}"
            response = client.session.get(url, timeout=10)
            response.raise_for_status()
            data = response.json()
            
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
                    if listing.city in TEL_AVIV_NAMES or listing.city == city_name_hebrew:
                        stats["city_listings"] += 1
            
            if verbose:
                status = "OK" if new_count > 0 else "SKIP"
                print(f"  [{idx}/{len(neighborhoods)}] ID {nid}: {neighborhood_name}")
                print(f"    -> {len(listings)} listings, +{new_count} new [{status}]")
            
            stats["neighborhoods_processed"] += 1
            
        except Exception as e:
            stats["errors"] += 1
            if verbose:
                print(f"  [{idx}/{len(neighborhoods)}] ID {nid}: ERROR - {e}")
        
        time.sleep(0.2)  # Rate limiting
    
    if verbose:
        print("\n" + "=" * 70)
        print("SCRAPING COMPLETE")
        print("=" * 70)
        print(f"Total API requests: {stats['total_requests']}")
        print(f"Neighborhoods processed: {stats['neighborhoods_processed']}")
        print(f"Total listings scraped: {stats['total_listings']}")
        print(f"Unique listings: {len(all_listings)}")
        print(f"City listings ({city_name_hebrew}): {stats['city_listings']}")
        print(f"Errors: {stats['errors']}")
        print("=" * 70)
    
    if all_listings:
        # Export to Parquet
        listings_list = list(all_listings.values())
        from datetime import datetime
        
        output_path = exporter.export(
            listings_list,
            output_path="",  # Ignored when using structured mode
            city_name=city_name_hebrew,
            base_output_path=config.output_path,
            date=datetime.now(),
        )
        
        if verbose:
            print(f"\nExported to: {output_path}")
        
        client.close()
        return output_path
    else:
        if verbose:
            print("\nNo listings found!")
        client.close()
        return None


def scrape_command(cities: List[str], output: Optional[str] = None, verbose: bool = False) -> int:
    """
    Execute scrape command for one or more cities.
    
    Accepts English or Hebrew city names. English names are converted to Hebrew internally.
    
    Args:
        cities: List of city names to scrape (English or Hebrew).
        output: Optional custom output directory (overrides config).
        verbose: If True, show detailed output.
        
    Returns:
        Exit code: 0 for success, 1 for errors.
    """
    results = {}
    
    # Convert English names to Hebrew
    hebrew_cities = []
    for city in cities:
        try:
            hebrew_city = normalize_city_name(city)
            hebrew_cities.append(hebrew_city)
        except KeyError as e:
            print(f"\nERROR: {e}")
            results[city] = None
            continue
    
    for idx, city_name in enumerate(hebrew_cities, 1):
        if len(hebrew_cities) > 1:
            print(f"\n{'=' * 70}")
            print(f"CITY {idx}/{len(cities)}: {city_name}")
            print(f"{'=' * 70}\n")
        
        # Override output path if specified
        # Note: This requires passing output_path through scrape_city function
        # For now, we'll use the default config output_path
        # TODO: Add output_path parameter to scrape_city function
        
        output_path = scrape_city(city_name, verbose=verbose)
        
        if output_path:
            results[city_name] = output_path
            print(f"\nSUCCESS: {city_name}")
            print(f"  -> {output_path}")
        else:
            results[city_name] = None
            print(f"\nFAILED: {city_name}")
        
        # Delay between cities (except after last)
        if idx < len(hebrew_cities):
            import time
            time.sleep(2)
    
    # Summary
    if len(hebrew_cities) > 1:
        print("\n" + "=" * 70)
        print("SCRAPING SUMMARY")
        print("=" * 70)
        for city_name, output_path in results.items():
            status = "SUCCESS" if output_path else "FAILED"
            print(f"{status}: {city_name}")
            if output_path:
                print(f"  -> {output_path}")
        print("=" * 70)
    
    # Return error code if any failed
    return 0 if all(results.values()) else 1


def list_cities_command() -> int:
    """
    List all available cities from the mapping file.
    
    Shows both Hebrew names and English equivalents.
    
    Returns:
        Exit code: 0 for success, 1 for errors.
    """
    try:
        if not CITY_TO_NEIGHBORHOODS_FILE.exists():
            print(f"ERROR: Mapping file not found: {CITY_TO_NEIGHBORHOODS_FILE}")
            return 1
        
        with open(CITY_TO_NEIGHBORHOODS_FILE, "r", encoding="utf-8") as f:
            city_map = json.load(f)
        
        cities = sorted(city_map.keys())
        
        # Create reverse mapping (Hebrew -> English)
        hebrew_to_english = {v: k for k, v in ENGLISH_TO_HEBREW_CITY_MAP.items()}
        
        print("Available cities:")
        print("=" * 70)
        for city_hebrew in cities:
            neighborhood_count = len(city_map[city_hebrew])
            # Find English name if available
            english_names = [k for k, v in ENGLISH_TO_HEBREW_CITY_MAP.items() if v == city_hebrew]
            if english_names:
                english_display = f" ({', '.join(sorted(set(english_names))[:3])})"  # Show up to 3 variations
            else:
                english_display = ""
            print(f"  {city_hebrew}{english_display} ({neighborhood_count} neighborhoods)")
        print("=" * 70)
        print(f"Total: {len(cities)} cities")
        print("\nTip: Use English names in CLI (e.g., 'tel aviv', 'ramat gan')")
        
        return 0
        
    except Exception as e:
        print(f"ERROR: Failed to load cities: {e}")
        return 1


def parse_args(args: Optional[List[str]] = None) -> argparse.Namespace:
    """
    Parse command-line arguments.
    
    Args:
        args: Optional list of arguments (defaults to sys.argv[1:]).
        
    Returns:
        Parsed arguments namespace.
    """
    parser = argparse.ArgumentParser(
        description="Yad2 Real Estate Scraper - Scrape real estate listings from yad2.co.il",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s scrape "tel aviv"
  %(prog)s scrape "tel aviv" "ramat gan" "givatayim" "bat yam"
  %(prog)s scrape "tel aviv" --verbose
  %(prog)s scrape "tel aviv" --output custom/path
  %(prog)s list-cities
  
Note: City names can be in English (e.g., "tel aviv") or Hebrew (e.g., "תל אביב יפו").
        """
    )
    
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    
    # Scrape command
    scrape_parser = subparsers.add_parser("scrape", help="Scrape listings for one or more cities")
    scrape_parser.add_argument(
        "cities",
        nargs="+",
        help="City names to scrape (English or Hebrew, e.g., 'tel aviv' or 'תל אביב יפו')"
    )
    scrape_parser.add_argument(
        "--output", "-o",
        help="Custom output directory (default: data/output)"
    )
    scrape_parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Show detailed progress output"
    )
    
    # List cities command
    list_parser = subparsers.add_parser("list-cities", help="List all available cities")
    
    return parser.parse_args(args)


def main(args: Optional[List[str]] = None) -> int:
    """
    Main CLI entry point.
    
    Args:
        args: Optional list of arguments (defaults to sys.argv[1:]).
        
    Returns:
        Exit code: 0 for success, 1 for errors.
    """
    try:
        parsed_args = parse_args(args)
        
        if parsed_args.command == "scrape":
            return scrape_command(
                cities=parsed_args.cities,
                output=parsed_args.output,
                verbose=parsed_args.verbose
            )
        elif parsed_args.command == "list-cities":
            return list_cities_command()
        else:
            # No command provided - show help
            parse_args(["--help"])
            return 1
            
    except KeyboardInterrupt:
        print("\n\nInterrupted by user")
        return 1
    except Exception as e:
        print(f"ERROR: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())


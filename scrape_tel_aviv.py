"""Scrape Tel Aviv real estate listings using the map API."""
import time
from datetime import datetime
from pathlib import Path
from scraper.api_client import Yad2ApiClient
from scraper.config import ScraperConfig
from scraper.parser import ListingParser
from scraper.exporter import ParquetExporter

# Scraping parameters
CITY = "תל אביב"
GRID_SIZE = 25  # Larger grid for Gush Dan metropolitan area
ZOOM = 16  # Higher zoom for smaller areas

# Gush Dan bbox (includes Tel Aviv, Ramat Gan, Givatayim, Holon, Bat Yam, Bnei Brak)
# We'll filter to only Tel Aviv listings after scraping
GUSH_DAN_BBOX = (31.95, 34.70, 32.25, 34.92)

# Tel Aviv city names as returned by API (may include variations)
TEL_AVIV_NAMES = ["תל אביב יפו", "תל אביב"]  # API returns "תל אביב יפו"


def main():
    print("=" * 50)
    print(f"Scraping: {CITY}")
    print("=" * 50)

    config = ScraperConfig()
    client = Yad2ApiClient(config)
    parser = ListingParser()
    exporter = ParquetExporter()

    # Use Gush Dan bbox - covers metropolitan area
    lat_min, lon_min, lat_max, lon_max = GUSH_DAN_BBOX
    print(f"Bbox: {GUSH_DAN_BBOX} (Gush Dan metropolitan area)")
    print(f"Grid: {GRID_SIZE}x{GRID_SIZE}, Zoom: {ZOOM}")
    print("Note: Filtering to Tel Aviv listings only")

    # Initialize session
    print("\nInitializing session...")
    client.init_session()

    # Calculate grid steps
    lat_step = (lat_max - lat_min) / GRID_SIZE
    lon_step = (lon_max - lon_min) / GRID_SIZE

    all_listings = {}  # url -> Listing (for deduplication)
    total_scraped = 0  # Track total listings before filtering
    total_requests = GRID_SIZE * GRID_SIZE

    print(f"\nScraping {total_requests} grid cells...")

    request_count = 0
    for i in range(GRID_SIZE):
        for j in range(GRID_SIZE):
            request_count += 1
            cell_lat_min = lat_min + i * lat_step
            cell_lat_max = cell_lat_min + lat_step
            cell_lon_min = lon_min + j * lon_step
            cell_lon_max = cell_lon_min + lon_step
            cell_bbox = f"{cell_lat_min},{cell_lon_min},{cell_lat_max},{cell_lon_max}"

            try:
                result = client.fetch_map_listings(bbox=cell_bbox, zoom=ZOOM)
                listings = parser.parse_map_response(result)
                total_scraped += len(listings)

                # Filter to only Tel Aviv listings and deduplicate by URL
                new_count = 0
                for listing in listings:
                    # Only keep listings from Tel Aviv
                    if listing.city in TEL_AVIV_NAMES:
                        if listing.url not in all_listings:
                            all_listings[listing.url] = listing
                            new_count += 1

                print(f"  [{request_count}/{total_requests}] "
                      f"{len(listings)} listings, +{new_count} Tel Aviv new")

            except Exception as e:
                print(f"  [{request_count}/{total_requests}] ERROR: {e}")

            time.sleep(0.3)

    print()
    print("=" * 50)
    print(f"Total listings scraped: {total_scraped}")
    print(f"Tel Aviv listings (filtered): {len(all_listings)}")
    print("=" * 50)

    if all_listings:
        # Export to Parquet using new structure: {city_name}/{YYYYMMDD}_{city_name}.parquet
        listings_list = list(all_listings.values())
        output_path = exporter.export(
            listings_list,
            output_path="",  # Ignored when using structured mode
            city_name=CITY,
            base_output_path=config.output_path,
            date=datetime.now(),
        )
        print(f"\nExported to: {output_path}")

        # Show sample
        print("\nSample listings:")
        for listing in listings_list[:3]:
            price_str = f"{listing.price:,} ILS" if listing.price else "Price N/A"
            print(f"  - {listing.city}: {listing.address}, "
                  f"{listing.rooms} rooms, {price_str}")
    else:
        print("\nNo Tel Aviv listings found!")

    client.close()
    print("\nDone!")


if __name__ == "__main__":
    main()

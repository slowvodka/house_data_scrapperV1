"""Scrape Tel Aviv real estate listings using the map API."""
import time
from datetime import datetime
from pathlib import Path
from src.api_client import Yad2ApiClient
from src.config import ScraperConfig
from src.parser import ListingParser
from src.exporter import ParquetExporter

# Scraping parameters
CITY = "תל אביב"
GRID_SIZE = 20  # Very fine grid - brute force
ZOOM = 16  # Higher zoom for smaller areas

# Original Tel Aviv bbox from OSM
ORIGINAL_BBOX = (32.0303, 34.7422, 32.1463, 34.8513)


def main():
    print("=" * 50)
    print(f"Scraping: {CITY}")
    print("=" * 50)

    config = ScraperConfig()
    client = Yad2ApiClient(config)
    parser = ListingParser()
    exporter = ParquetExporter()

    # Use original Tel Aviv bbox - brute force with fine grid
    lat_min, lon_min, lat_max, lon_max = ORIGINAL_BBOX
    print(f"Bbox: {ORIGINAL_BBOX}")
    print(f"Grid: {GRID_SIZE}x{GRID_SIZE}, Zoom: {ZOOM}")

    # Initialize session
    print("\nInitializing session...")
    client.init_session()

    # Calculate grid steps
    lat_step = (lat_max - lat_min) / GRID_SIZE
    lon_step = (lon_max - lon_min) / GRID_SIZE

    all_listings = {}  # url -> Listing (for deduplication)
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

                # Deduplicate by URL
                new_count = 0
                for listing in listings:
                    if listing.url not in all_listings:
                        all_listings[listing.url] = listing
                        new_count += 1

                print(f"  [{request_count}/{total_requests}] "
                      f"{len(listings)} listings, +{new_count} new")

            except Exception as e:
                print(f"  [{request_count}/{total_requests}] ERROR: {e}")

            time.sleep(0.3)

    print()
    print("=" * 50)
    print(f"Total unique listings: {len(all_listings)}")
    print("=" * 50)

    if all_listings:
        # Export to Parquet
        listings_list = list(all_listings.values())
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"tel_aviv_{timestamp}.parquet"
        output_path = Path(config.output_path) / filename

        exporter.export(listings_list, output_path)
        print(f"\nExported to: {output_path}")

        # Show sample
        print("\nSample listings:")
        for listing in listings_list[:3]:
            price_str = f"{listing.price:,} ILS" if listing.price else "Price N/A"
            print(f"  - {listing.city}: {listing.address}, "
                  f"{listing.rooms} rooms, {price_str}")

    client.close()
    print("\nDone!")


if __name__ == "__main__":
    main()

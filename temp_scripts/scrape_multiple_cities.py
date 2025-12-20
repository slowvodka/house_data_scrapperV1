"""Scrape multiple cities sequentially using neighborhood-based approach.

NOTE: Run from project root: python temp_scripts/scrape_multiple_cities.py
"""
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Import from temp_scripts directory
sys.path.insert(0, str(Path(__file__).parent))
from scrape_city_by_neighborhoods import scrape_city_by_neighborhoods

# Cities to scrape
CITIES = [
    "רמת גן",
    "תל אביב יפו",
    "גבעתיים",
]


def main():
    """Scrape all configured cities."""
    print("=" * 70)
    print("MULTI-CITY SCRAPER")
    print("=" * 70)
    print(f"Scraping {len(CITIES)} cities: {', '.join(CITIES)}")
    print("=" * 70)
    
    results = {}
    
    for idx, city_name in enumerate(CITIES, 1):
        print(f"\n{'=' * 70}")
        print(f"CITY {idx}/{len(CITIES)}: {city_name}")
        print(f"{'=' * 70}\n")
        
        output_path = scrape_city_by_neighborhoods(city_name)
        
        if output_path:
            results[city_name] = output_path
            print(f"\nSUCCESS: {city_name}")
            print(f"   File: {output_path}")
        else:
            results[city_name] = None
            print(f"\nFAILED: {city_name}")
        
        # Delay between cities (except after last)
        if idx < len(CITIES):
            print("\n" + "-" * 70)
            print("Waiting before next city...")
            print("-" * 70 + "\n")
            import time
            time.sleep(2)
    
    # Summary
    print("\n" + "=" * 70)
    print("SCRAPING SUMMARY")
    print("=" * 70)
    for city_name, output_path in results.items():
        status = "SUCCESS" if output_path else "FAILED"
        print(f"{status}: {city_name}")
        if output_path:
            print(f"  -> {output_path}")
    print("=" * 70)


if __name__ == "__main__":
    main()


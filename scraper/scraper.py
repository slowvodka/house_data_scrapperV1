"""
Scraper module for the Yad2 Real Estate Scraper.

Orchestrates the scraping workflow: fetches listings from API,
parses responses, handles pagination, and exports to Parquet.
"""

import time
from datetime import datetime
from pathlib import Path
from typing import List, Optional

from scraper.api_client import Yad2ApiClient
from scraper.config import ScraperConfig
from scraper.exporter import ParquetExporter
from scraper.models import Listing
from scraper.parser import ListingParser


class Yad2Scraper:
    """
    Main scraper class that orchestrates the data collection workflow.

    Coordinates API client, parser, and exporter to:
    1. Fetch listings for each configured city
    2. Handle pagination automatically
    3. Parse JSON responses into Listing objects
    4. Export collected data to Parquet files

    Attributes:
        config: ScraperConfig with cities and settings.
        api_client: HTTP client for Yad2 API.
        parser: JSON to Listing parser.
        exporter: Parquet file exporter.
    """

    def __init__(
        self,
        config: ScraperConfig,
        api_client: Yad2ApiClient,
        parser: ListingParser,
        exporter: ParquetExporter,
    ):
        """
        Initialize the scraper with dependencies.

        Args:
            config: ScraperConfig with cities and settings.
            api_client: HTTP client for Yad2 API.
            parser: JSON to Listing parser.
            exporter: Parquet file exporter.
        """
        self.config = config
        self.api_client = api_client
        self.parser = parser
        self.exporter = exporter

    @classmethod
    def create(cls, config: ScraperConfig) -> "Yad2Scraper":
        """
        Factory method to create a scraper with default components.

        Convenience method that creates all required components
        based on the provided configuration.

        Args:
            config: ScraperConfig with cities and settings.

        Returns:
            Fully configured Yad2Scraper instance.
        """
        api_client = Yad2ApiClient(config)
        # Initialize session to get cookies before API calls
        api_client.init_session()
        
        return cls(
            config=config,
            api_client=api_client,
            parser=ListingParser(),
            exporter=ParquetExporter(),
        )

    def scrape_city(self, city_name: str) -> List[Listing]:
        """
        Scrape all listings for a single city.

        Fetches all property types (apartments, penthouses, houses, etc.)
        and deduplicates by listing token.

        Args:
            city_name: City name in Hebrew (e.g., "באר שבע").

        Returns:
            List of unique Listing objects for the city.

        Raises:
            ValueError: If city name is not recognized.
        """
        city_id = self.config.get_city_id(city_name)
        all_listings: List[Listing] = []
        seen_urls: set = set()  # Track unique listings by URL
        
        # Fetch all property types
        for property_type in Yad2ApiClient.PROPERTY_TYPES:
            try:
                response = self.api_client.fetch_listings(city_id, property_type)
                listings = self.parser.parse_response(response, city_name)
                
                # Add only unique listings (by URL/token)
                for listing in listings:
                    if listing.url not in seen_urls:
                        seen_urls.add(listing.url)
                        all_listings.append(listing)
                
                # Small delay between property type requests
                time.sleep(0.5)
                
            except Exception as e:
                print(f"  Error fetching type {property_type}: {e}")
                continue
        
        return all_listings

    def scrape_all_cities(self) -> List[Listing]:
        """
        Scrape listings for all configured cities.

        Continues scraping even if individual cities fail,
        logging errors but not stopping the overall process.

        Returns:
            Combined list of Listing objects from all cities.
        """
        all_listings: List[Listing] = []

        for city_name in self.config.cities:
            try:
                print(f"Scraping {city_name}...")
                city_listings = self.scrape_city(city_name)
                all_listings.extend(city_listings)
                print(f"  Found {len(city_listings)} listings")

                # Delay between cities
                if city_name != self.config.cities[-1]:
                    delay = self.config.get_random_delay()
                    time.sleep(delay)

            except Exception as e:
                print(f"  Error scraping {city_name}: {e}")
                # Continue with next city
                continue

        return all_listings

    def run(self, output_filename: Optional[str] = None) -> Path:
        """
        Execute the full scraping workflow.

        1. Scrapes all configured cities
        2. Exports results to Parquet file
        3. Returns the output file path

        Args:
            output_filename: Optional custom filename for output.
                If not provided, generates timestamped filename.

        Returns:
            Path to the generated Parquet file.
        """
        # Scrape all cities
        print(f"Starting scrape for {len(self.config.cities)} cities...")
        listings = self.scrape_all_cities()
        print(f"Total listings collected: {len(listings)}")

        # Generate output path
        if output_filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_filename = f"yad2_listings_{timestamp}.parquet"

        output_path = Path(self.config.output_path) / output_filename

        # Export to Parquet
        self.exporter.export(listings, output_path)

        return output_path


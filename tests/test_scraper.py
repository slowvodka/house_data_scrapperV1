"""
Unit tests for the Scraper Module.

TDD Phase: RED - Writing tests before implementation.
Tests the main orchestration logic for scraping Yad2 listings.
"""

import pytest
import responses
from pathlib import Path
from datetime import datetime
from unittest.mock import Mock, patch, MagicMock

from src.scraper import Yad2Scraper
from src.config import ScraperConfig
from src.api_client import Yad2ApiClient
from src.parser import ListingParser
from src.exporter import ParquetExporter
from src.models import Listing


# Sample API response for testing
def make_api_response(num_listings: int) -> dict:
    """Create a mock API response with specified number of listings."""
    listings = []
    for i in range(num_listings):
        listings.append({
            "token": f"token_{i}",
            "price": 1000000 + (i * 100000),
            "additionalDetails": {
                "roomsCount": 3,
                "squareMeter": 80 + i,
            },
            "address": {
                "city": {"text": "באר שבע"},
                "street": {"text": "רחוב הבדיקה"},
                "house": {"floor": i + 1},
            },
            "inProperty": {},
            "metaData": {"description": f"Test listing {i}"},
        })
    return {"data": [listings]}


class TestScraperInitialization:
    """Test Scraper initialization and setup."""

    def test_scraper_accepts_config_and_components(self):
        """Scraper should accept config and component dependencies."""
        config = ScraperConfig(cities=["באר שבע"])
        api_client = Mock(spec=Yad2ApiClient)
        parser = Mock(spec=ListingParser)
        exporter = Mock(spec=ParquetExporter)

        scraper = Yad2Scraper(
            config=config,
            api_client=api_client,
            parser=parser,
            exporter=exporter,
        )

        assert scraper.config == config
        assert scraper.api_client == api_client
        assert scraper.parser == parser
        assert scraper.exporter == exporter

    def test_scraper_create_factory_method(self):
        """Factory method should create scraper with all components."""
        config = ScraperConfig(cities=["באר שבע"])
        
        scraper = Yad2Scraper.create(config)

        assert scraper.config == config
        assert isinstance(scraper.api_client, Yad2ApiClient)
        assert isinstance(scraper.parser, ListingParser)
        assert isinstance(scraper.exporter, ParquetExporter)


class TestScrapeSingleCity:
    """Test scraping a single city."""

    def test_scrape_city_single_page(self):
        """Should fetch and parse a single page of listings."""
        config = ScraperConfig(cities=["באר שבע"], results_per_page=40)
        
        # Mock API client to return less than full page (end of results)
        api_client = Mock(spec=Yad2ApiClient)
        api_client.fetch_listings.return_value = make_api_response(10)
        
        # Real parser to test integration
        parser = ListingParser()
        exporter = Mock(spec=ParquetExporter)

        scraper = Yad2Scraper(
            config=config,
            api_client=api_client,
            parser=parser,
            exporter=exporter,
        )

        listings = scraper.scrape_city("באר שבע")

        assert len(listings) == 10
        assert all(isinstance(l, Listing) for l in listings)
        # Should only call API once (10 < 40, so no more pages)
        api_client.fetch_listings.assert_called_once()

    def test_scrape_city_multiple_pages(self):
        """Should paginate and fetch all pages."""
        config = ScraperConfig(cities=["באר שבע"], results_per_page=10)
        
        api_client = Mock(spec=Yad2ApiClient)
        # First call: full page (10 items) → more pages
        # Second call: partial page (5 items) → done
        api_client.fetch_listings.side_effect = [
            make_api_response(10),
            make_api_response(5),
        ]
        
        parser = ListingParser()
        exporter = Mock(spec=ParquetExporter)

        scraper = Yad2Scraper(
            config=config,
            api_client=api_client,
            parser=parser,
            exporter=exporter,
        )

        # Patch sleep to avoid delays in tests
        with patch("time.sleep"):
            listings = scraper.scrape_city("באר שבע")

        assert len(listings) == 15  # 10 + 5
        assert api_client.fetch_listings.call_count == 2

    def test_scrape_city_empty_results(self):
        """Should handle city with no listings."""
        config = ScraperConfig(cities=["באר שבע"], results_per_page=40)
        
        api_client = Mock(spec=Yad2ApiClient)
        api_client.fetch_listings.return_value = {"data": [[]]}
        
        parser = ListingParser()
        exporter = Mock(spec=ParquetExporter)

        scraper = Yad2Scraper(
            config=config,
            api_client=api_client,
            parser=parser,
            exporter=exporter,
        )

        listings = scraper.scrape_city("באר שבע")

        assert listings == []

    def test_scrape_city_uses_city_id(self):
        """Should convert city name to ID for API call."""
        config = ScraperConfig(cities=["באר שבע"], results_per_page=40)
        
        api_client = Mock(spec=Yad2ApiClient)
        api_client.fetch_listings.return_value = make_api_response(5)
        
        parser = ListingParser()
        exporter = Mock(spec=ParquetExporter)

        scraper = Yad2Scraper(
            config=config,
            api_client=api_client,
            parser=parser,
            exporter=exporter,
        )

        scraper.scrape_city("באר שבע")

        # Beer Sheva ID is 9000
        api_client.fetch_listings.assert_called_with(9000, 1)


class TestScrapeMultipleCities:
    """Test scraping multiple cities."""

    def test_scrape_all_cities(self):
        """Should scrape all configured cities."""
        config = ScraperConfig(
            cities=["באר שבע", "תל אביב"],
            results_per_page=40,
        )
        
        api_client = Mock(spec=Yad2ApiClient)
        # Each city returns 5 listings
        api_client.fetch_listings.return_value = make_api_response(5)
        
        parser = ListingParser()
        exporter = Mock(spec=ParquetExporter)

        scraper = Yad2Scraper(
            config=config,
            api_client=api_client,
            parser=parser,
            exporter=exporter,
        )

        with patch("time.sleep"):
            listings = scraper.scrape_all_cities()

        assert len(listings) == 10  # 5 per city × 2 cities
        # API called twice (once per city)
        assert api_client.fetch_listings.call_count == 2

    def test_scrape_all_cities_continues_on_error(self):
        """Should continue scraping if one city fails."""
        config = ScraperConfig(
            cities=["באר שבע", "תל אביב"],
            results_per_page=40,
        )
        
        api_client = Mock(spec=Yad2ApiClient)
        # First city fails, second succeeds
        api_client.fetch_listings.side_effect = [
            Exception("API Error"),
            make_api_response(5),
        ]
        
        parser = ListingParser()
        exporter = Mock(spec=ParquetExporter)

        scraper = Yad2Scraper(
            config=config,
            api_client=api_client,
            parser=parser,
            exporter=exporter,
        )

        with patch("time.sleep"):
            listings = scraper.scrape_all_cities()

        # Should get 5 listings from the successful city
        assert len(listings) == 5
        # Both cities were attempted
        assert api_client.fetch_listings.call_count == 2


class TestScraperRun:
    """Test the full run workflow."""

    def test_run_exports_to_parquet(self, tmp_path):
        """Run should scrape all cities and export to Parquet."""
        config = ScraperConfig(
            cities=["באר שבע"],
            results_per_page=40,
            output_path=str(tmp_path),
        )
        
        api_client = Mock(spec=Yad2ApiClient)
        api_client.fetch_listings.return_value = make_api_response(3)
        
        parser = ListingParser()
        exporter = Mock(spec=ParquetExporter)

        scraper = Yad2Scraper(
            config=config,
            api_client=api_client,
            parser=parser,
            exporter=exporter,
        )

        with patch("time.sleep"):
            result_path = scraper.run()

        # Exporter should be called with listings
        exporter.export.assert_called_once()
        call_args = exporter.export.call_args
        exported_listings = call_args[0][0]
        assert len(exported_listings) == 3

    def test_run_generates_timestamped_filename(self, tmp_path):
        """Run should generate a timestamped output filename."""
        config = ScraperConfig(
            cities=["באר שבע"],
            results_per_page=40,
            output_path=str(tmp_path),
        )
        
        api_client = Mock(spec=Yad2ApiClient)
        api_client.fetch_listings.return_value = make_api_response(1)
        
        parser = ListingParser()
        exporter = Mock(spec=ParquetExporter)

        scraper = Yad2Scraper(
            config=config,
            api_client=api_client,
            parser=parser,
            exporter=exporter,
        )

        with patch("time.sleep"):
            result_path = scraper.run()

        # Check the export was called with a path
        exporter.export.assert_called_once()
        call_args = exporter.export.call_args
        output_path = call_args[0][1]
        
        # Path should be in the output directory
        assert str(tmp_path) in str(output_path)
        # Should have .parquet extension
        assert str(output_path).endswith(".parquet")

    def test_run_with_custom_filename(self, tmp_path):
        """Run should accept a custom output filename."""
        config = ScraperConfig(
            cities=["באר שבע"],
            results_per_page=40,
            output_path=str(tmp_path),
        )
        
        api_client = Mock(spec=Yad2ApiClient)
        api_client.fetch_listings.return_value = make_api_response(1)
        
        parser = ListingParser()
        exporter = Mock(spec=ParquetExporter)

        scraper = Yad2Scraper(
            config=config,
            api_client=api_client,
            parser=parser,
            exporter=exporter,
        )

        with patch("time.sleep"):
            result_path = scraper.run(output_filename="my_export.parquet")

        exporter.export.assert_called_once()
        call_args = exporter.export.call_args
        output_path = call_args[0][1]
        assert "my_export.parquet" in str(output_path)


class TestScraperRateLimiting:
    """Test rate limiting behavior."""

    def test_scrape_city_applies_delay_between_pages(self):
        """Should add delay between page fetches."""
        config = ScraperConfig(
            cities=["באר שבע"],
            results_per_page=10,
            min_delay=1.0,
            max_delay=2.0,
        )
        
        api_client = Mock(spec=Yad2ApiClient)
        api_client.fetch_listings.side_effect = [
            make_api_response(10),  # Full page → more
            make_api_response(5),   # Partial → done
        ]
        
        parser = ListingParser()
        exporter = Mock(spec=ParquetExporter)

        scraper = Yad2Scraper(
            config=config,
            api_client=api_client,
            parser=parser,
            exporter=exporter,
        )

        with patch("time.sleep") as mock_sleep:
            scraper.scrape_city("באר שבע")
            # Should sleep once between pages
            assert mock_sleep.call_count >= 1



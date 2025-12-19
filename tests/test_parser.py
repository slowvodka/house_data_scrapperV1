"""
Unit tests for the Parser Module.

TDD Phase: RED - Writing tests before implementation.
Parses Yad2 API JSON responses into Listing dataclass objects.
"""

import pytest
from datetime import datetime

from scraper.parser import ListingParser
from scraper.models import Listing


# Sample API response data based on discovered API structure
SAMPLE_LISTING_JSON = {
    "token": "7a7i4007",
    "orderId": 55198144,
    "adNumber": 52846718,
    "price": 1820000,
    "additionalDetails": {
        "balconiesCount": 1,
        "entranceDate": "2025-06-16T00:00:00",
        "squareMeter": 150,
        "roomsCount": 4,
        "property": {
            "id": 1,
            "text": "דירה",
            "textEng": "apartment"
        },
        "parkingSpacesCount": 1,
        "propertyCondition": {
            "id": 6,
            "text": "חדש (גרו בנכס)"
        },
        "squareMeterBuild": 130,
        "buildingTopFloor": 16,
    },
    "inProperty": {
        "includeBalcony": True,
        "includeParking": True,
        "includeSecurityRoom": False,
        "includeElevator": True,
        "includeWarehouse": True,
    },
    "address": {
        "city": {"id": 9000, "text": "באר שבע"},
        "neighborhood": {"id": 1344, "text": "שכונה ג'"},
        "street": {"id": "0504", "text": "גולומב"},
        "house": {"floor": 2, "number": 17},
    },
    "metaData": {
        "description": "דירת 4 חדרים משודרגת במגדלי דוד",
    },
}


class TestParserInitialization:
    """Test parser initialization."""

    def test_parser_creates_instance(self):
        """Parser should be instantiable."""
        parser = ListingParser()
        assert parser is not None


class TestParserSingleListing:
    """Test parsing a single listing from JSON."""

    def test_parse_listing_returns_listing_object(self):
        """parse_listing should return a Listing dataclass."""
        parser = ListingParser()
        listing = parser.parse_listing(SAMPLE_LISTING_JSON, city="באר שבע")
        assert isinstance(listing, Listing)

    def test_parse_listing_extracts_city(self):
        """Parser should extract city name."""
        parser = ListingParser()
        listing = parser.parse_listing(SAMPLE_LISTING_JSON, city="באר שבע")
        assert listing.city == "באר שבע"

    def test_parse_listing_extracts_price(self):
        """Parser should extract price."""
        parser = ListingParser()
        listing = parser.parse_listing(SAMPLE_LISTING_JSON, city="באר שבע")
        assert listing.price == 1820000

    def test_parse_listing_extracts_rooms(self):
        """Parser should extract room count."""
        parser = ListingParser()
        listing = parser.parse_listing(SAMPLE_LISTING_JSON, city="באר שבע")
        assert listing.rooms == 4

    def test_parse_listing_extracts_sqm(self):
        """Parser should extract square meters."""
        parser = ListingParser()
        listing = parser.parse_listing(SAMPLE_LISTING_JSON, city="באר שבע")
        assert listing.sqm == 150

    def test_parse_listing_extracts_floor(self):
        """Parser should extract floor number."""
        parser = ListingParser()
        listing = parser.parse_listing(SAMPLE_LISTING_JSON, city="באר שבע")
        assert listing.floor == 2

    def test_parse_listing_extracts_neighborhood(self):
        """Parser should extract neighborhood name."""
        parser = ListingParser()
        listing = parser.parse_listing(SAMPLE_LISTING_JSON, city="באר שבע")
        assert listing.neighborhood == "שכונה ג'"

    def test_parse_listing_extracts_asset_type(self):
        """Parser should extract asset type."""
        parser = ListingParser()
        listing = parser.parse_listing(SAMPLE_LISTING_JSON, city="באר שבע")
        assert listing.asset_type == "דירה"

    def test_parse_listing_extracts_description(self):
        """Parser should extract description."""
        parser = ListingParser()
        listing = parser.parse_listing(SAMPLE_LISTING_JSON, city="באר שבע")
        assert "משודרגת" in listing.description

    def test_parse_listing_extracts_url(self):
        """Parser should generate URL from token."""
        parser = ListingParser()
        listing = parser.parse_listing(SAMPLE_LISTING_JSON, city="באר שבע")
        assert "7a7i4007" in listing.url

    def test_parse_listing_has_scraped_at(self):
        """Parser should set scraped_at timestamp."""
        parser = ListingParser()
        listing = parser.parse_listing(SAMPLE_LISTING_JSON, city="באר שבע")
        assert isinstance(listing.scraped_at, datetime)


class TestParserPropertyFeatures:
    """Test parsing property feature fields."""

    def test_parse_listing_extracts_parking(self):
        """Parser should extract parking count."""
        parser = ListingParser()
        listing = parser.parse_listing(SAMPLE_LISTING_JSON, city="באר שבע")
        assert listing.parking == 1

    def test_parse_listing_extracts_balconies(self):
        """Parser should extract balcony count."""
        parser = ListingParser()
        listing = parser.parse_listing(SAMPLE_LISTING_JSON, city="באר שבע")
        assert listing.balconies == 1

    def test_parse_listing_extracts_elevator(self):
        """Parser should extract elevator presence."""
        parser = ListingParser()
        listing = parser.parse_listing(SAMPLE_LISTING_JSON, city="באר שבע")
        assert listing.elevator is True

    def test_parse_listing_extracts_mamad(self):
        """Parser should extract mamad (security room) presence."""
        parser = ListingParser()
        listing = parser.parse_listing(SAMPLE_LISTING_JSON, city="באר שבע")
        assert listing.mamad is False

    def test_parse_listing_extracts_storage_unit(self):
        """Parser should extract storage unit presence."""
        parser = ListingParser()
        listing = parser.parse_listing(SAMPLE_LISTING_JSON, city="באר שבע")
        assert listing.storage_unit is True

    def test_parse_listing_extracts_total_floors(self):
        """Parser should extract total floors in building."""
        parser = ListingParser()
        listing = parser.parse_listing(SAMPLE_LISTING_JSON, city="באר שבע")
        assert listing.total_floors == 16

    def test_parse_listing_extracts_condition(self):
        """Parser should extract property condition."""
        parser = ListingParser()
        listing = parser.parse_listing(SAMPLE_LISTING_JSON, city="באר שבע")
        assert listing.condition == "חדש (גרו בנכס)"

    def test_parse_listing_extracts_entrance_date(self):
        """Parser should extract entrance date."""
        parser = ListingParser()
        listing = parser.parse_listing(SAMPLE_LISTING_JSON, city="באר שבע")
        assert listing.entrance_date == "2025-06-16"


class TestParserAddress:
    """Test parsing address fields."""

    def test_parse_listing_extracts_street_address(self):
        """Parser should extract street address."""
        parser = ListingParser()
        listing = parser.parse_listing(SAMPLE_LISTING_JSON, city="באר שבע")
        assert "גולומב" in listing.address
        assert "17" in listing.address


class TestParserMissingFields:
    """Test handling of missing or null fields."""

    def test_parse_listing_handles_missing_price(self):
        """Parser should handle missing price."""
        data = {**SAMPLE_LISTING_JSON, "price": 0}
        parser = ListingParser()
        listing = parser.parse_listing(data, city="באר שבע")
        assert listing.price is None  # 0 means no price

    def test_parse_listing_handles_missing_rooms(self):
        """Parser should handle missing room count."""
        data = {**SAMPLE_LISTING_JSON}
        data["additionalDetails"] = {}
        parser = ListingParser()
        listing = parser.parse_listing(data, city="באר שבע")
        assert listing.rooms is None

    def test_parse_listing_handles_missing_address(self):
        """Parser should handle missing address."""
        data = {**SAMPLE_LISTING_JSON}
        data["address"] = {}
        parser = ListingParser()
        listing = parser.parse_listing(data, city="באר שבע")
        assert listing.address is None or listing.address == ""

    def test_parse_listing_handles_missing_elevator(self):
        """Parser should handle missing elevator info."""
        data = {**SAMPLE_LISTING_JSON}
        data["inProperty"] = {}
        parser = ListingParser()
        listing = parser.parse_listing(data, city="באר שבע")
        assert listing.elevator is None


class TestParserApiResponse:
    """Test parsing full API response."""

    def test_parse_response_extracts_all_listings(self):
        """parse_response should extract all listings from API response."""
        api_response = {
            "data": [[
                SAMPLE_LISTING_JSON,
                {**SAMPLE_LISTING_JSON, "token": "xyz789", "price": 2000000}
            ]]
        }
        parser = ListingParser()
        listings = parser.parse_response(api_response, city="באר שבע")
        assert len(listings) == 2

    def test_parse_response_handles_empty_data(self):
        """parse_response should handle empty data array."""
        api_response = {"data": [[]]}
        parser = ListingParser()
        listings = parser.parse_response(api_response, city="באר שבע")
        assert listings == []

    def test_parse_response_handles_missing_data_key(self):
        """parse_response should handle missing data key."""
        api_response = {}
        parser = ListingParser()
        listings = parser.parse_response(api_response, city="באר שבע")
        assert listings == []


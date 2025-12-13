"""
Parser module for the Yad2 Real Estate Scraper.

Converts Yad2 API JSON responses into Listing dataclass objects.
Handles data extraction, type conversion, and missing field handling.
"""

from datetime import datetime
from typing import Any, Dict, List, Optional

from src.models import Listing


class ListingParser:
    """
    Parses Yad2 API JSON responses into Listing objects.

    Handles the nested JSON structure returned by the Yad2 recommendations API
    and maps fields to our Listing dataclass with proper type conversions.
    """

    # Base URL for constructing listing URLs from token
    LISTING_URL_TEMPLATE = "https://www.yad2.co.il/realestate/item/{token}"

    def parse_listing(self, data: Dict[str, Any], city: str) -> Listing:
        """
        Parse a single listing from JSON to Listing dataclass.

        Args:
            data: Single listing JSON object from API response.
            city: City name (used as fallback if not in data).

        Returns:
            Listing dataclass populated with extracted data.
        """
        # Extract nested dictionaries safely
        additional = data.get("additionalDetails", {})
        in_property = data.get("inProperty", {})
        address_data = data.get("address", {})
        metadata = data.get("metaData", {})
        house = address_data.get("house", {})

        # Build URL from token
        token = data.get("token", "unknown")
        url = self.LISTING_URL_TEMPLATE.format(token=token)

        # Extract city from response or use provided city
        city_obj = address_data.get("city", {})
        extracted_city = city_obj.get("text") if city_obj else city

        # Build address string
        address = self._build_address(address_data)

        # Extract price (0 means no price)
        price = data.get("price")
        if price == 0:
            price = None

        # Extract entrance date as string
        entrance_date = self._parse_entrance_date(additional.get("entranceDate"))

        return Listing(
            # Required fields
            city=extracted_city or city,
            url=url,
            scraped_at=datetime.now(),
            # Core property details
            price=price,
            rooms=additional.get("roomsCount"),
            floor=house.get("floor"),
            sqm=additional.get("squareMeter"),
            address=address,
            neighborhood=self._safe_get_text(address_data, "neighborhood"),
            asset_type=self._safe_get_text(additional, "property"),
            description=metadata.get("description"),
            # Building information
            total_floors=additional.get("buildingTopFloor"),
            year_built=additional.get("yearBuilt"),  # May not always be present
            elevator=in_property.get("includeElevator"),
            # Property features
            parking=additional.get("parkingSpacesCount"),
            balconies=additional.get("balconiesCount"),
            mamad=in_property.get("includeSecurityRoom"),
            storage_unit=in_property.get("includeWarehouse"),
            condition=self._safe_get_text(additional, "propertyCondition"),
            # Availability
            entrance_date=entrance_date,
        )

    def parse_response(
        self, api_response: Dict[str, Any], city: str
    ) -> List[Listing]:
        """
        Parse full API response containing multiple listings.

        Args:
            api_response: Complete API response JSON with nested data structure.
            city: City name for listings.

        Returns:
            List of Listing objects extracted from response.
        """
        listings = []

        # API returns data as nested array: {"data": [[listing1, listing2, ...]]}
        data_outer = api_response.get("data", [])
        if not data_outer:
            return listings

        # First element contains the actual listings array
        if isinstance(data_outer, list) and len(data_outer) > 0:
            listings_data = data_outer[0]
            if isinstance(listings_data, list):
                for item in listings_data:
                    if isinstance(item, dict):
                        listing = self.parse_listing(item, city)
                        listings.append(listing)

        return listings

    def _build_address(self, address_data: Dict[str, Any]) -> Optional[str]:
        """
        Build address string from address components.

        Args:
            address_data: Address dictionary from API.

        Returns:
            Formatted address string or None if no data.
        """
        street = self._safe_get_text(address_data, "street")
        house = address_data.get("house", {})
        house_number = house.get("number")

        if not street:
            return None

        if house_number:
            return f"{street} {house_number}"
        return street

    def _safe_get_text(
        self, parent: Dict[str, Any], key: str
    ) -> Optional[str]:
        """
        Safely extract 'text' field from nested object.

        Args:
            parent: Parent dictionary.
            key: Key to nested object containing 'text'.

        Returns:
            Text value or None if not found.
        """
        obj = parent.get(key)
        if isinstance(obj, dict):
            return obj.get("text")
        return None

    def _parse_entrance_date(self, date_str: Optional[str]) -> Optional[str]:
        """
        Parse entrance date string to date-only format.

        Args:
            date_str: ISO datetime string from API (e.g., "2025-06-16T00:00:00").

        Returns:
            Date string in YYYY-MM-DD format or None.
        """
        if not date_str:
            return None

        try:
            # Parse ISO format and extract date part
            dt = datetime.fromisoformat(date_str.replace("Z", "+00:00"))
            return dt.strftime("%Y-%m-%d")
        except (ValueError, AttributeError):
            return None


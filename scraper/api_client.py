"""
API Client module for the Yad2 Real Estate Scraper.

Provides an HTTP client for interacting with the Yad2 recommendations API.
Handles request building, retry logic, and error handling.
"""

import time
from typing import Any, Dict, Optional
from urllib.parse import urlencode

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from scraper.config import ScraperConfig


# Map API endpoint for full listing coverage
MAP_API_URL = "https://gw.yad2.co.il/realestate-feed/forsale/map"

# Bounding box for all of Israel (lat_south,lon_west,lat_north,lon_east)
ISRAEL_BBOX = "29.5,34.2,33.3,35.9"

# Browser-like headers to avoid detection
DEFAULT_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    ),
    "Accept": "application/json, text/plain, */*",
    "Accept-Language": "he-IL,he;q=0.9,en-US;q=0.8,en;q=0.7",
    "Accept-Encoding": "gzip, deflate, br",
    "Origin": "https://www.yad2.co.il",
    "Referer": "https://www.yad2.co.il/",
    "Connection": "keep-alive",
}


class Yad2ApiClient:
    """
    HTTP client for the Yad2 recommendations API.

    Handles API requests with retry logic, rate limiting, and
    browser-like behavior to avoid detection.

    Attributes:
        config: ScraperConfig instance with API settings.
        session: requests.Session for connection pooling.
    """

    def __init__(self, config: ScraperConfig):
        """
        Initialize the API client.

        Args:
            config: ScraperConfig instance with API settings.
        """
        self.config = config
        self.session = self._create_session()

    def _create_session(self) -> requests.Session:
        """
        Create a requests session with retry strategy.

        Returns:
            Configured requests.Session object.
        """
        session = requests.Session()
        session.headers.update(DEFAULT_HEADERS)

        # Configure retry strategy for transient failures
        retry_strategy = Retry(
            total=self.config.max_retries,
            backoff_factor=self.config.retry_delay,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["GET"],
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        session.mount("https://", adapter)
        session.mount("http://", adapter)

        return session

    def init_session(self) -> None:
        """
        Initialize the session by visiting the main Yad2 website.

        This is required to obtain session cookies/tokens before
        making API calls. Call this once before fetch_listings().
        """
        # Visit the main real estate page to get cookies
        init_url = "https://www.yad2.co.il/realestate/forsale"
        try:
            response = self.session.get(
                init_url,
                timeout=self.config.request_timeout,
            )
            response.raise_for_status()
            print(f"Session initialized (got {len(self.session.cookies)} cookies)")
        except requests.exceptions.RequestException as e:
            print(f"Session init warning: {e}")

    # Valid property type IDs (subCategoriesIds)
    # 1=Apartment, 2=Garden Apt, 4=Penthouse, 5=Duplex, 6=Roof Apt, 7=House/Cottage
    PROPERTY_TYPES = [1, 2, 4, 5, 6, 7]

    def build_url(self, city_id: int, property_type: int = 1) -> str:
        """
        Build the API URL with query parameters.

        Args:
            city_id: Yad2 city ID to search.
            property_type: Property type ID (subCategoriesIds).

        Returns:
            Complete URL string with query parameters.
        """
        params = {
            "type": "home",
            "categoryId": 2,  # Real estate for sale
            "subCategoriesIds": property_type,
            "cityValues": city_id,
            "count": self.config.results_per_page,
            # Note: This API doesn't support pagination
        }

        query_string = urlencode(params)
        return f"{self.config.api_base_url}?{query_string}"

    def fetch_listings(self, city_id: int, property_type: int = 1) -> Dict[str, Any]:
        """
        Fetch listings from the Yad2 API for a city and property type.

        Note: This recommendations API returns ~60 items per property type.
        Call with different property_type values to get more results.

        Args:
            city_id: Yad2 city ID to search.
            property_type: Property type ID (1-7). See PROPERTY_TYPES.

        Returns:
            Parsed JSON response from the API.

        Raises:
            requests.exceptions.RequestException: On HTTP errors.
        """
        url = self.build_url(city_id, property_type)

        try:
            response = self.session.get(
                url,
                timeout=self.config.request_timeout,
            )
            response.raise_for_status()
            return response.json()

        except requests.exceptions.RequestException:
            # Let the retry strategy handle transient errors
            # Re-raise for the caller to handle
            raise

    def fetch_listings_for_city(self, city_name: str) -> Dict[str, Any]:
        """
        Fetch listings using city name instead of ID.

        Convenience method that converts city name to ID.

        Args:
            city_name: City name in Hebrew (e.g., "באר שבע").

        Returns:
            Parsed JSON response from the API.

        Raises:
            ValueError: If city name is not recognized.
            requests.exceptions.RequestException: On HTTP errors.
        """
        city_id = self.config.get_city_id(city_name)
        return self.fetch_listings(city_id)

    def build_map_url(self, bbox: str, zoom: int = 8) -> str:
        """
        Build the map API URL with bounding box parameters.

        Args:
            bbox: Bounding box as "lat_south,lon_west,lat_north,lon_east".
            zoom: Zoom level (lower = more results). Default 8.

        Returns:
            Complete URL string for the map API.
        """
        # Note: safe=',' keeps commas unencoded as the API expects
        return f"{MAP_API_URL}?bBox={bbox}&zoom={zoom}"

    def fetch_map_listings(self, bbox: str, zoom: int = 8) -> Dict[str, Any]:
        """
        Fetch all listings from the map API.

        This endpoint returns ALL listings within the bounding box,
        not limited like the recommendations API.

        Args:
            bbox: Bounding box as "lat_south,lon_west,lat_north,lon_east".
                  Use ISRAEL_BBOX constant for full country coverage.
            zoom: Zoom level (lower = more results). Default 8.

        Returns:
            Parsed JSON with data.markers array.

        Raises:
            requests.exceptions.RequestException: On HTTP errors.
        """
        url = self.build_map_url(bbox, zoom)

        try:
            response = self.session.get(
                url,
                timeout=self.config.request_timeout,
            )
            response.raise_for_status()
            return response.json()

        except requests.exceptions.RequestException:
            raise

    def close(self) -> None:
        """
        Close the HTTP session and clean up resources.

        Should be called when the client is no longer needed.
        """
        if self.session:
            self.session.close()

    def __enter__(self) -> "Yad2ApiClient":
        """Context manager entry."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        """Context manager exit - close session."""
        self.close()


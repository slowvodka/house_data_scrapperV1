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

from src.config import ScraperConfig


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

    def build_url(self, city_id: int, page: int = 1) -> str:
        """
        Build the API URL with query parameters.

        Args:
            city_id: Yad2 city ID to search.
            page: Page number for pagination (1-based).

        Returns:
            Complete URL string with query parameters.
        """
        params = {
            "type": "home",
            "categoryId": 2,  # Real estate for sale
            "subCategoriesIds": 1,  # Apartments
            "cityValues": city_id,
            "count": self.config.results_per_page,
            "page": page,
        }

        query_string = urlencode(params)
        return f"{self.config.api_base_url}?{query_string}"

    def fetch_listings(
        self, city_id: int, page: int = 1
    ) -> Dict[str, Any]:
        """
        Fetch listings from the Yad2 API.

        Args:
            city_id: Yad2 city ID to search.
            page: Page number for pagination (1-based).

        Returns:
            Parsed JSON response from the API.

        Raises:
            requests.exceptions.RequestException: On HTTP errors.
        """
        url = self.build_url(city_id, page)

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

    def fetch_listings_for_city(
        self, city_name: str, page: int = 1
    ) -> Dict[str, Any]:
        """
        Fetch listings using city name instead of ID.

        Convenience method that converts city name to ID.

        Args:
            city_name: City name in Hebrew (e.g., "באר שבע").
            page: Page number for pagination (1-based).

        Returns:
            Parsed JSON response from the API.

        Raises:
            ValueError: If city name is not recognized.
            requests.exceptions.RequestException: On HTTP errors.
        """
        city_id = self.config.get_city_id(city_name)
        return self.fetch_listings(city_id, page)

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


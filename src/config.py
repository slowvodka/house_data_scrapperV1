"""
Configuration module for the Yad2 Real Estate Scraper.

Provides a dataclass-based configuration system with sensible defaults
and validation for scraper settings.
"""

import random
from dataclasses import dataclass, field
from typing import Dict, List


# City name to Yad2 city ID mapping
# These IDs are used in the API query parameters
CITY_ID_MAP: Dict[str, int] = {
    "באר שבע": 9000,
    "תל אביב": 5000,
    "ירושלים": 3000,
    "חיפה": 4000,
    "ראשון לציון": 8300,
    "פתח תקווה": 7900,
    "אשדוד": 70,
    "נתניה": 7400,
    "חולון": 6600,
    "בני ברק": 6200,
    "רמת גן": 8600,
    "אשקלון": 2100,
    "רחובות": 8400,
    "בת ים": 6100,
    "הרצליה": 6400,
    "כפר סבא": 6900,
    "מודיעין": 1139,
    "רעננה": 8700,
    "נצרת": 7300,
}


@dataclass
class ScraperConfig:
    """
    Configuration settings for the Yad2 scraper.

    Attributes:
        cities: List of city names to scrape (Hebrew names supported).
        api_base_url: Base URL for Yad2 recommendations API.
        output_path: Directory path for output Parquet files.
        min_delay: Minimum delay between requests in seconds.
        max_delay: Maximum delay between requests in seconds.
        request_timeout: HTTP request timeout in seconds.
        max_retries: Maximum number of retry attempts for failed requests.
        retry_delay: Base delay for exponential backoff in seconds.
        results_per_page: Number of results to fetch per API call.
    """

    # Target cities to scrape
    cities: List[str] = field(default_factory=list)

    # API settings
    api_base_url: str = "https://gw.yad2.co.il/recommendations/items/realestate"

    # Output settings
    output_path: str = "data/output"

    # Rate limiting (anti-scraping protection)
    min_delay: float = 2.0
    max_delay: float = 5.0

    # Timeout settings
    request_timeout: int = 30  # seconds

    # Retry settings (network resilience)
    max_retries: int = 3
    retry_delay: float = 2.0  # base delay for exponential backoff

    # Pagination
    results_per_page: int = 40  # Max results per API call

    # Legacy - keeping for backwards compatibility with tests
    page_timeout: int = 30000  # milliseconds (deprecated)
    headless: bool = True  # (deprecated - no longer using browser)

    def __post_init__(self) -> None:
        """Validate configuration values after initialization."""
        if self.min_delay < 0:
            raise ValueError("min_delay must be non-negative")
        if self.max_delay < self.min_delay:
            raise ValueError("max_delay must be >= min_delay")
        if self.page_timeout <= 0:
            raise ValueError("page_timeout must be positive")
        if self.max_retries < 0:
            raise ValueError("max_retries must be non-negative")
        if self.request_timeout <= 0:
            raise ValueError("request_timeout must be positive")
        if self.results_per_page <= 0:
            raise ValueError("results_per_page must be positive")

    def get_random_delay(self) -> float:
        """
        Generate a random delay between min_delay and max_delay.

        Used to add human-like randomness to request timing,
        helping to avoid anti-scraping detection.

        Returns:
            Random float between min_delay and max_delay (inclusive).
        """
        return random.uniform(self.min_delay, self.max_delay)

    def get_city_id(self, city_name: str) -> int:
        """
        Get the Yad2 city ID for a given city name.

        Args:
            city_name: City name in Hebrew (e.g., "באר שבע").

        Returns:
            Integer city ID used by Yad2 API.

        Raises:
            ValueError: If city name is not in the mapping.
        """
        if city_name not in CITY_ID_MAP:
            raise ValueError(
                f"Unknown city: {city_name}. "
                f"Available cities: {list(CITY_ID_MAP.keys())}"
            )
        return CITY_ID_MAP[city_name]


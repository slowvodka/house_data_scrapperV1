"""
Configuration module for the Yad2 Real Estate Scraper.

Provides a dataclass-based configuration system with sensible defaults
and validation for scraper settings.
"""

import random
from dataclasses import dataclass, field
from typing import Dict, List, Tuple


# City data mapping: name -> {id, bbox}
# - id: Yad2 city ID for recommendations API
# - bbox: Bounding box for map API (lat_min, lon_min, lat_max, lon_max)
#
# Bounding boxes obtained from OpenStreetMap Nominatim API:
#   https://nominatim.openstreetmap.org/search?q=Tel+Aviv&format=json
#   Each city's "boundingbox" field: [lat_min, lat_max, lon_min, lon_max]
#
# Note: Boxes are approximate municipal boundaries. Adjust if needed.
CITY_DATA: Dict[str, Dict] = {
    "תל אביב": {
        "id": 5000,
        "bbox": (32.0303, 34.7422, 32.1463, 34.8513),
    },
    "ירושלים": {
        "id": 3000,
        "bbox": (31.7074, 35.1415, 31.8628, 35.2629),
    },
    "חיפה": {
        "id": 4000,
        "bbox": (32.7775, 34.9514, 32.8494, 35.0761),
    },
    "באר שבע": {
        "id": 9000,
        "bbox": (31.2074, 34.7514, 31.2894, 34.8361),
    },
    "ראשון לציון": {
        "id": 8300,
        "bbox": (31.9363, 34.7422, 32.0003, 34.8213),
    },
    "פתח תקווה": {
        "id": 7900,
        "bbox": (32.0603, 34.8522, 32.1163, 34.9113),
    },
    "אשדוד": {
        "id": 70,
        "bbox": (31.7563, 34.6122, 31.8403, 34.6913),
    },
    "נתניה": {
        "id": 7400,
        "bbox": (32.2803, 34.8322, 32.3563, 34.8913),
    },
    "חולון": {
        "id": 6600,
        "bbox": (32.0003, 34.7622, 32.0303, 34.8013),
    },
    "בני ברק": {
        "id": 6200,
        "bbox": (32.0803, 34.8222, 32.1103, 34.8513),
    },
    "רמת גן": {
        "id": 8600,
        "bbox": (32.0603, 34.7922, 32.1003, 34.8413),
    },
    "גבעתיים": {
        "id": 6300,
        "bbox": (32.0603, 34.7922, 32.0803, 34.8113),
    },
    "אשקלון": {
        "id": 2100,
        "bbox": (31.6463, 34.5322, 31.6963, 34.5913),
    },
    "רחובות": {
        "id": 8400,
        "bbox": (31.8763, 34.7822, 31.9163, 34.8313),
    },
    "בת ים": {
        "id": 6100,
        "bbox": (32.0103, 34.7322, 32.0403, 34.7622),
    },
    "הרצליה": {
        "id": 6400,
        "bbox": (32.1503, 34.8022, 32.1903, 34.8513),
    },
    "כפר סבא": {
        "id": 6900,
        "bbox": (32.1603, 34.8822, 32.2003, 34.9213),
    },
    "מודיעין": {
        "id": 1139,
        "bbox": (31.8763, 34.9622, 31.9263, 35.0213),
    },
    "רעננה": {
        "id": 8700,
        "bbox": (32.1703, 34.8522, 32.2103, 34.8913),
    },
    "נצרת": {
        "id": 7300,
        "bbox": (32.6863, 35.2822, 32.7163, 35.3213),
    },
}

# Legacy mapping for backwards compatibility
CITY_ID_MAP: Dict[str, int] = {
    city: data["id"] for city, data in CITY_DATA.items()
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

    # Results count (API doesn't support pagination, so fetch all at once)
    results_per_page: int = 500  # High value to get all results

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
        if city_name not in CITY_DATA:
            raise ValueError(
                f"Unknown city: {city_name}. "
                f"Available cities: {list(CITY_DATA.keys())}"
            )
        return CITY_DATA[city_name]["id"]

    def get_city_bbox(self, city_name: str) -> Tuple[float, float, float, float]:
        """
        Get the bounding box for a city (for map API).

        Args:
            city_name: City name in Hebrew (e.g., "תל אביב").

        Returns:
            Tuple of (lat_min, lon_min, lat_max, lon_max).

        Raises:
            ValueError: If city name is not in the mapping.
        """
        if city_name not in CITY_DATA:
            raise ValueError(
                f"Unknown city: {city_name}. "
                f"Available cities: {list(CITY_DATA.keys())}"
            )
        return CITY_DATA[city_name]["bbox"]

    def get_city_bbox_string(self, city_name: str) -> str:
        """
        Get bounding box as comma-separated string for API.

        Args:
            city_name: City name in Hebrew.

        Returns:
            String like "32.03,34.74,32.15,34.85".
        """
        bbox = self.get_city_bbox(city_name)
        return f"{bbox[0]},{bbox[1]},{bbox[2]},{bbox[3]}"


"""
Configuration module for the Yad2 Real Estate Scraper.

Provides a dataclass-based configuration system with sensible defaults
and validation for scraper settings.
"""

import random
from dataclasses import dataclass, field
from typing import List


@dataclass
class ScraperConfig:
    """
    Configuration settings for the Yad2 scraper.

    Attributes:
        cities: List of city names to scrape (Hebrew names supported).
        base_url: Base URL for yad2 real estate listings.
        output_path: Directory path for output Parquet files.
        min_delay: Minimum delay between requests in seconds.
        max_delay: Maximum delay between requests in seconds.
        page_timeout: Page load timeout in milliseconds.
        max_retries: Maximum number of retry attempts for failed requests.
        retry_delay: Base delay for exponential backoff in seconds.
        headless: Whether to run browser in headless mode.
    """

    # Target cities to scrape
    cities: List[str] = field(default_factory=list)

    # URL settings
    base_url: str = "https://www.yad2.co.il/realestate/forsale"

    # Output settings
    output_path: str = "data/output"

    # Rate limiting (anti-scraping protection)
    min_delay: float = 2.0
    max_delay: float = 5.0

    # Timeout settings
    page_timeout: int = 30000  # milliseconds

    # Retry settings (network resilience)
    max_retries: int = 3
    retry_delay: float = 2.0  # base delay for exponential backoff

    # Browser settings
    headless: bool = True

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

    def get_random_delay(self) -> float:
        """
        Generate a random delay between min_delay and max_delay.

        Used to add human-like randomness to request timing,
        helping to avoid anti-scraping detection.

        Returns:
            Random float between min_delay and max_delay (inclusive).
        """
        return random.uniform(self.min_delay, self.max_delay)


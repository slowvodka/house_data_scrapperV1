"""
Unit tests for the Configuration Module.

TDD Phase: RED - Writing tests before implementation.
"""

import pytest
from src.config import ScraperConfig


class TestScraperConfigDefaults:
    """Test that ScraperConfig has sensible default values."""

    def test_config_has_default_base_url(self):
        """Config should have yad2 base URL by default."""
        config = ScraperConfig()
        assert config.base_url == "https://www.yad2.co.il/realestate/forsale"

    def test_config_has_default_output_path(self):
        """Config should have default output directory."""
        config = ScraperConfig()
        assert config.output_path == "data/output"

    def test_config_has_default_request_delay(self):
        """Config should have default delay between requests (2-5 seconds range)."""
        config = ScraperConfig()
        assert config.min_delay == 2.0
        assert config.max_delay == 5.0

    def test_config_has_default_page_timeout(self):
        """Config should have default page load timeout of 30 seconds."""
        config = ScraperConfig()
        assert config.page_timeout == 30000  # milliseconds

    def test_config_has_default_retry_settings(self):
        """Config should have default retry settings."""
        config = ScraperConfig()
        assert config.max_retries == 3
        assert config.retry_delay == 2.0  # base delay for exponential backoff

    def test_config_has_empty_cities_by_default(self):
        """Config should have empty cities list by default (must be provided)."""
        config = ScraperConfig()
        assert config.cities == []

    def test_config_has_headless_true_by_default(self):
        """Config should run headless by default."""
        config = ScraperConfig()
        assert config.headless is True


class TestScraperConfigCustomValues:
    """Test that ScraperConfig accepts custom values."""

    def test_config_accepts_custom_cities_list(self):
        """Config should accept a custom list of cities."""
        cities = ["תל אביב", "חיפה", "ירושלים"]
        config = ScraperConfig(cities=cities)
        assert config.cities == cities

    def test_config_accepts_custom_output_path(self):
        """Config should accept a custom output path."""
        config = ScraperConfig(output_path="custom/output")
        assert config.output_path == "custom/output"

    def test_config_accepts_custom_delays(self):
        """Config should accept custom delay settings."""
        config = ScraperConfig(min_delay=1.0, max_delay=3.0)
        assert config.min_delay == 1.0
        assert config.max_delay == 3.0

    def test_config_accepts_headless_false(self):
        """Config should allow running with visible browser."""
        config = ScraperConfig(headless=False)
        assert config.headless is False


class TestScraperConfigMethods:
    """Test ScraperConfig helper methods."""

    def test_get_random_delay_within_range(self):
        """get_random_delay should return value between min and max delay."""
        config = ScraperConfig(min_delay=2.0, max_delay=5.0)
        # Test multiple times to ensure randomness stays in range
        for _ in range(100):
            delay = config.get_random_delay()
            assert 2.0 <= delay <= 5.0

    def test_get_random_delay_with_equal_min_max(self):
        """get_random_delay should work when min equals max."""
        config = ScraperConfig(min_delay=3.0, max_delay=3.0)
        delay = config.get_random_delay()
        assert delay == 3.0


class TestScraperConfigValidation:
    """Test that ScraperConfig validates input correctly."""

    def test_config_validates_min_delay_not_negative(self):
        """Config should raise error if min_delay is negative."""
        with pytest.raises(ValueError, match="min_delay must be non-negative"):
            ScraperConfig(min_delay=-1.0)

    def test_config_validates_max_delay_greater_than_min(self):
        """Config should raise error if max_delay < min_delay."""
        with pytest.raises(ValueError, match="max_delay must be >= min_delay"):
            ScraperConfig(min_delay=5.0, max_delay=2.0)

    def test_config_validates_page_timeout_positive(self):
        """Config should raise error if page_timeout is not positive."""
        with pytest.raises(ValueError, match="page_timeout must be positive"):
            ScraperConfig(page_timeout=0)

    def test_config_validates_max_retries_non_negative(self):
        """Config should raise error if max_retries is negative."""
        with pytest.raises(ValueError, match="max_retries must be non-negative"):
            ScraperConfig(max_retries=-1)


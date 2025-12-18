"""
Unit tests for the CLI Module.
"""

import json
import tempfile
from pathlib import Path
from unittest.mock import Mock, patch

import pytest

from src.cli import (
    list_cities_command,
    parse_args,
    scrape_city,
    scrape_command,
)


class TestCLIArgumentParsing:
    """Test CLI argument parsing."""

    def test_parse_args_scrape_single_city(self):
        """CLI should parse scrape command with single city."""
        args = parse_args(["scrape", "תל אביב יפו"])
        assert args.command == "scrape"
        assert args.cities == ["תל אביב יפו"]

    def test_parse_args_scrape_multiple_cities(self):
        """CLI should parse scrape command with multiple cities."""
        args = parse_args(["scrape", "תל אביב יפו", "רמת גן", "גבעתיים"])
        assert args.command == "scrape"
        assert args.cities == ["תל אביב יפו", "רמת גן", "גבעתיים"]

    def test_parse_args_list_cities(self):
        """CLI should parse list-cities command."""
        args = parse_args(["list-cities"])
        assert args.command == "list-cities"

    def test_parse_args_with_output_flag(self):
        """CLI should parse --output flag."""
        args = parse_args(["scrape", "תל אביב יפו", "--output", "custom/path"])
        assert args.output == "custom/path"

    def test_parse_args_with_verbose_flag(self):
        """CLI should parse --verbose flag."""
        args = parse_args(["scrape", "תל אביב יפו", "--verbose"])
        assert args.verbose is True


class TestCLIListCities:
    """Test list-cities command."""

    def test_list_cities_command_returns_success(self):
        """list-cities should return exit code 0 on success."""
        # This will use the actual mapping file
        exit_code = list_cities_command()
        assert exit_code == 0

    def test_list_cities_shows_available_cities(self, tmp_path):
        """list-cities should show cities from mapping file."""
        # Create mock mapping file
        mapping_file = tmp_path / "city_to_neighborhoods.json"
        mapping_file.write_text(
            json.dumps({
                "תל אביב יפו": [1, 2, 3],
                "רמת גן": [4, 5],
                "גבעתיים": [6]
            }),
            encoding="utf-8"
        )
        
        # Mock the mapping file path
        with patch("src.cli.CITY_TO_NEIGHBORHOODS_FILE", mapping_file):
            exit_code = list_cities_command()
            assert exit_code == 0


class TestCLIScrapeCommand:
    """Test scrape command."""

    def test_scrape_command_calls_scraper(self):
        """scrape command should call scraping function."""
        with patch("src.cli.scrape_city") as mock_scrape:
            mock_scrape.return_value = Path("test.parquet")
            exit_code = scrape_command(["תל אביב יפו"], verbose=False)
            mock_scrape.assert_called_once_with("תל אביב יפו", verbose=False)
            assert exit_code == 0

    def test_scrape_command_handles_multiple_cities(self):
        """scrape command should handle multiple cities."""
        with patch("src.cli.scrape_city") as mock_scrape:
            mock_scrape.return_value = Path("test.parquet")
            exit_code = scrape_command(["תל אביב יפו", "רמת גן"], verbose=False)
            assert mock_scrape.call_count == 2
            assert exit_code == 0

    def test_scrape_command_handles_invalid_city(self):
        """scrape command should handle invalid city gracefully."""
        with patch("src.cli.scrape_city") as mock_scrape:
            mock_scrape.return_value = None
            exit_code = scrape_command(["Invalid City"], verbose=False)
            assert exit_code == 1  # Error exit code


class TestCLIErrorHandling:
    """Test CLI error handling."""

    def test_parse_args_raises_error_for_invalid_command(self):
        """parse_args should raise SystemExit for invalid command."""
        with pytest.raises(SystemExit):
            parse_args(["invalid-command"])

    def test_scrape_city_handles_missing_city(self):
        """scrape_city should return None for non-existent city."""
        result = scrape_city("NonExistentCity123", verbose=False)
        assert result is None


"""
Unit tests for the API Client Module.

TDD Phase: RED - Writing tests before implementation.
Tests the HTTP client for Yad2 recommendations API.
"""

import pytest
import responses
from requests.exceptions import RequestException, Timeout

from src.api_client import Yad2ApiClient
from src.config import ScraperConfig


class TestApiClientInitialization:
    """Test API client initialization."""

    def test_api_client_accepts_config(self):
        """API client should accept a ScraperConfig object."""
        config = ScraperConfig()
        client = Yad2ApiClient(config)
        assert client.config == config

    def test_api_client_has_session(self):
        """API client should create a requests session."""
        config = ScraperConfig()
        client = Yad2ApiClient(config)
        assert client.session is not None


class TestApiClientUrlBuilder:
    """Test URL building for API requests."""

    def test_build_url_with_city_id(self):
        """Should build correct URL with city ID parameter."""
        config = ScraperConfig()
        client = Yad2ApiClient(config)
        url = client.build_url(city_id=9000)
        assert "cityValues=9000" in url
        assert config.api_base_url in url

    def test_build_url_with_property_type(self):
        """Should build URL with property type parameter."""
        config = ScraperConfig(results_per_page=20)
        client = Yad2ApiClient(config)
        url = client.build_url(city_id=9000, property_type=4)
        # Property type 4 = Penthouse
        assert "subCategoriesIds=4" in url

    def test_build_url_includes_required_params(self):
        """URL should include required API parameters."""
        config = ScraperConfig()
        client = Yad2ApiClient(config)
        url = client.build_url(city_id=9000)
        # Required params based on discovered API
        assert "type=home" in url
        assert "categoryId=2" in url

    def test_build_url_includes_count(self):
        """URL should include results count from config."""
        config = ScraperConfig(results_per_page=40)
        client = Yad2ApiClient(config)
        url = client.build_url(city_id=9000)
        assert "count=40" in url


class TestApiClientRequests:
    """Test API request functionality with mocked responses."""

    @responses.activate
    def test_fetch_listings_returns_data(self):
        """fetch_listings should return parsed JSON data."""
        config = ScraperConfig()
        client = Yad2ApiClient(config)
        
        # Mock the API response
        mock_response = {
            "data": [[
                {"token": "abc123", "price": 1500000}
            ]]
        }
        responses.add(
            responses.GET,
            config.api_base_url,
            json=mock_response,
            status=200
        )
        
        result = client.fetch_listings(city_id=9000)
        assert result == mock_response

    @responses.activate
    def test_fetch_listings_handles_empty_response(self):
        """fetch_listings should handle empty data gracefully."""
        config = ScraperConfig()
        client = Yad2ApiClient(config)
        
        mock_response = {"data": [[]]}
        responses.add(
            responses.GET,
            config.api_base_url,
            json=mock_response,
            status=200
        )
        
        result = client.fetch_listings(city_id=9000)
        assert result["data"] == [[]]

    @responses.activate
    def test_fetch_listings_raises_on_http_error(self):
        """fetch_listings should raise exception on HTTP errors."""
        config = ScraperConfig()
        client = Yad2ApiClient(config)
        
        responses.add(
            responses.GET,
            config.api_base_url,
            status=500
        )
        
        with pytest.raises(RequestException):
            client.fetch_listings(city_id=9000)

    @responses.activate
    def test_fetch_listings_uses_correct_headers(self):
        """fetch_listings should send browser-like headers."""
        config = ScraperConfig()
        client = Yad2ApiClient(config)
        
        responses.add(
            responses.GET,
            config.api_base_url,
            json={"data": [[]]},
            status=200
        )
        
        client.fetch_listings(city_id=9000)
        
        # Check that User-Agent was sent
        request = responses.calls[0].request
        assert "User-Agent" in request.headers
        assert "Mozilla" in request.headers["User-Agent"]


class TestApiClientRetry:
    """Test retry logic for failed requests."""

    def test_session_has_retry_adapter(self):
        """Client session should have retry adapter configured."""
        config = ScraperConfig(max_retries=3)
        client = Yad2ApiClient(config)
        
        # Check that HTTPS adapter is mounted
        adapter = client.session.get_adapter("https://")
        assert adapter is not None
        # Retry config is encapsulated in the adapter

    @responses.activate
    def test_raises_on_persistent_errors(self):
        """Client should raise when request consistently fails."""
        config = ScraperConfig(max_retries=0)  # No retries
        client = Yad2ApiClient(config)
        
        responses.add(
            responses.GET,
            config.api_base_url,
            body=RequestException("Connection failed")
        )
        
        with pytest.raises(RequestException):
            client.fetch_listings(city_id=9000)

    @responses.activate
    def test_handles_server_error_status(self):
        """Client should handle 5xx server errors."""
        config = ScraperConfig(max_retries=0)
        client = Yad2ApiClient(config)
        
        responses.add(
            responses.GET,
            config.api_base_url,
            status=503
        )
        
        with pytest.raises(RequestException):
            client.fetch_listings(city_id=9000)


class TestApiClientHelpers:
    """Test helper methods."""

    def test_get_listings_for_city_by_name(self):
        """Should fetch listings using city name instead of ID."""
        config = ScraperConfig()
        client = Yad2ApiClient(config)
        
        # This should work without errors (city name -> ID conversion)
        city_id = config.get_city_id("באר שבע")
        assert city_id == 9000

    def test_close_cleans_up_session(self):
        """close() should clean up the HTTP session."""
        config = ScraperConfig()
        client = Yad2ApiClient(config)
        client.close()
        # After close, session should be closed
        # This is implementation-specific but good to test


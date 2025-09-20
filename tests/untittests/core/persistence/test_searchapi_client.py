"""Tests for SearchAPI.io HTTP client."""

from typing import Any
from unittest.mock import AsyncMock, Mock, patch

import httpx
import pytest

from src.core.config import SearchAPISettings
from src.core.persistence.searchapi_client import (
    SearchAPIAuthenticationError,
    SearchAPIClient,
    SearchAPIError,
    SearchAPIRateLimitError,
    SearchAPITimeoutError,
)


class TestSearchAPIClient:
    """Test suite for SearchAPIClient."""

    @pytest.fixture
    def settings(self) -> SearchAPISettings:
        """Create test SearchAPI settings."""
        return SearchAPISettings(
            api_key="test-api-key",
            base_url="https://api.test.com/v1",
            timeout=30,
            max_retries=3,
        )

    @pytest.fixture
    def client(self, settings: SearchAPISettings) -> SearchAPIClient:
        """Create SearchAPIClient instance for testing."""
        return SearchAPIClient(settings)

    @pytest.fixture
    def mock_response_data(self) -> dict[str, Any]:
        """Mock SearchAPI.io response data."""
        return {
            "search_metadata": {
                "status": "Success",
                "total_time_taken": 1.23,
            },
            "properties": [
                {
                    "name": "Test Hotel",
                    "gps_coordinates": {"latitude": 40.7128, "longitude": -74.0060},
                    "check_in_time": "3:00 PM",
                    "check_out_time": "11:00 AM",
                    "rate_per_night": {"lowest": "$150"},
                    "total_rate": {"lowest": "$300"},
                    "nearby_places": [{"name": "Central Park", "transportations": []}],
                    "hotel_class": "4-star hotel",
                    "extracted_hotel_class": 4,
                    "images": [],
                    "overall_rating": 4.5,
                    "reviews": 1250,
                    "location_rating": 4.7,
                    "amenities": ["Free WiFi", "Pool", "Gym"],
                    "excluded_amenities": [],
                    "essential_info": [],
                }
            ],
        }

    async def test_initialization(self, settings: SearchAPISettings) -> None:
        """Test SearchAPIClient initialization."""
        client = SearchAPIClient(settings)
        assert client._settings == settings
        assert client._client is None

    async def test_context_manager(self, client: SearchAPIClient) -> None:
        """Test async context manager functionality."""
        async with client as managed_client:
            assert managed_client is client
            assert client._client is not None
            assert isinstance(client._client, httpx.AsyncClient)

        # Client should be closed after context exit
        assert client._client is None

    async def test_ensure_client_creates_httpx_client(self, client: SearchAPIClient) -> None:
        """Test that _ensure_client creates httpx.AsyncClient with proper configuration."""
        await client._ensure_client()

        assert client._client is not None
        assert isinstance(client._client, httpx.AsyncClient)
        assert client._client.timeout.connect == client._settings.timeout

        await client.close()

    async def test_close_cleans_up_client(self, client: SearchAPIClient) -> None:
        """Test that close() properly cleans up HTTP client."""
        await client._ensure_client()
        assert client._client is not None

        await client.close()
        assert client._client is None

    @patch("httpx.AsyncClient.get")
    async def test_search_hotels_success(
        self,
        mock_get: AsyncMock,
        client: SearchAPIClient,
        mock_response_data: dict[str, Any],
    ) -> None:
        """Test successful hotel search request."""
        # Setup mock response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = mock_response_data
        mock_get.return_value = mock_response

        result = await client.search_hotels(
            location="New York",
            check_in_date="2024-12-01",
            check_out_date="2024-12-03",
            property_type="hotel",
            adults=2,
        )

        # Verify the result
        assert result == mock_response_data
        assert "properties" in result
        assert len(result["properties"]) == 1
        assert result["properties"][0]["name"] == "Test Hotel"

        # Verify the request was made with correct parameters
        mock_get.assert_called_once()
        call_args = mock_get.call_args
        assert call_args[0][0] == "https://api.test.com/v1/search"

        params = call_args[1]["params"]
        assert params["engine"] == "google_hotels"
        assert params["q"] == "New York"
        assert params["check_in_date"] == "2024-12-01"
        assert params["check_out_date"] == "2024-12-03"
        assert params["property_type"] == "hotel"
        assert params["adults"] == "2"
        assert params["api_key"] == "test-api-key"

        await client.close()

    @patch("httpx.AsyncClient.get")
    async def test_search_hotels_default_parameters(
        self,
        mock_get: AsyncMock,
        client: SearchAPIClient,
        mock_response_data: dict[str, Any],
    ) -> None:
        """Test hotel search with default parameters."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = mock_response_data
        mock_get.return_value = mock_response

        await client.search_hotels(
            location="Paris",
            check_in_date="2024-12-15",
            check_out_date="2024-12-17",
        )

        # Verify default parameters were used
        params = mock_get.call_args[1]["params"]
        assert params["property_type"] == "hotel"
        assert params["adults"] == "2"

        await client.close()

    @patch("httpx.AsyncClient.get")
    async def test_search_hotels_authentication_error(self, mock_get: AsyncMock, client: SearchAPIClient) -> None:
        """Test handling of authentication errors (401)."""
        mock_response = Mock()
        mock_response.status_code = 401
        mock_get.return_value = mock_response

        with pytest.raises(SearchAPIAuthenticationError) as exc_info:
            await client.search_hotels(
                location="Test Location",
                check_in_date="2024-12-01",
                check_out_date="2024-12-03",
            )

        assert "Invalid SearchAPI.io API key" in str(exc_info.value)
        await client.close()

    @patch("httpx.AsyncClient.get")
    async def test_search_hotels_rate_limit_error(self, mock_get: AsyncMock, client: SearchAPIClient) -> None:
        """Test handling of rate limit errors (429)."""
        mock_response = Mock()
        mock_response.status_code = 429
        mock_get.return_value = mock_response

        with pytest.raises(SearchAPIRateLimitError) as exc_info:
            await client.search_hotels(
                location="Test Location",
                check_in_date="2024-12-01",
                check_out_date="2024-12-03",
            )

        assert "SearchAPI.io rate limit exceeded" in str(exc_info.value)
        await client.close()

    @patch("httpx.AsyncClient.get")
    async def test_search_hotels_general_http_error(self, mock_get: AsyncMock, client: SearchAPIClient) -> None:
        """Test handling of general HTTP errors (4xx/5xx)."""
        mock_response = Mock()
        mock_response.status_code = 500
        mock_response.text = "Internal Server Error"
        mock_get.return_value = mock_response

        with pytest.raises(SearchAPIError) as exc_info:
            await client.search_hotels(
                location="Test Location",
                check_in_date="2024-12-01",
                check_out_date="2024-12-03",
            )

        assert "SearchAPI.io request failed with status 500" in str(exc_info.value)
        assert "Internal Server Error" in str(exc_info.value)
        await client.close()

    @patch("httpx.AsyncClient.get")
    async def test_search_hotels_timeout_error(self, mock_get: AsyncMock, client: SearchAPIClient) -> None:
        """Test handling of timeout errors."""
        mock_get.side_effect = httpx.TimeoutException("Request timed out")

        with pytest.raises(SearchAPITimeoutError) as exc_info:
            await client.search_hotels(
                location="Test Location",
                check_in_date="2024-12-01",
                check_out_date="2024-12-03",
            )

        assert "SearchAPI.io request timed out after 30s" in str(exc_info.value)
        await client.close()

    @patch("httpx.AsyncClient.get")
    async def test_search_hotels_http_error(self, mock_get: AsyncMock, client: SearchAPIClient) -> None:
        """Test handling of general HTTP errors."""
        mock_get.side_effect = httpx.HTTPError("Network error")

        with pytest.raises(SearchAPIError) as exc_info:
            await client.search_hotels(
                location="Test Location",
                check_in_date="2024-12-01",
                check_out_date="2024-12-03",
            )

        assert "HTTP error during SearchAPI.io request" in str(exc_info.value)
        await client.close()

    async def test_search_hotels_no_client_error(self, client: SearchAPIClient) -> None:
        """Test error when HTTP client is not initialized."""
        # Patch _ensure_client to not create a client
        with patch.object(client, "_ensure_client") as mock_ensure:
            mock_ensure.return_value = None
            client._client = None

            with pytest.raises(SearchAPIError) as exc_info:
                await client.search_hotels(
                    location="Test Location",
                    check_in_date="2024-12-01",
                    check_out_date="2024-12-03",
                )

            assert "HTTP client not initialized" in str(exc_info.value)

    async def test_session_context_manager(self, client: SearchAPIClient, mock_response_data: dict[str, Any]) -> None:
        """Test session context manager for multiple API calls."""
        with patch("httpx.AsyncClient.get") as mock_get:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = mock_response_data
            mock_get.return_value = mock_response

            async with client.session() as session:
                # First call
                result1 = await session.search_hotels(
                    location="New York",
                    check_in_date="2024-12-01",
                    check_out_date="2024-12-03",
                )

                # Second call using same session
                result2 = await session.search_hotels(
                    location="Paris",
                    check_in_date="2024-12-05",
                    check_out_date="2024-12-07",
                )

                assert result1 == mock_response_data
                assert result2 == mock_response_data
                assert mock_get.call_count == 2

            # Client should be closed after session exit
            assert client._client is None

    async def test_multiple_close_calls_safe(self, client: SearchAPIClient) -> None:
        """Test that multiple close() calls are safe."""
        await client._ensure_client()
        assert client._client is not None

        # First close
        await client.close()
        assert client._client is None

        # Second close should not raise an error
        await client.close()
        assert client._client is None

    async def test_vacation_rental_property_type(
        self, client: SearchAPIClient, mock_response_data: dict[str, Any]
    ) -> None:
        """Test search with vacation_rental property type."""
        with patch("httpx.AsyncClient.get") as mock_get:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = mock_response_data
            mock_get.return_value = mock_response

            await client.search_hotels(
                location="Miami",
                check_in_date="2024-12-10",
                check_out_date="2024-12-12",
                property_type="vacation_rental",
                adults=4,
            )

            params = mock_get.call_args[1]["params"]
            assert params["property_type"] == "vacation_rental"
            assert params["adults"] == "4"

            await client.close()


class TestSearchAPIClientExceptions:
    """Test suite for SearchAPIClient custom exceptions."""

    def test_searchapi_error_inheritance(self) -> None:
        """Test that custom exceptions inherit from appropriate base classes."""
        assert issubclass(SearchAPIError, Exception)
        assert issubclass(SearchAPITimeoutError, SearchAPIError)
        assert issubclass(SearchAPIRateLimitError, SearchAPIError)
        assert issubclass(SearchAPIAuthenticationError, SearchAPIError)

    def test_exception_messages(self) -> None:
        """Test that exceptions can be created with custom messages."""
        error = SearchAPIError("Custom error message")
        assert str(error) == "Custom error message"

        timeout_error = SearchAPITimeoutError("Timeout occurred")
        assert str(timeout_error) == "Timeout occurred"

        rate_limit_error = SearchAPIRateLimitError("Rate limit exceeded")
        assert str(rate_limit_error) == "Rate limit exceeded"

        auth_error = SearchAPIAuthenticationError("Authentication failed")
        assert str(auth_error) == "Authentication failed"

"""Tests for hotel service business logic."""

from datetime import date, timedelta
from unittest.mock import AsyncMock

import pytest

from src.app.schemas.hotel_search import HotelSearchRequest, PropertyType
from src.app.services.hotel_service import HotelService
from src.app.services.searchapi.client import SearchAPIClient, SearchAPIError


class TestHotelService:
    """Test suite for HotelService business logic."""

    @pytest.fixture
    def mock_searchapi_client(self) -> AsyncMock:
        """Create a mock SearchAPI client."""
        client = AsyncMock(spec=SearchAPIClient)
        return client

    @pytest.fixture
    def hotel_service(self, mock_searchapi_client: AsyncMock) -> HotelService:
        """Create hotel service with mocked dependencies."""
        return HotelService(mock_searchapi_client)

    @pytest.fixture
    def sample_request(self) -> HotelSearchRequest:
        """Create a sample hotel search request."""
        tomorrow = date.today() + timedelta(days=1)
        day_after = tomorrow + timedelta(days=1)

        return HotelSearchRequest(
            q="New York", check_in=tomorrow, check_out=day_after, property_type=PropertyType.HOTEL, adults=2
        )

    @pytest.fixture
    def mock_searchapi_response(self) -> dict:
        """Mock response from SearchAPI.io."""
        return {
            "search_metadata": {"id": "test-search-123", "status": "Success", "processed_at": "2024-01-01T12:00:00Z"},
            "search_parameters": {
                "engine": "google_hotels",
                "q": "New York",
                "check_in_date": "2024-01-01",
                "check_out_date": "2024-01-02",
            },
            "properties": [
                {
                    "name": "Test Hotel",
                    "description": "A test hotel in New York",
                    "address": "123 Test St, New York, NY",
                    "price": {"rate": 150.0, "total": 300.0, "currency": "USD"},
                    "rating": {"rating": 4.5, "reviews_count": 1250},
                }
            ],
            "search_information": {"properties_results_state": "Results are ready"},
        }

    async def test_search_hotels_success(
        self,
        hotel_service: HotelService,
        mock_searchapi_client: AsyncMock,
        sample_request: HotelSearchRequest,
        mock_searchapi_response: dict,
    ) -> None:
        """Test successful hotel search operation."""
        # Setup mock
        mock_searchapi_client.search_hotels.return_value = mock_searchapi_response

        # Execute
        result = await hotel_service.search_hotels(sample_request)

        # Verify SearchAPI client was called correctly
        mock_searchapi_client.search_hotels.assert_called_once_with(
            location="New York",
            check_in_date=sample_request.check_in.isoformat(),
            check_out_date=sample_request.check_out.isoformat(),
            property_type="hotel",
            adults=2,
        )

        # Verify response structure
        assert result.search_metadata == mock_searchapi_response["search_metadata"]
        assert result.search_parameters == mock_searchapi_response["search_parameters"]
        assert len(result.properties) == 1
        # Properties are passed through as raw dict data from SearchAPI
        assert result.properties[0]["name"] == "Test Hotel"

    async def test_search_hotels_searchapi_error(
        self, hotel_service: HotelService, mock_searchapi_client: AsyncMock, sample_request: HotelSearchRequest
    ) -> None:
        """Test handling of SearchAPI errors."""
        # Setup mock to raise SearchAPIError
        mock_searchapi_client.search_hotels.side_effect = SearchAPIError("API Error")

        # Execute and verify exception is propagated
        with pytest.raises(SearchAPIError, match="API Error"):
            await hotel_service.search_hotels(sample_request)

    async def test_search_hotels_unexpected_error(
        self, hotel_service: HotelService, mock_searchapi_client: AsyncMock, sample_request: HotelSearchRequest
    ) -> None:
        """Test handling of unexpected errors."""
        # Setup mock to raise unexpected error
        mock_searchapi_client.search_hotels.side_effect = RuntimeError("Unexpected error")

        # Execute and verify exception is propagated
        with pytest.raises(RuntimeError, match="Unexpected error"):
            await hotel_service.search_hotels(sample_request)

    async def test_transform_searchapi_response_empty_properties(
        self, hotel_service: HotelService, mock_searchapi_client: AsyncMock, sample_request: HotelSearchRequest
    ) -> None:
        """Test response transformation with empty properties list."""
        empty_response = {"search_metadata": {"id": "test-123"}, "properties": []}

        mock_searchapi_client.search_hotels.return_value = empty_response

        result = await hotel_service.search_hotels(sample_request)

        assert len(result.properties) == 0
        assert result.search_metadata == {"id": "test-123"}

    async def test_transform_searchapi_response_missing_optional_fields(
        self, hotel_service: HotelService, mock_searchapi_client: AsyncMock, sample_request: HotelSearchRequest
    ) -> None:
        """Test response transformation when optional fields are missing."""
        minimal_response = {"properties": [{"name": "Minimal Hotel"}]}

        mock_searchapi_client.search_hotels.return_value = minimal_response

        result = await hotel_service.search_hotels(sample_request)

        assert len(result.properties) == 1
        assert result.search_metadata is None
        assert result.search_parameters is None
        assert result.filters is None

    async def test_parameter_transformation_vacation_rental(
        self, hotel_service: HotelService, mock_searchapi_client: AsyncMock, mock_searchapi_response: dict
    ) -> None:
        """Test parameter transformation for vacation rental property type."""
        tomorrow = date.today() + timedelta(days=1)
        day_after = tomorrow + timedelta(days=1)

        request = HotelSearchRequest(
            q="Paris, France",
            check_in=tomorrow,
            check_out=day_after,
            property_type=PropertyType.VACATION_RENTAL,
            adults=4,
        )

        mock_searchapi_client.search_hotels.return_value = mock_searchapi_response

        await hotel_service.search_hotels(request)

        # Verify correct parameters were passed
        mock_searchapi_client.search_hotels.assert_called_once_with(
            location="Paris, France",
            check_in_date=request.check_in.isoformat(),
            check_out_date=request.check_out.isoformat(),
            property_type="vacation_rental",
            adults=4,
        )

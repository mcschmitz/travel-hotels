"""End-to-end integration tests for hotel search functionality with real SearchAPI.io."""

import os
import time
from datetime import date, timedelta

import pytest
from fastapi.testclient import TestClient

from src.main import create_app
from tests.utils.decorators import github_actions_only


@pytest.fixture
def client() -> TestClient:
    """Create test client for integration tests."""
    app = create_app()
    return TestClient(app)


@pytest.fixture
def api_key() -> str:
    """Get SearchAPI.io API key from environment."""
    key = os.getenv("SEARCHAPI_API_KEY")
    if not key:
        pytest.skip("SEARCHAPI_API_KEY environment variable not set")
    return key


@pytest.fixture
def future_dates() -> dict[str, str]:
    """Generate future check-in and check-out dates for testing."""
    check_in = date.today() + timedelta(days=30)
    check_out = check_in + timedelta(days=3)
    return {"check_in": check_in.isoformat(), "check_out": check_out.isoformat()}


class TestEndToEndHotelSearch:
    """End-to-end integration tests for hotel search functionality."""

    @github_actions_only
    def test_hotel_search_new_york_success(self, client: TestClient, api_key: str, future_dates: dict) -> None:
        """Test successful hotel search for New York with real SearchAPI.io."""
        # Ensure API key is configured
        os.environ["SEARCHAPI_API_KEY"] = api_key

        start_time = time.time()

        response = client.get(
            "/api/v1/hotels/search",
            params={
                "q": "New York",
                "check_in": future_dates["check_in"],
                "check_out": future_dates["check_out"],
                "adults": 2,
                "property_type": "hotel",
            },
        )

        end_time = time.time()
        response_time = end_time - start_time

        # Validate response
        assert response.status_code == 200
        data = response.json()

        # Validate response structure
        assert "search_metadata" in data
        assert "search_parameters" in data
        assert "properties" in data

        # Validate search parameters
        params = data["search_parameters"]
        assert params["q"] == "New York"
        assert params["check_in"] == future_dates["check_in"]
        assert params["check_out"] == future_dates["check_out"]
        assert params["adults"] == 2

        # Validate properties (should have results for New York)
        properties = data["properties"]
        assert isinstance(properties, list)

        if properties:
            # Validate first property structure
            prop = properties[0]
            assert "name" in prop
            assert "price" in prop or "rate_per_night" in prop

        # Performance validation (should respond within 10 seconds)
        assert response_time < 10.0, f"Response time {response_time:.2f}s exceeded 10s threshold"

    @github_actions_only
    def test_hotel_search_invalid_location(self, client: TestClient, api_key: str, future_dates: dict) -> None:
        """Test hotel search with invalid location."""
        # Ensure API key is configured
        os.environ["SEARCHAPI_API_KEY"] = api_key

        response = client.get(
            "/api/v1/hotels/search",
            params={
                "q": "InvalidLocationThatDoesNotExist12345",
                "check_in": future_dates["check_in"],
                "check_out": future_dates["check_out"],
                "adults": 2,
            },
        )

        assert response.status_code == 200
        data = response.json()

        # Validate response structure exists
        assert "search_metadata" in data
        assert "search_parameters" in data
        assert "properties" in data

    def test_hotel_search_parameter_validation(self, client: TestClient, api_key: str) -> None:
        """Test parameter validation with real API."""
        # Ensure API key is configured
        os.environ["SEARCHAPI_API_KEY"] = api_key

        # Test missing required parameters
        response = client.get("/api/v1/hotels/search")
        assert response.status_code == 422  # Validation error

        # Test invalid date format
        response = client.get(
            "/api/v1/hotels/search",
            params={"q": "New York", "check_in": "invalid-date", "check_out": "2024-12-05", "adults": 2},
        )
        assert response.status_code == 422  # Validation error

    def test_hotel_search_past_date_validation(self, client: TestClient, api_key: str) -> None:
        """Test validation of past check-in dates."""
        os.environ["SEARCHAPI_API_KEY"] = api_key

        # Test past check-in date
        past_date = (date.today() - timedelta(days=1)).isoformat()
        future_date = (date.today() + timedelta(days=5)).isoformat()

        response = client.get(
            "/api/v1/hotels/search",
            params={"q": "New York", "check_in": past_date, "check_out": future_date, "adults": 2},
        )
        assert response.status_code == 422  # Validation error

    def test_hotel_search_error_handling_no_api_key(self, client: TestClient) -> None:
        """Test error handling when API key is missing."""
        original_key = os.environ.pop("SEARCHAPI_API_KEY", None)

        try:
            future_date = (date.today() + timedelta(days=30)).isoformat()
            checkout_date = (date.today() + timedelta(days=33)).isoformat()

            response = client.get(
                "/api/v1/hotels/search",
                params={"q": "New York", "check_in": future_date, "check_out": checkout_date, "adults": 2},
            )

            assert response.status_code in [401, 500, 502]  # Authentication or server error

        finally:
            if original_key:
                os.environ["SEARCHAPI_API_KEY"] = original_key

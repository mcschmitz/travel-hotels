"""End-to-end integration tests for hotel search functionality with real SearchAPI.io."""

import os
import time
from datetime import date, timedelta

import pytest
from fastapi.testclient import TestClient

from src.main import create_app


@pytest.fixture
def client():
    """Create test client for integration tests."""
    app = create_app()
    return TestClient(app)


@pytest.fixture
def api_key():
    """Get SearchAPI.io API key from environment."""
    key = os.getenv("SEARCHAPI_API_KEY")
    if not key:
        pytest.skip("SEARCHAPI_API_KEY environment variable not set")
    return key


@pytest.fixture
def future_dates():
    """Generate future check-in and check-out dates for testing."""
    check_in = date.today() + timedelta(days=30)
    check_out = check_in + timedelta(days=3)
    return {"check_in": check_in.isoformat(), "check_out": check_out.isoformat()}


class TestEndToEndHotelSearch:
    """End-to-end integration tests for hotel search functionality."""

    def test_hotel_search_new_york_success(self, client: TestClient, api_key: str, future_dates: dict):
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

        print(f"✅ New York search completed in {response_time:.2f}s with {len(properties)} properties")

    def test_hotel_search_paris_success(self, client: TestClient, api_key: str, future_dates: dict):
        """Test successful hotel search for Paris with real SearchAPI.io."""
        # Ensure API key is configured
        os.environ["SEARCHAPI_API_KEY"] = api_key

        start_time = time.time()

        response = client.get(
            "/api/v1/hotels/search",
            params={
                "q": "Paris, France",
                "check_in": future_dates["check_in"],
                "check_out": future_dates["check_out"],
                "adults": 1,
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
        assert "Paris" in params["q"]
        assert params["adults"] == 1

        # Performance validation
        assert response_time < 10.0, f"Response time {response_time:.2f}s exceeded 10s threshold"

        print(f"✅ Paris search completed in {response_time:.2f}s")

    def test_hotel_search_invalid_location(self, client: TestClient, api_key: str, future_dates: dict):
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

        # Should still return 200 but with empty or minimal results
        assert response.status_code == 200
        data = response.json()

        # Validate response structure exists
        assert "search_metadata" in data
        assert "search_parameters" in data
        assert "properties" in data

        print("✅ Invalid location handled gracefully")

    def test_hotel_search_parameter_validation(self, client: TestClient, api_key: str):
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

        print("✅ Parameter validation working correctly")

    def test_hotel_search_past_date_validation(self, client: TestClient, api_key: str):
        """Test validation of past check-in dates."""
        # Ensure API key is configured
        os.environ["SEARCHAPI_API_KEY"] = api_key

        # Test past check-in date
        past_date = (date.today() - timedelta(days=1)).isoformat()
        future_date = (date.today() + timedelta(days=5)).isoformat()

        response = client.get(
            "/api/v1/hotels/search",
            params={"q": "New York", "check_in": past_date, "check_out": future_date, "adults": 2},
        )
        assert response.status_code == 422  # Validation error

        print("✅ Past date validation working correctly")

    def test_hotel_search_different_property_types(self, client: TestClient, api_key: str, future_dates: dict):
        """Test different property types."""
        # Ensure API key is configured
        os.environ["SEARCHAPI_API_KEY"] = api_key

        property_types = ["hotel", "vacation_rental", "bed_and_breakfast"]

        for prop_type in property_types:
            response = client.get(
                "/api/v1/hotels/search",
                params={
                    "q": "San Francisco",
                    "check_in": future_dates["check_in"],
                    "check_out": future_dates["check_out"],
                    "adults": 2,
                    "property_type": prop_type,
                },
            )

            assert response.status_code == 200
            data = response.json()
            assert data["search_parameters"]["property_type"] == prop_type

            print(f"✅ Property type '{prop_type}' search successful")

    def test_hotel_search_various_adult_counts(self, client: TestClient, api_key: str, future_dates: dict):
        """Test different adult counts."""
        # Ensure API key is configured
        os.environ["SEARCHAPI_API_KEY"] = api_key

        adult_counts = [1, 2, 4, 8]

        for adults in adult_counts:
            response = client.get(
                "/api/v1/hotels/search",
                params={
                    "q": "Los Angeles",
                    "check_in": future_dates["check_in"],
                    "check_out": future_dates["check_out"],
                    "adults": adults,
                },
            )

            assert response.status_code == 200
            data = response.json()
            assert data["search_parameters"]["adults"] == adults

            print(f"✅ Adult count {adults} search successful")

    @pytest.mark.slow
    def test_hotel_search_performance_benchmark(self, client: TestClient, api_key: str, future_dates: dict):
        """Benchmark performance with multiple requests."""
        # Ensure API key is configured
        os.environ["SEARCHAPI_API_KEY"] = api_key

        locations = ["New York", "London", "Tokyo", "Sydney"]
        response_times = []

        for location in locations:
            start_time = time.time()

            response = client.get(
                "/api/v1/hotels/search",
                params={
                    "q": location,
                    "check_in": future_dates["check_in"],
                    "check_out": future_dates["check_out"],
                    "adults": 2,
                },
            )

            end_time = time.time()
            response_time = end_time - start_time
            response_times.append(response_time)

            assert response.status_code == 200

            # Brief pause to avoid rate limiting
            time.sleep(1)

            print(f"✅ {location} search: {response_time:.2f}s")

        # Performance validation
        avg_response_time = sum(response_times) / len(response_times)
        max_response_time = max(response_times)

        assert avg_response_time < 8.0, f"Average response time {avg_response_time:.2f}s exceeded 8s"
        assert max_response_time < 15.0, f"Max response time {max_response_time:.2f}s exceeded 15s"

        print(f"✅ Performance benchmark: avg={avg_response_time:.2f}s, max={max_response_time:.2f}s")

    def test_hotel_search_error_handling_no_api_key(self, client: TestClient):
        """Test error handling when API key is missing."""
        # Remove API key temporarily
        original_key = os.environ.pop("SEARCHAPI_API_KEY", None)

        try:
            future_date = (date.today() + timedelta(days=30)).isoformat()
            checkout_date = (date.today() + timedelta(days=33)).isoformat()

            response = client.get(
                "/api/v1/hotels/search",
                params={"q": "New York", "check_in": future_date, "check_out": checkout_date, "adults": 2},
            )

            # Should return an error due to missing API key
            assert response.status_code in [401, 500, 502]  # Authentication or server error

            print(f"✅ Missing API key handled correctly: {response.status_code}")

        finally:
            # Restore API key if it existed
            if original_key:
                os.environ["SEARCHAPI_API_KEY"] = original_key

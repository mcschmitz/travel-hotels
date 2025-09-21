"""Comprehensive tests for hotel search Pydantic models."""

from datetime import date, timedelta
from typing import Any

import pytest
from pydantic import ValidationError

from src.app.schemas.hotel_search import (
    HotelAmenity,
    HotelPrice,
    HotelRating,
    HotelResult,
    HotelSearchRequest,
    HotelSearchResponse,
    PropertyType,
    SearchAPIErrorResponse,
)


class TestPropertyType:
    """Test suite for PropertyType enum."""

    def test_property_type_values(self) -> None:
        """Test PropertyType enum has correct values."""
        assert PropertyType.HOTEL == "hotel"
        assert PropertyType.VACATION_RENTAL == "vacation_rental"

    def test_property_type_string_conversion(self) -> None:
        """Test PropertyType can be used as string."""
        assert PropertyType.HOTEL.value == "hotel"
        assert PropertyType.VACATION_RENTAL.value == "vacation_rental"


class TestHotelSearchRequest:
    """Test suite for HotelSearchRequest model with comprehensive validation."""

    def test_valid_request_minimal(self) -> None:
        """Test valid request with minimal required fields."""
        tomorrow = date.today() + timedelta(days=1)
        day_after = date.today() + timedelta(days=2)

        request = HotelSearchRequest(
            q="New York",
            check_in=tomorrow.isoformat(),
            check_out=day_after.isoformat(),
        )

        assert request.q == "New York"
        assert request.check_in == tomorrow.isoformat()
        assert request.check_out == day_after.isoformat()
        assert request.property_type == PropertyType.HOTEL  # default
        assert request.adults == 2  # default

    def test_valid_request_all_fields(self) -> None:
        """Test valid request with all fields specified."""
        tomorrow = date.today() + timedelta(days=1)
        day_after = date.today() + timedelta(days=2)

        request = HotelSearchRequest(
            q="Paris, France",
            check_in=tomorrow.isoformat(),
            check_out=day_after.isoformat(),
            property_type=PropertyType.VACATION_RENTAL,
            adults=4,
        )

        assert request.q == "Paris, France"
        assert request.property_type == PropertyType.VACATION_RENTAL
        assert request.adults == 4

    def test_location_query_validation_empty(self) -> None:
        """Test location query validation for empty values."""
        tomorrow = date.today() + timedelta(days=1)
        day_after = date.today() + timedelta(days=2)

        # Empty string
        with pytest.raises(ValidationError) as exc_info:
            HotelSearchRequest(
                q="",
                check_in=tomorrow.isoformat(),
                check_out=day_after.isoformat(),
            )

        error = exc_info.value.errors()[0]
        assert error["type"] == "string_too_short"

        # Only whitespace
        with pytest.raises(ValidationError) as exc_info:
            HotelSearchRequest(
                q="   ",
                check_in=tomorrow.isoformat(),
                check_out=day_after.isoformat(),
            )

        error = exc_info.value.errors()[0]
        assert "Location query cannot be empty or only whitespace" in str(error)

    def test_location_query_validation_too_long(self) -> None:
        """Test location query validation for overly long values."""
        tomorrow = date.today() + timedelta(days=1)
        day_after = date.today() + timedelta(days=2)
        long_query = "a" * 201

        with pytest.raises(ValidationError) as exc_info:
            HotelSearchRequest(
                q=long_query,
                check_in=tomorrow.isoformat(),
                check_out=day_after.isoformat(),
            )

        error = exc_info.value.errors()[0]
        assert error["type"] == "string_too_long"

    def test_location_query_whitespace_cleanup(self) -> None:
        """Test location query whitespace is properly cleaned."""
        tomorrow = date.today() + timedelta(days=1)
        day_after = date.today() + timedelta(days=2)

        request = HotelSearchRequest(
            q="  New   York  City  ",
            check_in=tomorrow.isoformat(),
            check_out=day_after.isoformat(),
        )

        assert request.q == "New York City"

    def test_date_format_validation_invalid_format(self) -> None:
        """Test date format validation for invalid formats."""
        # Invalid date formats
        invalid_dates = [
            "2024/12/01",  # Wrong separator
            "12-01-2024",  # Wrong order
            "2024-1-1",  # Missing leading zeros
            "24-12-01",  # Two-digit year
            "2024-13-01",  # Invalid month
            "2024-12-32",  # Invalid day
            "not-a-date",  # Not a date
            "2024-02-30",  # Invalid date (Feb 30)
        ]

        for invalid_date in invalid_dates:
            with pytest.raises(ValidationError) as exc_info:
                HotelSearchRequest(
                    q="New York",
                    check_in=invalid_date,
                    check_out="2024-12-05",
                )

            errors = exc_info.value.errors()
            assert any(
                "Date must be in YYYY-MM-DD format" in str(error) or "Invalid date" in str(error) for error in errors
            ), f"Failed for {invalid_date}"

    def test_date_format_validation_valid_format(self) -> None:
        """Test date format validation for valid formats."""
        request = HotelSearchRequest(
            q="New York",
            check_in="2024-12-01",
            check_out="2024-12-05",
        )

        assert request.check_in == "2024-12-01"
        assert request.check_out == "2024-12-05"

    def test_date_order_validation_invalid(self) -> None:
        """Test date order validation for invalid date sequences."""
        # Same date
        with pytest.raises(ValidationError) as exc_info:
            HotelSearchRequest(
                q="New York",
                check_in="2024-12-01",
                check_out="2024-12-01",
            )

        error_messages = [str(error) for error in exc_info.value.errors()]
        assert any("Check-out date must be after check-in date" in msg for msg in error_messages)

        # Check-out before check-in
        with pytest.raises(ValidationError) as exc_info:
            HotelSearchRequest(
                q="New York",
                check_in="2024-12-05",
                check_out="2024-12-01",
            )

        error_messages = [str(error) for error in exc_info.value.errors()]
        assert any("Check-out date must be after check-in date" in msg for msg in error_messages)

    def test_date_order_validation_valid(self) -> None:
        """Test date order validation for valid date sequences."""
        request = HotelSearchRequest(
            q="New York",
            check_in="2024-12-01",
            check_out="2024-12-05",
        )

        assert request.check_in == "2024-12-01"
        assert request.check_out == "2024-12-05"

    def test_adults_validation_boundaries(self) -> None:
        """Test adults field boundary validation."""
        tomorrow = date.today() + timedelta(days=1)
        day_after = date.today() + timedelta(days=2)

        # Too few adults
        with pytest.raises(ValidationError) as exc_info:
            HotelSearchRequest(
                q="New York",
                check_in=tomorrow.isoformat(),
                check_out=day_after.isoformat(),
                adults=0,
            )

        error = exc_info.value.errors()[0]
        assert error["type"] == "greater_than_equal"

        # Too many adults
        with pytest.raises(ValidationError) as exc_info:
            HotelSearchRequest(
                q="New York",
                check_in=tomorrow.isoformat(),
                check_out=day_after.isoformat(),
                adults=11,
            )

        error = exc_info.value.errors()[0]
        assert error["type"] == "less_than_equal"

        # Valid boundaries
        request_min = HotelSearchRequest(
            q="New York",
            check_in=tomorrow.isoformat(),
            check_out=day_after.isoformat(),
            adults=1,
        )
        assert request_min.adults == 1

        request_max = HotelSearchRequest(
            q="New York",
            check_in=tomorrow.isoformat(),
            check_out=day_after.isoformat(),
            adults=10,
        )
        assert request_max.adults == 10

    def test_property_type_validation(self) -> None:
        """Test property type validation."""
        tomorrow = date.today() + timedelta(days=1)
        day_after = date.today() + timedelta(days=2)

        # Valid property types
        for prop_type in PropertyType:
            request = HotelSearchRequest(
                q="New York",
                check_in=tomorrow.isoformat(),
                check_out=day_after.isoformat(),
                property_type=prop_type,
            )
            assert request.property_type == prop_type

        # Invalid property type (this would fail at Pydantic level)
        with pytest.raises(ValidationError):
            HotelSearchRequest(
                q="New York",
                check_in=tomorrow.isoformat(),
                check_out=day_after.isoformat(),
                property_type="invalid_type",  # type: ignore
            )


class TestHotelPrice:
    """Test suite for HotelPrice model."""

    def test_hotel_price_all_fields(self) -> None:
        """Test HotelPrice with all fields."""
        price = HotelPrice(
            rate=150.00,
            total=750.00,
            currency="USD",
        )

        assert price.rate == 150.00
        assert price.total == 750.00
        assert price.currency == "USD"

    def test_hotel_price_optional_fields(self) -> None:
        """Test HotelPrice with optional fields as None."""
        price = HotelPrice()

        assert price.rate is None
        assert price.total is None
        assert price.currency is None


class TestHotelAmenity:
    """Test suite for HotelAmenity model."""

    def test_hotel_amenity_required_field(self) -> None:
        """Test HotelAmenity with required name field."""
        amenity = HotelAmenity(name="Free WiFi")

        assert amenity.name == "Free WiFi"
        assert amenity.icon is None

    def test_hotel_amenity_all_fields(self) -> None:
        """Test HotelAmenity with all fields."""
        amenity = HotelAmenity(
            name="Swimming Pool",
            icon="pool-icon-url",
        )

        assert amenity.name == "Swimming Pool"
        assert amenity.icon == "pool-icon-url"

    def test_hotel_amenity_name_required(self) -> None:
        """Test HotelAmenity requires name field."""
        with pytest.raises(ValidationError) as exc_info:
            HotelAmenity()  # type: ignore

        error = exc_info.value.errors()[0]
        assert error["type"] == "missing"
        assert error["loc"] == ("name",)


class TestHotelRating:
    """Test suite for HotelRating model."""

    def test_hotel_rating_all_fields(self) -> None:
        """Test HotelRating with all fields."""
        rating = HotelRating(
            rating=4.5,
            reviews_count=128,
            source="Google",
        )

        assert rating.rating == 4.5
        assert rating.reviews_count == 128
        assert rating.source == "Google"

    def test_hotel_rating_optional_fields(self) -> None:
        """Test HotelRating with optional fields as None."""
        rating = HotelRating()

        assert rating.rating is None
        assert rating.reviews_count is None
        assert rating.source is None

    def test_hotel_rating_boundaries(self) -> None:
        """Test HotelRating rating and reviews_count boundaries."""
        # Valid rating boundaries
        rating_min = HotelRating(rating=0.0)
        assert rating_min.rating == 0.0

        rating_max = HotelRating(rating=5.0)
        assert rating_max.rating == 5.0

        # Invalid rating boundaries
        with pytest.raises(ValidationError):
            HotelRating(rating=-0.1)

        with pytest.raises(ValidationError):
            HotelRating(rating=5.1)

        # Valid reviews_count boundaries
        rating_no_reviews = HotelRating(reviews_count=0)
        assert rating_no_reviews.reviews_count == 0

        # Invalid reviews_count
        with pytest.raises(ValidationError):
            HotelRating(reviews_count=-1)


class TestHotelResult:
    """Test suite for HotelResult model."""

    def test_hotel_result_minimal(self) -> None:
        """Test HotelResult with minimal required fields."""
        hotel = HotelResult(name="Grand Hotel")

        assert hotel.name == "Grand Hotel"
        assert hotel.description is None
        assert hotel.amenities == []
        assert hotel.images == []

    def test_hotel_result_full(self) -> None:
        """Test HotelResult with all fields populated."""
        amenities = [
            HotelAmenity(name="Free WiFi", icon="wifi-icon"),
            HotelAmenity(name="Pool"),
        ]

        price = HotelPrice(rate=200.0, total=1000.0, currency="USD")
        rating = HotelRating(rating=4.2, reviews_count=87, source="Google")

        hotel = HotelResult(
            name="Luxury Resort",
            description="Beautiful beachfront resort",
            link="https://example.com/hotel",
            address="123 Beach Blvd, Miami, FL",
            gps_coordinates={"latitude": 25.7617, "longitude": -80.1918},
            price=price,
            property_type="resort",
            hotel_class=5,
            rating=rating,
            amenities=amenities,
            images=["image1.jpg", "image2.jpg"],
            is_available=True,
            source_id="searchapi-123",
            thumbnail="thumb.jpg",
        )

        assert hotel.name == "Luxury Resort"
        assert hotel.description == "Beautiful beachfront resort"
        assert hotel.gps_coordinates == {"latitude": 25.7617, "longitude": -80.1918}
        assert hotel.price == price
        assert hotel.hotel_class == 5
        assert hotel.rating == rating
        assert hotel.amenities is not None and len(hotel.amenities) == 2
        assert hotel.images is not None and len(hotel.images) == 2

    def test_hotel_result_hotel_class_boundaries(self) -> None:
        """Test HotelResult hotel_class boundary validation."""
        # Valid boundaries
        hotel_min = HotelResult(name="Budget Hotel", hotel_class=1)
        assert hotel_min.hotel_class == 1

        hotel_max = HotelResult(name="Luxury Hotel", hotel_class=5)
        assert hotel_max.hotel_class == 5

        # Invalid boundaries
        with pytest.raises(ValidationError):
            HotelResult(name="Invalid Hotel", hotel_class=0)

        with pytest.raises(ValidationError):
            HotelResult(name="Invalid Hotel", hotel_class=6)

    def test_hotel_result_name_required(self) -> None:
        """Test HotelResult requires name field."""
        with pytest.raises(ValidationError) as exc_info:
            HotelResult()  # type: ignore

        error = exc_info.value.errors()[0]
        assert error["type"] == "missing"
        assert error["loc"] == ("name",)


class TestHotelSearchResponse:
    """Test suite for HotelSearchResponse model."""

    def test_hotel_search_response_empty(self) -> None:
        """Test HotelSearchResponse with default empty values."""
        response = HotelSearchResponse()

        assert response.search_metadata is None
        assert response.search_parameters is None
        assert response.search_information is None
        assert response.properties == []
        assert response.filters is None
        assert response.pagination is None
        assert response.brands == []
        assert response.location_info is None

    def test_hotel_search_response_with_results(self) -> None:
        """Test HotelSearchResponse with populated results."""
        hotels = [
            HotelResult(name="Hotel A"),
            HotelResult(name="Hotel B"),
        ]

        response = HotelSearchResponse(
            search_metadata={"id": "search-123"},
            search_parameters={"q": "New York", "check_in": "2024-12-01"},
            search_information={"total_results": 2},
            properties=hotels,
            filters={"price_range": [100, 500]},
            pagination={"page": 1, "total_pages": 1},
            brands=[{"name": "Marriott", "count": 1}],
            location_info={"city": "New York", "state": "NY"},
        )

        assert response.search_metadata == {"id": "search-123"}
        assert len(response.properties) == 2
        assert response.properties[0].name == "Hotel A"
        assert response.filters == {"price_range": [100, 500]}

    def test_hotel_search_response_complex_structure(self) -> None:
        """Test HotelSearchResponse with complex nested data."""
        complex_metadata: dict[str, Any] = {
            "request_id": "req-456",
            "timestamp": "2024-01-01T00:00:00Z",
            "processing_time_ms": 234,
        }

        response = HotelSearchResponse(
            search_metadata=complex_metadata,
            properties=[
                HotelResult(
                    name="Complex Hotel",
                    amenities=[HotelAmenity(name="Spa")],
                    price=HotelPrice(rate=300.0, currency="EUR"),
                )
            ],
        )

        assert response.search_metadata is not None and response.search_metadata["request_id"] == "req-456"
        assert response.properties[0].price is not None and response.properties[0].price.currency == "EUR"


class TestSearchAPIErrorResponse:
    """Test suite for SearchAPIErrorResponse model."""

    def test_error_response_minimal(self) -> None:
        """Test SearchAPIErrorResponse with minimal required fields."""
        error = SearchAPIErrorResponse(
            error="authentication_failed",
            message="Invalid API key provided",
        )

        assert error.error == "authentication_failed"
        assert error.message == "Invalid API key provided"
        assert error.status_code is None
        assert error.details is None
        assert error.timestamp is None
        assert error.request_id is None

    def test_error_response_full(self) -> None:
        """Test SearchAPIErrorResponse with all fields."""
        error = SearchAPIErrorResponse(
            error="rate_limit_exceeded",
            message="Too many requests. Please try again later.",
            status_code=429,
            details={"limit": 100, "window": "1h", "retry_after": 3600},
            timestamp="2024-01-01T12:00:00Z",
            request_id="req-789",
        )

        assert error.error == "rate_limit_exceeded"
        assert error.message == "Too many requests. Please try again later."
        assert error.status_code == 429
        assert error.details == {"limit": 100, "window": "1h", "retry_after": 3600}
        assert error.timestamp == "2024-01-01T12:00:00Z"
        assert error.request_id == "req-789"

    def test_error_response_required_fields(self) -> None:
        """Test SearchAPIErrorResponse requires error and message fields."""
        # Missing error
        with pytest.raises(ValidationError) as exc_info:
            SearchAPIErrorResponse(message="Test message")  # type: ignore

        error = exc_info.value.errors()[0]
        assert error["type"] == "missing"
        assert error["loc"] == ("error",)

        # Missing message
        with pytest.raises(ValidationError) as exc_info:
            SearchAPIErrorResponse(error="test_error")  # type: ignore

        error = exc_info.value.errors()[0]
        assert error["type"] == "missing"
        assert error["loc"] == ("message",)

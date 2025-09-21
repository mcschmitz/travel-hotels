"""Comprehensive tests for hotel search Pydantic models."""

from datetime import date, timedelta

import pytest
from pydantic import ValidationError

from src.app.schemas.hotel_search import (
    HotelAmenity,
    HotelSearchRequest,
    PropertyType,
)


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
        assert request.check_in == tomorrow
        assert request.check_out == day_after
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

        with pytest.raises(ValidationError):
            HotelSearchRequest(q="", check_in=tomorrow.isoformat(), check_out=day_after.isoformat())

        with pytest.raises(ValidationError):
            HotelSearchRequest(q="   ", check_in=tomorrow.isoformat(), check_out=day_after.isoformat())

    def test_location_query_validation_too_long(self) -> None:
        """Test location query validation for overly long values."""
        tomorrow = date.today() + timedelta(days=1)
        day_after = date.today() + timedelta(days=2)
        long_query = "a" * 201

        with pytest.raises(ValidationError):
            HotelSearchRequest(q=long_query, check_in=tomorrow.isoformat(), check_out=day_after.isoformat())

    def test_location_query_whitespace_cleanup(self) -> None:
        """Test location query whitespace is properly cleaned."""
        tomorrow = date.today() + timedelta(days=1)
        day_after = date.today() + timedelta(days=2)

        request = HotelSearchRequest(
            q="  New   York  City  ", check_in=tomorrow.isoformat(), check_out=day_after.isoformat()
        )

        assert request.q == "New York City"

    @pytest.mark.parametrize(
        "date_str",
        ["2024/12/01", "12-01-2024", "2024-1-1", "24-12-01", "2024-13-01", "2024-12-32", "not-a-date", "2024-02-30"],
    )
    def test_date_format_validation_invalid_format(self, date_str: str) -> None:
        """Test date format validation for invalid formats."""
        with pytest.raises(ValidationError):
            HotelSearchRequest(q="New York", check_in=date_str, check_out="2024-12-05")

    def test_date_format_validation_valid_format(self) -> None:
        """Test date format validation for valid formats."""
        tomorrow = date.today() + timedelta(days=1)
        day_after = date.today() + timedelta(days=5)

        request = HotelSearchRequest(q="New York", check_in=tomorrow.isoformat(), check_out=day_after.isoformat())

        assert request.check_in == tomorrow
        assert request.check_out == day_after

    def test_date_order_validation_invalid(self) -> None:
        """Test date order validation for invalid date sequences."""
        tomorrow = date.today() + timedelta(days=1)
        day_after = date.today() + timedelta(days=5)

        with pytest.raises(ValidationError):
            HotelSearchRequest(q="New York", check_in=tomorrow.isoformat(), check_out=tomorrow.isoformat())

        with pytest.raises(ValidationError):
            HotelSearchRequest(q="New York", check_in=day_after.isoformat(), check_out=tomorrow.isoformat())

    def test_date_order_validation_valid(self) -> None:
        """Test date order validation for valid date sequences."""
        tomorrow = date.today() + timedelta(days=1)
        day_after = date.today() + timedelta(days=5)

        request = HotelSearchRequest(q="New York", check_in=tomorrow.isoformat(), check_out=day_after.isoformat())

        assert request.check_in == tomorrow
        assert request.check_out == day_after

    def test_check_in_date_past_validation(self) -> None:
        """Test that check-in date cannot be in the past."""
        yesterday = date.today() - timedelta(days=1)
        tomorrow = date.today() + timedelta(days=1)

        with pytest.raises(ValidationError, match="Check-in date cannot be in the past"):
            HotelSearchRequest(q="New York", check_in=yesterday.isoformat(), check_out=tomorrow.isoformat())

    def test_check_in_date_today_validation(self) -> None:
        """Test that check-in date can be today."""
        today = date.today()
        tomorrow = date.today() + timedelta(days=1)

        request = HotelSearchRequest(q="New York", check_in=today.isoformat(), check_out=tomorrow.isoformat())

        assert request.check_in == today
        assert request.check_out == tomorrow


class TestHotelAmenity:
    """Test suite for HotelAmenity model."""

    def test_hotel_amenity_required_field(self) -> None:
        """Test HotelAmenity with required name field."""
        amenity = HotelAmenity(name="Free WiFi")

        assert amenity.name == "Free WiFi"
        assert amenity.icon is None

    def test_hotel_amenity_all_fields(self) -> None:
        """Test HotelAmenity with all fields."""
        amenity = HotelAmenity(name="Swimming Pool", icon="pool-icon-url")

        assert amenity.name == "Swimming Pool"
        assert amenity.icon == "pool-icon-url"

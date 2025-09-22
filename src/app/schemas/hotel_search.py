"""Pydantic models for hotel search requests and responses."""

import re
from datetime import date
from enum import Enum
from typing import Any

from pydantic import BaseModel, Field, field_validator, model_validator


class PropertyType(str, Enum):
    """Valid property types for hotel search."""

    HOTEL = "hotel"
    VACATION_RENTAL = "vacation_rental"


class HotelSearchRequest(BaseModel):
    """
    Request model for hotel search with comprehensive validation.

    This model validates search parameters for SearchAPI.io Google Hotels API,
    ensuring proper date formats, location queries, and property types.
    """

    q: str = Field(
        ...,
        min_length=1,
        max_length=200,
        description="Location search query (e.g., 'New York', 'Paris, France')",
        examples=["New York", "Paris, France", "Tokyo, Japan"],
    )
    check_in: date = Field(..., description="Check-in date in YYYY-MM-DD format", examples=["2024-12-01"])
    check_out: date = Field(..., description="Check-out date in YYYY-MM-DD format", examples=["2024-12-05"])
    property_type: PropertyType = Field(default=PropertyType.HOTEL, description="Type of property to search for")
    adults: int = Field(default=2, ge=1, le=10, description="Number of adults (1-10)")

    @model_validator(mode="after")
    def validate_dates(self) -> "HotelSearchRequest":
        """Validate date constraints: check-in >= today and check-out > check-in."""
        today = date.today()

        # Validate check-in is not in the past
        if self.check_in < today:
            raise ValueError("Check-in date cannot be in the past")

        # Validate check-out is after check-in
        if self.check_out <= self.check_in:
            raise ValueError("Check-out date must be after check-in date")

        return self

    @field_validator("q")
    @classmethod
    def validate_location_query(cls, v: str) -> str:
        """Validate and clean location query."""
        # Remove excessive whitespace and ensure it's not just whitespace
        cleaned = " ".join(v.split())
        if not cleaned:
            raise ValueError("Location query cannot be empty or only whitespace")
        return cleaned


class HotelPrice(BaseModel):
    """Hotel price information from SearchAPI.io."""

    rate: float | None = Field(None, description="Price per night")
    total: float | None = Field(None, description="Total price for the stay")
    currency: str | None = Field(None, description="Currency code (e.g., 'USD')")


class HotelAmenity(BaseModel):
    """Hotel amenity information."""

    name: str = Field(..., description="Amenity name")
    icon: str | None = Field(None, description="Amenity icon URL or identifier")


class HotelRating(BaseModel):
    """Hotel rating and review information."""

    rating: float | None = Field(None, ge=0, le=5, description="Hotel rating (0-5)")
    reviews_count: int | None = Field(None, ge=0, description="Number of reviews")
    source: str | None = Field(None, description="Rating source (e.g., 'Google')")


class HotelResult(BaseModel):
    """
    Individual hotel result from SearchAPI.io response.

    Represents a single hotel listing with all available information
    including location, pricing, amenities, and ratings.
    """

    name: str = Field(..., description="Hotel name")
    description: str | None = Field(None, description="Hotel description")
    link: str | None = Field(None, description="Link to hotel booking page")

    address: str | None = Field(None, description="Hotel address")
    gps_coordinates: dict[str, float] | None = Field(
        None, description="GPS coordinates with 'latitude' and 'longitude' keys"
    )

    price: HotelPrice | None = Field(None, description="Price information")

    property_type: str | None = Field(None, description="Property type")
    hotel_class: int | None = Field(None, ge=1, le=5, description="Hotel star rating (1-5)")

    rating: float | None = Field(None, ge=0, le=5, description="Hotel rating (0-5)")

    amenities: list[str] | None = Field(default_factory=list, description="List of hotel amenities")

    images: list[str | dict[str, Any]] | None = Field(
        default_factory=list, description="List of hotel image URLs or image objects"
    )

    is_available: bool | None = Field(None, description="Whether the hotel is available")

    source_id: str | None = Field(None, description="Source identifier from SearchAPI.io")
    thumbnail: str | None = Field(None, description="Thumbnail image URL")

    @field_validator("hotel_class", mode="before")
    @classmethod
    def parse_hotel_class(cls, v: Any) -> int | None:
        """Parse hotel class from string format like '3-star hotel' to integer."""
        if v is None:
            return None
        if isinstance(v, int):
            return v
        if isinstance(v, str):
            match = re.search(r"(\d+)", v)
            if match:
                return int(match.group(1))
        return None


class HotelSearchResponse(BaseModel):
    """
    Complete response model for hotel search from SearchAPI.io.

    Contains search metadata, results, and pagination information
    following SearchAPI.io response structure.
    """

    search_metadata: dict[str, Any] | None = Field(None, description="Search metadata from SearchAPI.io")
    search_parameters: dict[str, Any] | None = Field(None, description="Search parameters used in the request")
    search_information: dict[str, Any] | None = Field(None, description="Search information and statistics")
    properties: list[HotelResult] = Field(default_factory=list, description="List of hotel results")

    # Pagination and filtering information
    filters: dict[str, Any] | None = Field(None, description="Available filters for refining search")
    pagination: dict[str, Any] | None = Field(None, description="Pagination information")

    # Location and brand information
    brands: list[dict[str, Any]] | None = Field(default_factory=list, description="Available hotel brands")
    location_info: dict[str, Any] | None = Field(None, description="Location information for the search")

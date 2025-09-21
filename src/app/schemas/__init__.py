"""Pydantic schemas for request and response models."""

from .hotel_search import (
    HotelResult,
    HotelSearchRequest,
    HotelSearchResponse,
    SearchAPIErrorResponse,
)

__all__ = [
    "HotelSearchRequest",
    "HotelSearchResponse",
    "HotelResult",
    "SearchAPIErrorResponse",
]

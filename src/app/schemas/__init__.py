"""Pydantic schemas for request and response models."""

from src.app.schemas.hotel_search import HotelResult, HotelSearchRequest, HotelSearchResponse

__all__ = ["HotelSearchRequest", "HotelSearchResponse", "HotelResult"]

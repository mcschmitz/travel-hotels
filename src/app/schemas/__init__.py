"""Pydantic schemas for request and response models."""

from src.app.schemas.hotel_search import HotelResult, HotelSearchRequest, HotelSearchResponse, SearchAPIErrorResponse

__all__ = ["HotelSearchRequest", "HotelSearchResponse", "HotelResult", "SearchAPIErrorResponse"]

"""Hotel service for coordinating business logic and external API calls."""

import logging
from typing import Any

from src.app.schemas.hotel_search import HotelSearchRequest, HotelSearchResponse
from src.app.services.searchapi.client import SearchAPIClient, SearchAPIError
from src.core.config import SearchAPISettings

logger = logging.getLogger(__name__)


class HotelService:
    """
    Business logic service for hotel search operations.

    Coordinates between the API layer and external SearchAPI.io service,
    handling request transformation, response processing, and error management.
    """

    def __init__(self, searchapi_client: SearchAPIClient) -> None:
        """
        Initialize hotel service with dependencies.

        Args:
            searchapi_client: SearchAPI.io HTTP client for hotel search

        """
        self._searchapi_client = searchapi_client

    async def search_hotels(self, request: HotelSearchRequest) -> HotelSearchResponse:
        """
        Search for hotels using the provided search criteria.

        This method coordinates the hotel search operation by:
        1. Processing and validating the search request
        2. Transforming the request for SearchAPI.io format
        3. Making the external API call
        4. Processing and transforming the response
        5. Handling any errors that occur

        Args:
            request: Hotel search parameters with validation

        Returns:
            HotelSearchResponse: Processed search results with hotel listings

        Raises:
            SearchAPIError: When external API call fails
            ValueError: When request parameters are invalid

        """
        logger.info(
            "Starting hotel search",
            extra={
                "location": request.q,
                "check_in": request.check_in.isoformat(),
                "check_out": request.check_out.isoformat(),
                "property_type": request.property_type.value,
                "adults": request.adults,
            },
        )

        try:
            # Transform Pydantic model to SearchAPI client format
            searchapi_response = await self._searchapi_client.search_hotels(
                location=request.q,
                check_in_date=request.check_in.isoformat(),
                check_out_date=request.check_out.isoformat(),
                property_type=request.property_type.value,
                adults=request.adults,
            )

            # Transform SearchAPI.io response to our standardized format
            response = self._transform_searchapi_response(searchapi_response)

            logger.info(
                "Hotel search completed successfully",
                extra={
                    "location": request.q,
                    "results_count": len(response.properties),
                },
            )

            return response

        except SearchAPIError as e:
            logger.error(
                "SearchAPI.io request failed",
                extra={
                    "location": request.q,
                    "error": str(e),
                    "error_type": type(e).__name__,
                },
            )
            raise

        except Exception as e:
            logger.error(
                "Unexpected error during hotel search",
                extra={
                    "location": request.q,
                    "error": str(e),
                    "error_type": type(e).__name__,
                },
            )
            raise

    def _transform_searchapi_response(self, raw_response: dict[str, Any]) -> HotelSearchResponse:
        """
        Transform raw SearchAPI.io response to our standardized response format.

        Args:
            raw_response: Raw JSON response from SearchAPI.io

        Returns:
            HotelSearchResponse: Standardized response format

        """
        # For now, we pass through the raw response structure
        # This allows us to maintain compatibility with SearchAPI.io format
        # while providing type safety through our Pydantic models

        # Extract properties/hotels list safely
        properties = raw_response.get("properties", [])

        # Create response with validation
        return HotelSearchResponse(
            search_metadata=raw_response.get("search_metadata"),
            search_parameters=raw_response.get("search_parameters"),
            search_information=raw_response.get("search_information"),
            properties=properties,  # Will be validated by Pydantic
            filters=raw_response.get("filters"),
            pagination=raw_response.get("pagination"),
            brands=raw_response.get("brands", []),
            location_info=raw_response.get("location_info"),
        )


def create_hotel_service(settings: SearchAPISettings) -> HotelService:
    """
    Create a HotelService instance.

    Args:
        settings: SearchAPI.io configuration settings

    Returns:
        HotelService: Configured service instance

    """
    searchapi_client = SearchAPIClient(settings)
    return HotelService(searchapi_client)

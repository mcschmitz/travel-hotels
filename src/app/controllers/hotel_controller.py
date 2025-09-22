"""Hotel controller for handling HTTP request/response logic."""

from fastapi import HTTPException, status
from loguru import logger
from pydantic import ValidationError

from src.app.schemas.hotel_search import HotelSearchRequest, HotelSearchResponse
from src.app.services.factory import ServiceFactory
from src.app.services.hotel_service import HotelService
from src.app.services.searchapi.exceptions import (
    SearchAPIAuthenticationError,
    SearchAPIError,
    SearchAPIRateLimitError,
    SearchAPITimeoutError,
)


class HotelController:
    """
    Controller for hotel search operations.

    Handles HTTP request/response logic, coordinates with the hotel service layer,
    and manages error handling with appropriate HTTP status codes.
    """

    def __init__(self, hotel_service: HotelService | None = None) -> None:
        """Initialize hotel controller."""
        self.hotel_service = hotel_service or ServiceFactory.get_hotel_service()

    async def search_hotels(self, request: HotelSearchRequest) -> HotelSearchResponse:
        """
        Handle hotel search requests from API endpoints.

        This method processes hotel search requests by:
        1. Validating the incoming request (handled by Pydantic)
        2. Delegating to the hotel service for business logic
        3. Handling exceptions and converting to appropriate HTTP errors
        4. Returning the formatted response

        Args:
            request: Validated hotel search parameters

        Returns:
            HotelSearchResponse: Search results with hotel listings

        Raises:
            HTTPException: For various error conditions with appropriate status codes
                - 400: Invalid request parameters
                - 401: Authentication errors (invalid API key)
                - 429: Rate limiting errors
                - 502: External service errors
                - 504: Timeout errors

        """
        logger.info(
            "Processing hotel search request",
            extra={
                "location": request.q,
                "check_in": request.check_in.isoformat(),
                "check_out": request.check_out.isoformat(),
                "adults": request.adults,
                "property_type": request.property_type.value,
            },
        )

        try:
            response = await self.hotel_service.search_hotels(request)
            logger.info(
                "Hotel search completed successfully",
                extra={"location": request.q, "results_count": len(response.properties)},
            )
            return response

        except ValidationError as e:
            logger.warning("Invalid request parameters", extra={"location": request.q, "validation_errors": str(e)})
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail=f"Invalid request parameters: {e}"
            ) from e

        except SearchAPIAuthenticationError as e:
            logger.error("SearchAPI authentication failed", extra={"location": request.q, "error": str(e)})
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Authentication failed with external hotel search service",
            ) from e

        except SearchAPIRateLimitError as e:
            logger.warning("SearchAPI rate limit exceeded", extra={"location": request.q, "error": str(e)})
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS, detail="Rate limit exceeded. Please try again later."
            ) from e

        except SearchAPITimeoutError as e:
            logger.error("SearchAPI request timed out", extra={"location": request.q, "error": str(e)})
            raise HTTPException(
                status_code=status.HTTP_504_GATEWAY_TIMEOUT,
                detail="Hotel search service request timed out. Please try again.",
            ) from e

        except SearchAPIError as e:
            logger.error(
                "SearchAPI service error",
                extra={"location": request.q, "error": str(e), "error_type": type(e).__name__},
            )
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY, detail="External hotel search service is currently unavailable"
            ) from e

        except Exception as e:
            logger.error(
                "Unexpected error during hotel search",
                extra={"location": request.q, "error": str(e), "error_type": type(e).__name__},
            )
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="An unexpected error occurred. Please try again later.",
            ) from e

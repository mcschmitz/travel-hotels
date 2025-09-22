"""Hotels API router for hotel search and management."""

from datetime import date
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query

from src.api.dependencies.controllers import get_hotel_controller
from src.app.controllers.hotel_controller import HotelController
from src.app.schemas.hotel_search import HotelSearchRequest, HotelSearchResponse, PropertyType

router = APIRouter(prefix="/api/v1/hotels", tags=["hotels"])


@router.get("/search", response_model=HotelSearchResponse)
async def search_hotels(
    q: Annotated[
        str,
        Query(
            min_length=1,
            max_length=200,
            description="Location search query (e.g., 'New York', 'Paris, France')",
            examples=["New York", "Paris, France", "Tokyo, Japan"],
        ),
    ],
    check_in: Annotated[date, Query(description="Check-in date in YYYY-MM-DD format", examples=["2024-12-01"])],
    check_out: Annotated[date, Query(description="Check-out date in YYYY-MM-DD format", examples=["2024-12-05"])],
    property_type: Annotated[
        PropertyType,
        Query(
            description="Type of property to search for", examples=[PropertyType.HOTEL, PropertyType.VACATION_RENTAL]
        ),
    ] = PropertyType.HOTEL,
    adults: Annotated[int, Query(ge=1, le=10, description="Number of adults (1-10)", examples=[2, 4])] = 2,
    controller: HotelController = Depends(get_hotel_controller),
) -> HotelSearchResponse:
    """
    Search for hotels based on location, dates, and preferences.

    This endpoint provides comprehensive hotel search functionality using the SearchAPI.io Google Hotels API. It
    validates search parameters, handles various error conditions, and returns structured hotel data.

    Args:
        q: Location search query (required)
        check_in: Check-in date in YYYY-MM-DD format (required)
        check_out: Check-out date in YYYY-MM-DD format (required)
        property_type: Type of property to search for (optional, default: hotel)
        adults: Number of adults (optional, default: 2, range: 1-10)
        controller: Hotel controller dependency

    Returns:
        HotelSearchResponse: Search results with hotel listings, metadata, and filters

    Raises:
        HTTPException:
            - 400: Invalid request parameters (validation errors)
            - 401: Authentication errors with external service
            - 429: Rate limiting errors
            - 502: External service errors
            - 504: Request timeout errors
            - 500: Unexpected server errors

    Example:
        GET /api/v1/hotels/search?q=New York&check_in=2024-12-01&check_out=2024-12-05&adults=2

        Response:
        {
            "properties": [
                {
                    "name": "Hotel Example",
                    "address": "123 Main St, New York, NY",
                    "price": {
                        "rate": 250.00,
                        "total": 1000.00,
                        "currency": "USD"
                    },
                    "rating": {
                        "rating": 4.5,
                        "reviews_count": 1250,
                        "source": "Google"
                    }
                }
            ],
            "search_metadata": {...},
            "search_parameters": {...}
        }

    """
    try:
        request = HotelSearchRequest(
            q=q,
            check_in=check_in,
            check_out=check_out,
            property_type=property_type,
            adults=adults,
        )
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e)) from e
    return await controller.search_hotels(request)

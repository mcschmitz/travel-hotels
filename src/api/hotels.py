"""Hotels API router for hotel search and management."""

from fastapi import APIRouter

router = APIRouter(prefix="/api/v1/hotels", tags=["hotels"])


@router.get("/health")
async def hotels_health() -> dict[str, str]:
    """
    Hotel service health check endpoint.

    Returns:
        dict[str, str]: Health status of the hotels service

    Example:
        {"status": "hotels service healthy"}

    """
    return {"status": "hotels service healthy"}

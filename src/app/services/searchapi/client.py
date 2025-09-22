"""SearchAPI.io HTTP client for hotel search functionality."""

from typing import Any

import httpx
from pydantic import ValidationError

from src.app.services.searchapi.exceptions import (
    SearchAPIAuthenticationError,
    SearchAPIError,
    SearchAPIRateLimitError,
    SearchAPITimeoutError,
)
from src.core.config import SearchAPISettings


class SearchAPIClient:
    """
    Async HTTP client for SearchAPI.io Google Hotels API.

    This client handles authentication, request formation, and error handling
    for SearchAPI.io hotel search requests. It uses httpx for async HTTP
    communication and implements proper resource management.

    The client formats requests specifically for SearchAPI.io's Google Hotels
    engine and handles common API errors with appropriate exceptions.
    """

    def __init__(self, settings: SearchAPISettings) -> None:
        """
        Initialize SearchAPI client with configuration settings.

        Args:
            settings: SearchAPI configuration including API key, base URL, and timeouts

        """
        self._settings = settings or SearchAPISettings()
        self._client: httpx.AsyncClient | None = None

    async def _ensure_client(self) -> None:
        """Ensure HTTP client is initialized."""
        if self._client is None:
            timeout = httpx.Timeout(self._settings.timeout)
            self._client = httpx.AsyncClient(
                timeout=timeout,
                follow_redirects=True,
                limits=httpx.Limits(max_keepalive_connections=5, max_connections=10),
            )

    async def close(self) -> None:
        """Close the HTTP client and clean up resources."""
        if self._client is not None:
            await self._client.aclose()
            self._client = None

    async def search_hotels(
        self,
        location: str,
        check_in_date: str,
        check_out_date: str,
        property_type: str = "hotel",
        adults: int = 2,
    ) -> dict[str, Any]:
        """
        Search hotels using SearchAPI.io Google Hotels engine.

        Args:
            location: Location search query (e.g., "New York", "Paris, France")
            check_in_date: Check-in date in YYYY-MM-DD format
            check_out_date: Check-out date in YYYY-MM-DD format
            property_type: Type of property ("hotel" or "vacation_rental")
            adults: Number of adults (default: 2)

        Returns:
            dict[str, Any]: Raw SearchAPI.io response data

        Raises:
            SearchAPIAuthenticationError: When API key is invalid
            SearchAPIRateLimitError: When rate limit is exceeded
            SearchAPITimeoutError: When request times out
            SearchAPIError: For other API-related errors
            ValidationError: When request parameters are invalid

        """
        await self._ensure_client()

        if not self._client:
            raise SearchAPIError("HTTP client not initialized")
        params = {
            "engine": "google_hotels",
            "q": location,
            "check_in_date": check_in_date,
            "check_out_date": check_out_date,
            "property_type": property_type,
            "adults": str(adults),
            "api_key": self._settings.api_key.get_secret_value(),
        }

        url = f"{self._settings.base_url}/search"

        try:
            response = await self._client.get(url, params=params)

            if response.status_code == 401:
                raise SearchAPIAuthenticationError("Invalid SearchAPI.io API key")
            elif response.status_code == 429:
                raise SearchAPIRateLimitError("SearchAPI.io rate limit exceeded")
            elif response.status_code >= 400:
                error_detail = response.text[:200] if response.text else "Unknown error"
                raise SearchAPIError(f"SearchAPI.io request failed with status {response.status_code}: {error_detail}")

            response.raise_for_status()

            return response.json()

        except httpx.TimeoutException as e:
            raise SearchAPITimeoutError(f"SearchAPI.io request timed out after {self._settings.timeout}s") from e
        except httpx.HTTPError as e:
            raise SearchAPIError(f"HTTP error during SearchAPI.io request: {e}") from e
        except ValidationError as e:
            raise ValidationError(f"Invalid request parameters: {e}") from e

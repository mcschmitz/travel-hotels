"""Persistence layer factory for managing external service clients."""

from src.core.config import SearchAPISettings
from src.core.persistence.searchapi_client import SearchAPIClient


class PersistenceFactory:
    """
    Factory class for creating and managing persistence layer clients.

    This factory follows the singleton pattern to ensure consistent
    configuration and resource management across the application.
    It manages external service clients including SearchAPI.io.
    """

    _instance: "PersistenceFactory | None" = None
    _searchapi_client: SearchAPIClient | None = None
    _searchapi_settings: SearchAPISettings | None = None

    def __new__(cls) -> "PersistenceFactory":
        """Ensure singleton instance."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def configure_searchapi(self, settings: SearchAPISettings) -> None:
        """
        Configure SearchAPI.io client settings.

        Args:
            settings: SearchAPI configuration including API key and connection settings

        """
        self._searchapi_settings = settings
        # Reset client to ensure new settings are applied
        if self._searchapi_client is not None:
            self._searchapi_client = None

    def get_searchapi_client(self) -> SearchAPIClient:
        """
        Get configured SearchAPI.io client instance.

        Returns:
            SearchAPIClient: Configured SearchAPI.io HTTP client

        Raises:
            RuntimeError: When SearchAPI settings have not been configured

        """
        if self._searchapi_settings is None:
            raise RuntimeError("SearchAPI settings not configured. Call configure_searchapi() first.")

        if self._searchapi_client is None:
            self._searchapi_client = SearchAPIClient(self._searchapi_settings)

        return self._searchapi_client

    async def cleanup(self) -> None:
        """
        Clean up all managed clients and resources.

        This method should be called during application shutdown
        to ensure proper cleanup of HTTP clients and connections.
        """
        if self._searchapi_client is not None:
            await self._searchapi_client.close()
            self._searchapi_client = None

    def reset(self) -> None:
        """
        Reset factory state for testing purposes.

        This method is primarily intended for use in tests
        to ensure clean state between test runs.
        """
        if self._searchapi_client is not None:
            # Note: In production, this should include async cleanup
            # For testing, we assume cleanup is handled by test fixtures
            self._searchapi_client = None
        self._searchapi_settings = None


# Global factory instance
persistence_factory = PersistenceFactory()

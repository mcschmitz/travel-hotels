from src.app.services.hotel_service import HotelService
from src.app.services.searchapi.client import SearchAPIClient
from src.core.config import SearchAPISettings


class ServiceFactory:
    """
    Factory class for creating and managing service layer clients.

    This factory follows the singleton pattern to ensure consistent
    configuration and resource management across the application.
    It manages external service clients including SearchAPI.io.
    """

    _searchapi_client: SearchAPIClient | None = None
    _hotel_service: HotelService | None = None

    @classmethod
    def get_searchapi_client(cls, settings: SearchAPISettings | None = None) -> SearchAPIClient:
        """
        Get configured SearchAPI.io client instance.

        Returns:
            SearchAPIClient: Configured SearchAPI.io HTTP client

        Raises:
            RuntimeError: When SearchAPI settings have not been configured

        """
        if cls._searchapi_client is None:
            cls._searchapi_client = SearchAPIClient(settings=SearchAPISettings() if settings is None else settings)

        return cls._searchapi_client

    @classmethod
    def get_hotel_service(cls, settings: SearchAPISettings | None = None) -> HotelService:
        """
        Get configured hotel service instance.

        Returns:
            HotelService: Configured hotel business logic service

        """
        if cls._hotel_service is None:
            searchapi_client = cls.get_searchapi_client(settings)
            cls._hotel_service = HotelService(searchapi_client)

        return cls._hotel_service

    @classmethod
    async def cleanup(cls) -> None:
        """
        Clean up all managed clients and resources.

        This method should be called during application shutdown
        to ensure proper cleanup of HTTP clients and connections.
        """
        if cls._searchapi_client is not None:
            await cls._searchapi_client.close()
            cls._searchapi_client = None

        cls._hotel_service = None

    @classmethod
    def reset(cls) -> None:
        """
        Reset factory state for testing purposes.

        This method is primarily intended for use in tests
        to ensure clean state between test runs.
        """
        cls._searchapi_client = None
        cls._hotel_service = None

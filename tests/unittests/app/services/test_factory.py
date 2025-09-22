"""Tests for service factory."""

from src.app.services.factory import ServiceFactory
from src.app.services.hotel_service import HotelService
from src.app.services.searchapi.client import SearchAPIClient
from src.core.config import SearchAPISettings


class TestServiceFactory:
    """Test suite for ServiceFactory."""

    def teardown_method(self) -> None:
        """Reset factory state after each test."""
        ServiceFactory.reset()

    def test_get_hotel_service_creates_instance(self) -> None:
        """Test that factory creates hotel service instance."""
        settings = SearchAPISettings(api_key="test-key")

        service = ServiceFactory.get_hotel_service(settings)

        assert isinstance(service, HotelService)
        assert service is not None

    def test_get_hotel_service_singleton_behavior(self) -> None:
        """Test that factory returns same instance on subsequent calls."""
        settings = SearchAPISettings(api_key="test-key")

        service1 = ServiceFactory.get_hotel_service(settings)
        service2 = ServiceFactory.get_hotel_service(settings)

        assert service1 is service2

    def test_get_searchapi_client_creates_instance(self) -> None:
        """Test that factory creates SearchAPI client instance."""
        settings = SearchAPISettings(api_key="test-key")

        client = ServiceFactory.get_searchapi_client(settings)

        assert isinstance(client, SearchAPIClient)
        assert client is not None

    def test_get_searchapi_client_singleton_behavior(self) -> None:
        """Test that factory returns same client instance on subsequent calls."""
        settings = SearchAPISettings(api_key="test-key")

        client1 = ServiceFactory.get_searchapi_client(settings)
        client2 = ServiceFactory.get_searchapi_client(settings)

        assert client1 is client2

    def test_hotel_service_uses_same_searchapi_client(self) -> None:
        """Test that hotel service uses the same SearchAPI client from factory."""
        settings = SearchAPISettings(api_key="test-key")
        direct_client = ServiceFactory.get_searchapi_client(settings)
        hotel_service = ServiceFactory.get_hotel_service(settings)
        assert hotel_service._searchapi_client is direct_client

    async def test_cleanup_resets_instances(self) -> None:
        """Test that cleanup properly resets factory state."""
        settings = SearchAPISettings(api_key="test-key")

        ServiceFactory.get_hotel_service(settings)
        ServiceFactory.get_searchapi_client(settings)

        await ServiceFactory.cleanup()

        assert ServiceFactory._hotel_service is None
        assert ServiceFactory._searchapi_client is None

    def test_reset_clears_instances(self) -> None:
        """Test that reset clears all instances."""
        settings = SearchAPISettings(api_key="test-key")

        ServiceFactory.get_hotel_service(settings)
        ServiceFactory.get_searchapi_client(settings)

        ServiceFactory.reset()

        assert ServiceFactory._hotel_service is None
        assert ServiceFactory._searchapi_client is None

    def test_factory_creates_new_instances_after_reset(self) -> None:
        """Test that factory creates new instances after reset."""
        settings = SearchAPISettings(api_key="test-key")

        original_service = ServiceFactory.get_hotel_service(settings)
        original_client = ServiceFactory.get_searchapi_client(settings)

        ServiceFactory.reset()
        new_service = ServiceFactory.get_hotel_service(settings)
        new_client = ServiceFactory.get_searchapi_client(settings)

        assert new_service is not original_service
        assert new_client is not original_client

"""Tests for persistence factory."""

from unittest.mock import patch

import pytest

from src.app.services.factory import ServiceFactory
from src.app.services.searchapi.client import SearchAPIClient
from src.core.config import SearchAPISettings


class TestPersistenceFactory:
    """Test suite for PersistenceFactory."""

    @pytest.fixture(autouse=True)
    def reset_factory(self) -> None:
        """Reset factory state before each test."""
        ServiceFactory.reset()
        ServiceFactory._searchapi_client = None

    def test_get_searchapi_client_with_configuration(self) -> None:
        """Test getting SearchAPI client with proper configuration."""
        factory = ServiceFactory()
        settings = SearchAPISettings(api_key="test-key")

        factory.get_searchapi_client(settings)
        client = ServiceFactory.get_searchapi_client()

        assert isinstance(client, SearchAPIClient)
        assert client._settings is settings

    def test_get_searchapi_client_returns_same_instance(self) -> None:
        """Test that multiple calls return the same client instance."""
        factory = ServiceFactory()
        settings = SearchAPISettings(api_key="test-key")

        factory.get_searchapi_client(settings)
        client1 = ServiceFactory.get_searchapi_client()
        client2 = ServiceFactory.get_searchapi_client()

        assert client1 is client2

    def test_reconfigure_searchapi_resets_client(self) -> None:
        """Test that reconfiguring SearchAPI settings resets the client."""
        factory = ServiceFactory()
        settings1 = SearchAPISettings(api_key="test-key-1")
        settings2 = SearchAPISettings(api_key="test-key-2")

        # Initial configuration and client
        factory.get_searchapi_client(settings1)
        client1 = ServiceFactory.get_searchapi_client()

        # Reconfigure with new settings
        factory.get_searchapi_client(settings2)
        client2 = ServiceFactory.get_searchapi_client()

        # Should be a new client instance with new settings
        assert client1 is not client2
        assert client2._settings is settings2

    async def test_cleanup_with_no_clients(self) -> None:
        """Test cleanup when no clients have been created."""
        factory = ServiceFactory()

        # Should not raise any errors
        await factory.cleanup()

    async def test_cleanup_with_searchapi_client(self) -> None:
        """Test cleanup properly closes SearchAPI client."""
        factory = ServiceFactory()
        settings = SearchAPISettings(api_key="test-key")

        factory.get_searchapi_client(settings)
        client = ServiceFactory.get_searchapi_client()

        # Mock the close method to verify it's called
        close_called = False

        async def mock_close() -> None:
            nonlocal close_called
            close_called = True

        # Use patch instead of direct assignment to avoid mypy issues
        with patch.object(client, "close", side_effect=mock_close):
            await factory.cleanup()

        assert close_called
        assert factory._searchapi_client is None

    def test_reset_clears_all_state(self) -> None:
        """Test that reset clears all factory state."""
        factory = ServiceFactory()
        settings = SearchAPISettings(api_key="test-key")

        # Set up some state
        factory.get_searchapi_client(settings)
        ServiceFactory.get_searchapi_client()

        assert factory._searchapi_client is not None

        # Reset should clear everything
        factory.reset()

        assert factory._searchapi_client is None

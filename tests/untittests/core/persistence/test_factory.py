"""Tests for persistence factory."""

from unittest.mock import patch

import pytest

from src.core.config import SearchAPISettings
from src.core.persistence.factory import PersistenceFactory, persistence_factory
from src.core.persistence.searchapi_client import SearchAPIClient


class TestPersistenceFactory:
    """Test suite for PersistenceFactory."""

    @pytest.fixture(autouse=True)
    def reset_factory(self) -> None:
        """Reset factory state before each test."""
        # Reset the global factory instance
        persistence_factory.reset()
        # Reset class-level singleton
        PersistenceFactory._instance = None

    def test_singleton_pattern(self) -> None:
        """Test that PersistenceFactory follows singleton pattern."""
        factory1 = PersistenceFactory()
        factory2 = PersistenceFactory()

        assert factory1 is factory2
        assert id(factory1) == id(factory2)

    def test_global_factory_instance(self) -> None:
        """Test that global factory instance is available."""
        assert isinstance(persistence_factory, PersistenceFactory)

    def test_configure_searchapi_settings(self) -> None:
        """Test configuring SearchAPI settings."""
        factory = PersistenceFactory()
        settings = SearchAPISettings(api_key="test-key")

        factory.configure_searchapi(settings)

        assert factory._searchapi_settings is settings

    def test_get_searchapi_client_without_configuration_raises_error(self) -> None:
        """Test that getting SearchAPI client without configuration raises error."""
        factory = PersistenceFactory()

        with pytest.raises(RuntimeError) as exc_info:
            factory.get_searchapi_client()

        assert "SearchAPI settings not configured" in str(exc_info.value)
        assert "Call configure_searchapi() first" in str(exc_info.value)

    def test_get_searchapi_client_with_configuration(self) -> None:
        """Test getting SearchAPI client with proper configuration."""
        factory = PersistenceFactory()
        settings = SearchAPISettings(api_key="test-key")

        factory.configure_searchapi(settings)
        client = factory.get_searchapi_client()

        assert isinstance(client, SearchAPIClient)
        assert client._settings is settings

    def test_get_searchapi_client_returns_same_instance(self) -> None:
        """Test that multiple calls return the same client instance."""
        factory = PersistenceFactory()
        settings = SearchAPISettings(api_key="test-key")

        factory.configure_searchapi(settings)
        client1 = factory.get_searchapi_client()
        client2 = factory.get_searchapi_client()

        assert client1 is client2

    def test_reconfigure_searchapi_resets_client(self) -> None:
        """Test that reconfiguring SearchAPI settings resets the client."""
        factory = PersistenceFactory()
        settings1 = SearchAPISettings(api_key="test-key-1")
        settings2 = SearchAPISettings(api_key="test-key-2")

        # Initial configuration and client
        factory.configure_searchapi(settings1)
        client1 = factory.get_searchapi_client()

        # Reconfigure with new settings
        factory.configure_searchapi(settings2)
        client2 = factory.get_searchapi_client()

        # Should be a new client instance with new settings
        assert client1 is not client2
        assert client2._settings is settings2

    async def test_cleanup_with_no_clients(self) -> None:
        """Test cleanup when no clients have been created."""
        factory = PersistenceFactory()

        # Should not raise any errors
        await factory.cleanup()

    async def test_cleanup_with_searchapi_client(self) -> None:
        """Test cleanup properly closes SearchAPI client."""
        factory = PersistenceFactory()
        settings = SearchAPISettings(api_key="test-key")

        factory.configure_searchapi(settings)
        client = factory.get_searchapi_client()

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
        factory = PersistenceFactory()
        settings = SearchAPISettings(api_key="test-key")

        # Set up some state
        factory.configure_searchapi(settings)
        factory.get_searchapi_client()

        assert factory._searchapi_settings is not None
        assert factory._searchapi_client is not None

        # Reset should clear everything
        factory.reset()

        assert factory._searchapi_settings is None
        assert factory._searchapi_client is None

    def test_reset_allows_reconfiguration(self) -> None:
        """Test that reset allows fresh configuration."""
        factory = PersistenceFactory()
        settings1 = SearchAPISettings(api_key="test-key-1")
        settings2 = SearchAPISettings(api_key="test-key-2")

        # Initial setup
        factory.configure_searchapi(settings1)
        client1 = factory.get_searchapi_client()

        # Reset and reconfigure
        factory.reset()
        factory.configure_searchapi(settings2)
        client2 = factory.get_searchapi_client()

        assert client1 is not client2
        assert client2._settings is settings2

    def test_factory_state_isolation_between_instances(self) -> None:
        """Test that singleton properly maintains state across references."""
        factory1 = PersistenceFactory()
        factory2 = PersistenceFactory()

        settings = SearchAPISettings(api_key="test-key")
        factory1.configure_searchapi(settings)

        # Both references should see the same configuration
        assert factory2._searchapi_settings is settings

        client1 = factory1.get_searchapi_client()
        client2 = factory2.get_searchapi_client()

        # Should return the same client instance
        assert client1 is client2

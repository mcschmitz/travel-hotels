"""Tests for configuration management."""

import pytest
from pydantic import ValidationError

from src.core.config import SearchAPISettings, ServerSettings


class TestServerSettings:
    """Test suite for ServerSettings configuration class."""

    def test_host_validation_invalid(self) -> None:
        """Test that invalid hosts raise validation errors."""
        with pytest.raises(ValidationError) as exc_info:
            ServerSettings(host="invalid-host-@#$")

        error = exc_info.value.errors()[0]
        assert "Invalid host" in str(error["ctx"]["error"])


class TestSearchAPISettings:
    """Test suite for SearchAPISettings configuration class."""

    def test_api_key_required(self) -> None:
        """Test that API key is required."""
        with pytest.raises(ValidationError) as exc_info:
            SearchAPISettings()

        error = exc_info.value.errors()[0]
        assert error["type"] == "missing"
        assert error["loc"] == ("api_key",)

    def test_timeout_validation_boundaries(self) -> None:
        """Test timeout boundary validation."""
        # Test minimum boundary
        with pytest.raises(ValidationError):
            SearchAPISettings(api_key="test-key", timeout=0)

        # Test maximum boundary
        with pytest.raises(ValidationError):
            SearchAPISettings(api_key="test-key", timeout=301)

        # Test valid boundaries
        settings = SearchAPISettings(api_key="test-key", timeout=1)
        assert settings.timeout == 1

        settings = SearchAPISettings(api_key="test-key", timeout=300)
        assert settings.timeout == 300

    def test_max_retries_validation_boundaries(self) -> None:
        """Test max_retries boundary validation."""
        # Test maximum boundary
        with pytest.raises(ValidationError):
            SearchAPISettings(api_key="test-key", max_retries=11)

        # Test valid boundaries
        settings = SearchAPISettings(api_key="test-key", max_retries=0)
        assert settings.max_retries == 0

        settings = SearchAPISettings(api_key="test-key", max_retries=10)
        assert settings.max_retries == 10

    def test_api_key_secret_handling(self) -> None:
        """Test that API key is handled as a secret."""
        settings = SearchAPISettings(api_key="secret-key")

        # API key should be wrapped in SecretStr
        assert hasattr(settings.api_key, "get_secret_value")
        assert settings.api_key.get_secret_value() == "secret-key"

        # String representation should not expose the secret
        settings_str = str(settings)
        assert "secret-key" not in settings_str
        assert "**********" in settings_str

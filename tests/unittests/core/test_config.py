"""Tests for configuration management."""

import pytest
from pydantic import ValidationError

from src.core.config import SearchAPISettings, ServerSettings


class TestServerSettings:
    """Test suite for ServerSettings configuration class."""

    def test_host_validation_invalid(self) -> None:
        """Test that invalid hosts raise validation errors."""
        with pytest.raises(ValidationError):
            ServerSettings(host="invalid-host-@#$")


class TestSearchAPISettings:
    """Test suite for SearchAPISettings configuration class."""

    def test_api_key_required(self) -> None:
        """Test that API key is required."""
        with pytest.raises(ValidationError):
            SearchAPISettings()

    def test_api_key_secret_handling(self) -> None:
        """Test that API key is handled as a secret."""
        settings = SearchAPISettings(api_key="secret-key")

        assert hasattr(settings.api_key, "get_secret_value")
        assert settings.api_key.get_secret_value() == "secret-key"

        settings_str = str(settings)
        assert "secret-key" not in settings_str
        assert "**********" in settings_str

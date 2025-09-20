"""Tests for configuration management."""

import pytest
from pydantic import ValidationError

from src.core.config import Environment, SearchAPISettings, ServerSettings, Settings


class TestServerSettings:
    """Test suite for ServerSettings configuration class."""

    def test_default_values(self) -> None:
        """Test that ServerSettings initializes with correct default values."""
        settings = ServerSettings()

        assert settings.app_name == "travel-hotels"
        assert settings.version == "0.0.1"
        assert settings.environment == Environment.DEVELOPMENT
        assert settings.debug is False
        assert str(settings.host) == "0.0.0.0"
        assert settings.port == 8000

    def test_environment_variable_override(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Test that environment variables override default values."""
        monkeypatch.setenv("SERVER_APP_NAME", "test-app")
        monkeypatch.setenv("SERVER_DEBUG", "true")
        monkeypatch.setenv("SERVER_PORT", "9000")
        monkeypatch.setenv("SERVER_HOST", "localhost")
        monkeypatch.setenv("SERVER_ENVIRONMENT", "production")

        settings = ServerSettings()

        assert settings.app_name == "test-app"
        assert settings.debug is True
        assert settings.port == 9000
        assert settings.host == "localhost"
        assert settings.environment == Environment.PRODUCTION

    def test_invalid_port_validation(self) -> None:
        """Test that invalid port values raise validation errors."""
        with pytest.raises(ValidationError) as exc_info:
            ServerSettings(port=70000)

        error = exc_info.value.errors()[0]
        assert error["type"] == "less_than_equal"
        assert error["input"] == 70000

    def test_host_validation_localhost(self) -> None:
        """Test that localhost is a valid host."""
        settings = ServerSettings(host="localhost")
        assert settings.host == "localhost"

    def test_host_validation_ip_address(self) -> None:
        """Test that IP addresses are valid hosts."""
        settings = ServerSettings(host="192.168.1.1")
        assert str(settings.host) == "192.168.1.1"

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

    def test_default_values_with_api_key(self) -> None:
        """Test that SearchAPISettings initializes with correct default values when API key is provided."""
        settings = SearchAPISettings(api_key="test-key")

        assert settings.api_key.get_secret_value() == "test-key"
        assert settings.base_url == "https://www.searchapi.io/api/v1"
        assert settings.timeout == 30
        assert settings.max_retries == 3

    def test_environment_variable_override(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Test that environment variables override default values."""
        monkeypatch.setenv("SEARCHAPI_API_KEY", "env-key")
        monkeypatch.setenv("SEARCHAPI_BASE_URL", "https://custom.api.url")
        monkeypatch.setenv("SEARCHAPI_TIMEOUT", "60")
        monkeypatch.setenv("SEARCHAPI_MAX_RETRIES", "5")

        settings = SearchAPISettings()

        assert settings.api_key.get_secret_value() == "env-key"
        assert settings.base_url == "https://custom.api.url"
        assert settings.timeout == 60
        assert settings.max_retries == 5

    def test_timeout_validation_minimum(self) -> None:
        """Test that timeout has minimum value validation."""
        with pytest.raises(ValidationError) as exc_info:
            SearchAPISettings(api_key="test-key", timeout=0)

        error = exc_info.value.errors()[0]
        assert error["type"] == "greater_than_equal"
        assert error["input"] == 0

    def test_timeout_validation_maximum(self) -> None:
        """Test that timeout has maximum value validation."""
        with pytest.raises(ValidationError) as exc_info:
            SearchAPISettings(api_key="test-key", timeout=301)

        error = exc_info.value.errors()[0]
        assert error["type"] == "less_than_equal"
        assert error["input"] == 301

    def test_max_retries_validation_minimum(self) -> None:
        """Test that max_retries has minimum value validation."""
        settings = SearchAPISettings(api_key="test-key", max_retries=0)
        assert settings.max_retries == 0

    def test_max_retries_validation_maximum(self) -> None:
        """Test that max_retries has maximum value validation."""
        with pytest.raises(ValidationError) as exc_info:
            SearchAPISettings(api_key="test-key", max_retries=11)

        error = exc_info.value.errors()[0]
        assert error["type"] == "less_than_equal"
        assert error["input"] == 11

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


class TestSettings:
    """Test suite for main Settings configuration class."""

    def test_default_initialization(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Test that main Settings class initializes with default sub-settings."""
        # Need to provide API key for SearchAPI settings
        monkeypatch.setenv("SEARCHAPI_API_KEY", "test-key")

        settings = Settings()

        assert isinstance(settings.server, ServerSettings)
        assert isinstance(settings.searchapi, SearchAPISettings)

        # Check that default values are preserved
        assert settings.server.app_name == "travel-hotels"
        assert settings.searchapi.api_key.get_secret_value() == "test-key"

    def test_environment_isolation(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Test that environment variables are properly isolated by prefix."""
        monkeypatch.setenv("SERVER_DEBUG", "true")
        monkeypatch.setenv("SEARCHAPI_API_KEY", "env-key")
        monkeypatch.setenv("SEARCHAPI_TIMEOUT", "45")

        settings = Settings()

        # Server settings should pick up SERVER_ prefixed variables
        assert settings.server.debug is True

        # SearchAPI settings should pick up SEARCHAPI_ prefixed variables
        assert settings.searchapi.api_key.get_secret_value() == "env-key"
        assert settings.searchapi.timeout == 45

    def test_partial_environment_override(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Test that partial environment variable override works correctly."""
        monkeypatch.setenv("SERVER_PORT", "3000")
        monkeypatch.setenv("SEARCHAPI_API_KEY", "partial-key")

        settings = Settings()

        # Only specified environment variables should be overridden
        assert settings.server.port == 3000
        assert settings.server.debug is False  # Default value preserved

        assert settings.searchapi.api_key.get_secret_value() == "partial-key"
        assert settings.searchapi.timeout == 30  # Default value preserved

    def test_validation_failure_propagation(self) -> None:
        """Test that validation failures from sub-settings are properly propagated."""
        with pytest.raises(ValidationError) as exc_info:
            Settings()  # Missing required SEARCHAPI_API_KEY

        # Should contain error about missing api_key in the searchapi sub-settings
        errors = exc_info.value.errors()

        # Find error related to api_key - it may be nested differently
        api_key_error = None
        for error in errors:
            if "api_key" in str(error.get("loc", [])):
                api_key_error = error
                break

        assert api_key_error is not None
        assert error["type"] == "missing"

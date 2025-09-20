"""Configuration management using Pydantic settings."""

import ipaddress
from enum import Enum

from pydantic import AnyUrl, Field, IPvAnyAddress, PositiveInt, SecretStr, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

from src.core import __package_name__, __version__


class Environment(str, Enum):
    """Environment enumeration."""

    DEVELOPMENT = "development"
    STAGING = "staging"
    PRODUCTION = "production"


class ServerSettings(BaseSettings):
    """
    Server configuration settings.

    Manages basic application server configuration including name, version,
    environment, debug mode, and network settings.
    """

    app_name: str = Field(default=__package_name__, min_length=1)
    version: str = Field(default=__version__)
    environment: Environment = Field(default=Environment.DEVELOPMENT)
    debug: bool = False
    host: IPvAnyAddress | AnyUrl | str = "0.0.0.0"  # nosec B104
    port: PositiveInt = Field(default=8000, le=65535)

    model_config = SettingsConfigDict(env_prefix="SERVER_", extra="ignore")

    @field_validator("host", mode="before")
    @classmethod
    def validate_host(cls, v: str) -> str:
        """Validate and normalize the host address."""
        if v == "localhost":
            return v
        try:
            ipaddress.ip_address(v)
            return v
        except ValueError:
            pass
        try:
            AnyUrl(v)
            return v
        except Exception:  # nosec: B110
            pass
        raise ValueError(f"Invalid host: {v}")


class SearchAPISettings(BaseSettings):
    """
    SearchAPI.io configuration settings.

    Manages configuration for SearchAPI.io hotel search service including
    API key, base URL, timeout settings, and other client configuration.
    """

    api_key: SecretStr = Field(..., description="SearchAPI.io API key")
    base_url: str = Field(default="https://www.searchapi.io/api/v1", description="SearchAPI.io base URL")
    timeout: int = Field(default=30, ge=1, le=300, description="Request timeout in seconds")
    max_retries: int = Field(default=3, ge=0, le=10, description="Maximum number of retries for failed requests")

    model_config = SettingsConfigDict(env_prefix="SEARCHAPI_", extra="ignore")

"""Configuration management using Pydantic settings."""

import ipaddress
from enum import Enum

from pydantic import AnyUrl, Field, IPvAnyAddress, PositiveInt, field_validator
from pydantic_settings import BaseSettings

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

    class Config:
        """Pydantic configuration for settings management."""

        env_prefix = "SERVER_"
        extra = "ignore"

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

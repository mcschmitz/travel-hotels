"""Contains a function to fetch package information for logging."""

import toml

_PYPROJECT_DATA = toml.load("./pyproject.toml")


def _get_metadata_from_pyproject() -> dict[str, str]:
    """Get package version and name from cached pyproject.toml data."""
    version: str = _PYPROJECT_DATA["project"]["version"]
    name: str = _PYPROJECT_DATA["project"]["name"]
    return {"version": version, "name": name}


__version__ = _get_metadata_from_pyproject()["version"]
__package_name__ = _get_metadata_from_pyproject()["name"]

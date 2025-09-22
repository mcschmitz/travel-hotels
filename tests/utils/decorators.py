"""Test decorators for conditional test execution."""

import os
from typing import Callable

import pytest


def github_actions_only(func: Callable) -> Callable:
    """
    Skip test execution unless running in GitHub Actions environment.

    This decorator checks for the presence of GitHub Actions environment variables to determine if the test is running
    in a CI environment. Tests decorated with this will be skipped when run locally but will execute in GitHub Actions.

    Args:
        func: The test function to conditionally execute

    Returns:
        The wrapped test function with conditional execution logic

    """
    is_github_actions = (
        os.getenv("GITHUB_ACTIONS") == "true" or os.getenv("CI") == "true" and os.getenv("GITHUB_WORKFLOW") is not None
    )

    return pytest.mark.skipif(not is_github_actions, reason="Test only runs in GitHub Actions environment")(func)

class SearchAPIError(Exception):
    """Base exception for SearchAPI.io related errors."""

    pass


class SearchAPITimeoutError(SearchAPIError):
    """Raised when SearchAPI.io request times out."""

    pass


class SearchAPIRateLimitError(SearchAPIError):
    """Raised when SearchAPI.io rate limit is exceeded."""

    pass


class SearchAPIAuthenticationError(SearchAPIError):
    """Raised when SearchAPI.io authentication fails."""

    pass

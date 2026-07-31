"""Exceptions raised by integrations with external providers."""


class ExternalProviderError(Exception):
    """Base exception for failures involving external service providers."""


class ExternalProviderResponseError(ExternalProviderError):
    """Indicate that an external provider returned an invalid response."""
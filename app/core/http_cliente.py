from httpx import AsyncClient, Timeout

class HTTPClient:
    """
    Factory responsible for creating configured HTTP clients.

    This centralizes HTTP client configuration, making it reusable
    across the application.
    """

    @staticmethod
    def create() -> AsyncClient:
        """
        Create and configure an asynchronous HTTP client.

        Returns:
            A configured AsyncClient instance.
        """
        return AsyncClient(
            timeout=Timeout(30.0),
            follow_redirects=True,
            headers={
                "User-Agent": (
                    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                    "AppleWebKit/537.36 (KHTML, like Gecko) "
                    "Chrome/137.0.0.0 Safari/537.36"
                ),
                "Accept": "text/html,application/xhtml+xml",
            },
        )
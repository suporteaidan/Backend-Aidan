from app.core.http_cliente import HTTPClient

class NFEClient:
    """
    Client responsible for downloading the HTML content of a NFC-e page.
    """

    async def fetch_nfe_html(self, qr_code_url: str) -> str:
        """
        Download the HTML content of a NFC-e page.

        Args:
            qr_code_url: NFC-e QR Code URL.

        Returns:
            HTML page as a string.

        Raises:
            HTTPStatusError:
                If the server returns an unsuccessful status code.

            RequestError:
                If a network error occurs.
        """

        async with HTTPClient.create() as client:
            response = await client.get(qr_code_url)
            response.raise_for_status()
            return response.text
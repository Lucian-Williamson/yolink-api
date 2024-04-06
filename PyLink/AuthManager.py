import time

import aiohttp

from yolink.auth_mgr import YoLinkAuthMgr
from yolink.endpoint import Endpoints


class AuthManager(YoLinkAuthMgr):
    """My YoLink API Authentication Manager."""

    def __init__(self, session: aiohttp.ClientSession, id: str, key: str) -> None:
        """Initialize YoLink Auth Manager."""
        super().__init__(session)
        self.url: str = ''
        self._UAID_: str = id
        self._SecretKey_: str = key
        self._token_expiration_: int = 0
        self._time_since_: int = 0
        self._token_: str = ""

    def set_region(self, US: bool = False, EU: bool = False):
        if US and not EU:
            self.url = Endpoints.US.value.token_url
        elif EU and not US:
            self.url = Endpoints.EU.value.token_url
        else:
            raise ValueError('US or EU must be selected!')

    async def _use_active_token(self):
        """
        Checks and returns the active token if valid; otherwise, generates a new token.

        Returns:
        - str: Active access token.
        """
        # If Client does not give us an expiration
        if time.time() - self._time_since_ < self._token_expiration_:
            return self._token_
        else:
            print("Refreshing Token")
            return await self.generate_access_token()  # Await the asynchronous call here

    async def access_token(self) -> str:
        """
        Retrieves the current access token.

        Returns:
        - str: Current access token.
        """
        return await self._use_active_token()  # Await the asynchronous call here

    async def check_and_refresh_token(self) -> str:
        """
        Checks and refreshes the access token.

        Returns:
        - str: Refreshed access token.
        """
        return await self._use_active_token()  # Await the asynchronous call here

    async def generate_access_token(self) -> str:
        """
        Generates a new access token asynchronously.

        Returns:
        - str: Newly generated access token.
        """
        payload = {
            "grant_type"   : "client_credentials",
            "client_id"    : self._UAID_,
            "client_secret": self._SecretKey_,
        }
        try:
            # Create the request context manager
            request_context_manager = self._session.post(self.url, data=payload)

            # Execute the request and handle the response
            async with request_context_manager as response:
                print(f"Request {'successful' if response.status == 200 else 'failed'}. Code {response.status}")
                if response.status == 200:
                    data = await response.json()
                    self._token_ = data.get("access_token")
                    self._token_expiration_ = data.get("expires_in")
                    self._time_since_ = time.time()
                    return self._token_
                else:
                    print(f"Request failed with status code {response.status} \n {await response.text()}")
                    return ""
        # Handle response
        except Exception as e:
            print("Error occurred during token generation:", e)
            x = 1

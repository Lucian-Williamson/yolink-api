"""YoLink Client."""
from typing import Any, Dict, List

from aiohttp import ClientError, ClientResponse

from .const import YOLINK_API_GATE
from .auth_mgr import YoLinkAuthMgr
from .exception import YoLinkClientError
from .model import BRDP


class YoLinkClient:
    """YoLink Client."""

    def __init__(self, auth_mgr: YoLinkAuthMgr) -> None:
        """Init YoLink Client"""
        self._auth_mgr = auth_mgr

    async def request(self, method: str, url: str, auth_required: bool = True, **kwargs: Any) -> ClientResponse:
        """Proxy Request and add Auth/CV headers."""
        headers = kwargs.pop("headers", {})
        params = kwargs.pop("params", None)
        data = kwargs.pop("data", None)

        # Extra, user supplied values
        extra_headers = kwargs.pop("extra_headers", None)
        extra_params = kwargs.pop("extra_params", None)
        extra_data = kwargs.pop("extra_data", None)
        if auth_required:
            # Ensure token valid
            await self._auth_mgr.check_and_refresh_token()
            # Set auth header
            headers["Authorization"] = self._auth_mgr.http_auth_header()
        # Extend with optionally supplied values
        if extra_headers:
            headers.update(extra_headers)
        if extra_params:
            # Query parameters
            params = params or {}
            params.update(extra_params)
        if extra_data:
            # form encoded post data
            data = data or {}
            data.update(extra_data)
        return await self._auth_mgr.client_session().request(
            method, url, **kwargs, headers=headers, params=params, data=data, timeout=8
        )

    async def get(self, url: str, **kwargs: Any) -> ClientResponse:
        """Call http request with Get Method."""
        return await self.request("GET", url, True, **kwargs)

    async def post(self, url: str, **kwargs: Any) -> ClientResponse:
        """Call Http Request with POST Method"""
        return await self.request("POST", url, True, **kwargs)

    async def call_yolink_api(self, bsdp: Dict, **kwargs: Any) -> BRDP:
        """Call YoLink Api"""
        try:
            yl_resp = await self.post(YOLINK_API_GATE, json=bsdp, **kwargs)
            yl_resp.raise_for_status()
            _yl_body = await yl_resp.text()
            brdp = BRDP.parse_raw(_yl_body)
            brdp.check_response()
        except ClientError:
            raise YoLinkClientError("-1", "client error")
        except YoLinkClientError as err:
            raise err
        return brdp

    async def get_auth_devices(self, **kwargs: Any) -> BRDP:
        """Get auth devices."""
        return await self.call_yolink_api({"method": "Home.getDeviceList"}, **kwargs)

    async def get_general_info(self, **kwargs: Any) -> BRDP:
        """Get general info."""
        return await self.call_yolink_api({"method": "Home.getGeneralInfo"}, **kwargs)

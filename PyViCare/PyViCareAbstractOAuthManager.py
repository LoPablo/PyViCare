import logging
import socketio
import json

from abc import abstractclassmethod
from typing import Any

from authlib.integrations.base_client import TokenExpiredError, InvalidTokenError
from authlib.integrations.requests_client import OAuth2Session

from PyViCare import Feature
from PyViCare.PyViCareUtils import (PyViCareCommandError,
                                    PyViCareInternalServerError,
                                    PyViCareRateLimitError)

logger = logging.getLogger('ViCare')
logger.addHandler(logging.NullHandler())

API_BASE_URL = 'https://api.viessmann.com/iot/v1'
LIVEUPDATE_REQUEST_URL = 'https://api.viessmann.com/live-updates/v1/iot'
WSS_URL = "wss://api.viessmann.com/live-updates/v1/connect/?id="
TRANSPORT = 'websocket'

SUBSCRIPTION_BASE = {
    "subscriptions": []
}


class AbstractViCareOAuthManager:
    def __init__(self, oauth_session: OAuth2Session) -> None:
        self.__oauth = oauth_session

    @property
    def oauth_session(self) -> OAuth2Session:
        return self.__oauth

    def replace_session(self, new_session: OAuth2Session) -> None:
        self.__oauth = new_session

    @abstractclassmethod
    def renewToken(self) -> None:
        return

    async def subscribe_to_live_updates(self):
        response = self._oAuthManager.post_raw(LIVEUPDATE_REQUEST_URL, json.dumps(self._subscriptions))
        if response is not None:
            await self.establish_websocket_connection(response)

    async def establish_websocket_connection(self, response):
        sio = socketio.AsyncClient()

        self.socket_id = response['id']
        await sio.connect(WSS_URL + self.socket_id, transports=['websocket'], socketio_path=response['path'],
                          namespaces=response['namespace'])

        @sio.on('connect', namespace=response['namespace'])
        async def connect():
            print('connection established')

        @sio.on('feature', namespace=response['namespace'])
        def feature_changed(data):
            print(data)

        @sio.on('gateway-aggregated-status-changed', namespace=response['namespace'])
        def gateway_aggregated_status_changed(data):
            print(data)

        @sio.event
        async def disconnect():
            print('disconnected from server')

        await sio.wait()

    def get(self, url: str) -> Any:
        try:
            logger.debug(self.__oauth)
            response = self.__oauth.get(f"{API_BASE_URL}{url}", timeout=31).json()
            logger.debug(f"Response to get request: {response}")
            self.__handle_expired_token(response)
            self.__handle_rate_limit(response)
            self.__handle_server_error(response)
            return response
        except TokenExpiredError:
            self.renewToken()
            return self.get(url)
        except InvalidTokenError:
            self.renewToken()
            return self.get(url)

    def __handle_expired_token(self, response):
        if ("error" in response and response["error"] == "EXPIRED TOKEN"):
            raise TokenExpiredError(response)

    def __handle_rate_limit(self, response):
        if not Feature.raise_exception_on_rate_limit:
            return

        if ("statusCode" in response and response["statusCode"] == 429):
            raise PyViCareRateLimitError(response)

    def __handle_server_error(self, response):
        if ("statusCode" in response and response["statusCode"] >= 500):
            raise PyViCareInternalServerError(response)

    def __handle_command_error(self, response):
        if not Feature.raise_exception_on_command_failure:
            return

        if ("statusCode" in response and response["statusCode"] >= 400):
            raise PyViCareCommandError(response)



    def post(self, url, data) -> Any:
        """POST URL using OAuth session. Automatically renew the token if needed
            Parameters
            ----------
            url : str
                URL to get
            data : str
                Data to post

            Returns
            -------
            result: json
                json representation of the answer
            """
        self.post_raw(f"{API_BASE_URL}{url}", data)

    def post_raw(self, url, data) -> Any:
        headers = {"Content-Type": "application/json",
                   "Accept": "application/vnd.siren+json"}
        try:
            response = self.__oauth.post(
                f"{url}", data, headers=headers).json()
            self.__handle_expired_token(response)
            self.__handle_rate_limit(response)
            self.__handle_command_error(response)
            return response
        except TokenExpiredError:
            self.renewToken()
            return self.post(url, data)
        except InvalidTokenError:
            self.renewToken()
            return self.get(url)

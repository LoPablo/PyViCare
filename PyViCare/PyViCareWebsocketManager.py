import logging
import json
import asyncio
import socketio
from PyViCare.PyViCareAbstractOAuthManager import AbstractViCareOAuthManager

logger = logging.getLogger('ViCare')
logger.addHandler(logging.NullHandler())

LIVEUPDATE_REQUEST_URL = 'https://api.viessmann.com/live-updates/v1/iot'
TRANSPORT = 'websocket'
DUMMY_SUBSCRIPTION = '{"subscriptions":[{"id":"HEMS","type":"device-features","gatewayId":"7736172106234225"},{"id":"0","type":"device-features","gatewayId":"7736172106234225"},{"id":"7736172106234225","type":"gateway-features"},{"id":"RoomControl-1","type":"device-features","gatewayId":"7952592000729225"}]}'

SUBSCRIPTION_BASE = {
    "subscriptions": []
}


class LiveUpdateManager():

    _subscriptions = SUBSCRIPTION_BASE
    def __init__(self, o_auth_manager: AbstractViCareOAuthManager):
        self._oAuthManager = o_auth_manager

    async def addToSubscription(self, id : str, gateway_id : str, property_name : str):
        self._subscriptions.get("subscriptions").append({
            "id" : id,
            "type" : "device-features",
            "gatewayId" : gateway_id
        })


    async def subscribeToLiveUpdates(self):
        response = self._oAuthManager.post_raw(LIVEUPDATE_REQUEST_URL, json.dumps(self._subscriptions))
        if response is not None:
            await self.establishWebsocketConnection(response)


    async def renewWebsocketConnection(self):
        return

    async def establishWebsocketConnection(self, response):
        sio = socketio.AsyncClient()

        self.socket_id = response['id']
        await sio.connect(response['url'], transports=['websocket'], socketio_path=response['path'],
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

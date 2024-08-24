import logging
import json
import socketio
from PyViCare.PyViCareAbstractOAuthManager import AbstractViCareOAuthManager
from PyViCare.PyViCareDevice import Device

logger = logging.getLogger('ViCare')
logger.addHandler(logging.NullHandler())

LIVEUPDATE_REQUEST_URL = 'https://api.viessmann.com/live-updates/v1/iot'
WSS_URL = "wss://api.viessmann.com/live-updates/v1/connect/"
TRANSPORT = 'websocket'
SUBSCRIPTION_BASE = {"subscriptions": []}


class LiveUpdateManager():
    _subscriptions = SUBSCRIPTION_BASE

    def __init__(self, o_auth_manager: AbstractViCareOAuthManager):
        self._oAuthManager = o_auth_manager
        self._subscribed_devices = []


    @property
    def subscriptions(self):
        return self._subscriptions

    def addToSubscription(self, device : Device):
        self._subscribed_devices.append(device)
        newSubscrption = device.getLiveUpdateSubscriptionString()
        for sub in newSubscrption:
            self._subscriptions.get("subscriptions").append(sub)

    async def subscribeToLiveUpdates(self):
        response = self._oAuthManager.post_raw(LIVEUPDATE_REQUEST_URL, json.dumps(self._subscriptions, separators=(',', ':')))
        if response is not None:
            print(response)
            await self.establishWebsocketConnection(response)

    async def renewWebsocketConnection(self):
        return

    async def establishWebsocketConnection(self, response):
        sio = socketio.AsyncClient()

        self.socket_id = response['id']
        await sio.connect(response['url'], transports=['websocket'], socketio_path=response['path'],
                          namespaces=response['namespace'])

        @sio.event
        def connect():
            logger.info('connected to server')

        @sio.on('connect', namespace=response['namespace'])
        async def connect():
            print('connection established')

        @sio.on('feature', namespace=response['namespace'])
        def feature_changed(data):
            feature = data['feature']
            if feature is not None and "deviceId" in feature:
                device_id = feature['deviceId']
                updated_feature_name = feature['feature']
                properties = feature['properties']
                for device in self._subscribed_devices:
                    if device_id == device.getId():
                        if device.service.hasPropertyObserver(updated_feature_name):
                            device.service.updateProperty(device_id, updated_feature_name, properties)

        @sio.on('message', namespace=response['namespace'])
        def message_changed(data):
            print(data)

        @sio.on('gateway-aggregated-status-changed', namespace=response['namespace'])
        def gateway_aggregated_status_changed(data):
            print(data)

        @sio.event
        async def disconnect():
            print('disconnected from server')

        await sio.wait()

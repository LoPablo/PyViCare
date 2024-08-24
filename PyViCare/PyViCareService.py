import json
import logging
from typing import Any, List

from PyViCare.PyViCareAbstractOAuthManager import AbstractViCareOAuthManager
from PyViCare.PyViCareUtils import PyViCareNotSupportedFeatureError

logger = logging.getLogger('ViCare')
logger.addHandler(logging.NullHandler())


def readFeature(entities, property_name):
    feature = next(
        (f for f in entities if f["feature"] == property_name), None)

    if (feature is None):
        raise PyViCareNotSupportedFeatureError(property_name)

    return feature


def hasRoles(requested_roles: List[str], existing_roles: List[str]) -> bool:
    return len(requested_roles) > 0 and set(requested_roles).issubset(set(existing_roles))


def buildSetPropertyUrl(accessor, property_name, action):
    return f'/features/installations/{accessor.id}/gateways/{accessor.serial}/devices/{accessor.device_id}/features/{property_name}/commands/{action}'


def buildGetPropertyUrl(accessor, property_name):
    return f'/features/installations/{accessor.id}/gateways/{accessor.serial}/devices/{accessor.device_id}/features/{property_name}'

class ViCareDeviceAccessor:
    def __init__(self, _id: int, serial: str, device_id: str) -> None:
        self.id = _id
        self.serial = serial
        self.device_id = device_id

class ViCareService:
    def __init__(self, oauth_manager: AbstractViCareOAuthManager, accessor: ViCareDeviceAccessor, roles: List[str]) -> None:
        self.oauth_manager = oauth_manager
        self.accessor = accessor
        self.roles = roles
        self._observers = {}

    def getProperty(self, property_name: str) -> Any:
        url = self.buildGetPropertyUrl(property_name)
        return self.oauth_manager.get(url)

    def hasPropertyObserver(self, property_name: str) -> bool:
        return property_name in self._observers

    def updateProperty(self, device_id : str, property_name: str, data: Any) -> None:
        self._informObserver(device_id, property_name, data)

    def _informObserver(self, device_id : str, property_name: str, data: Any):
        if property_name in self._observers:
           for observer in self._observers[property_name]:
             observer(device_id, property_name,data)

    def buildGetPropertyUrl(self, property_name):
        if self._isGateway():
            return f'/features/installations/{self.accessor.id}/gateways/{self.accessor.serial}/features/{property_name}'
        return f'/features/installations/{self.accessor.id}/gateways/{self.accessor.serial}/devices/{self.accessor.device_id}/features/{property_name}'

    def hasRoles(self, requested_roles) -> bool:
        return hasRoles(requested_roles, self.roles)

    def _isGateway(self) -> bool:
        return self.hasRoles(["type:gateway;VitoconnectOpto1"]) or self.hasRoles(["type:gateway;TCU300"])

    def setProperty(self, property_name: str, action: str, data: Any) -> Any:
        url = buildSetPropertyUrl(
            self.accessor, property_name, action)

        post_data = data if isinstance(data, str) else json.dumps(data)
        return self.oauth_manager.post(url, post_data)

    def subscribeToLiveUpdatesForProperty(self, callback, property_name: str):
        if property_name not in self._observers:
            self._observers[property_name] = []
        self._observers[property_name].append(callback);

    def fetch_all_features(self) -> Any:
        url = f'/features/installations/{self.accessor.id}/gateways/{self.accessor.serial}/devices/{self.accessor.device_id}/features/'
        if self._isGateway():
            url = f'/features/installations/{self.accessor.id}/gateways/{self.accessor.serial}/features/'
        return self.oauth_manager.get(url)

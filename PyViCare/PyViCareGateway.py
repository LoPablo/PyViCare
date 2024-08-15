from PyViCare.PyViCareDevice import Device
from PyViCare.PyViCareUtils import handleNotSupported


class Gateway(Device):

    @handleNotSupported
    def getSerial(self):
        return self.service.getProperty("gateway.devices")["gatewayId"]

    @handleNotSupported
    def getWifiSignalStrength(self):
        return self.service.getProperty("gateway.wifi")["properties"]["strength"]["value"]

    def getLiveUpdateSubscriptionString(self):
        return [{"id": self.getGatewayId(), "type": "gateway-features", "version": "2"}, {"id": self.getId(), "type": "device-features", "gatewayId": self.getGatewayId(), "version": "2"}]


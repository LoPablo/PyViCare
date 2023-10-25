from PyViCare.PyViCareDevice import Device
from PyViCare.PyViCareUtils import handleNotSupported


class RoomSensor(Device):

    @handleNotSupported
    def getTemperature(self):
        return self.service.getProperty("device.sensors.temperature")["properties"]["value"]["value"]

    @handleNotSupported
    def getHumidity(self):
        return self.service.getProperty("device.sensors.humidity")["properties"]["value"]["value"]

    @handleNotSupported
    def getBatteryPercentage(self):
        return self.service.getProperty("device.power.battery")["properties"]["level"]["value"]

    @handleNotSupported
    def getLinkQualityIndicator(self):
        return self.service.getProperty("device.zigbee.lqi")["properties"]["strength"]["value"]

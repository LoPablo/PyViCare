from PyViCare.PyViCareDevice import Device
from PyViCare.PyViCareUtils import handleNotSupported


class FloorHeatingCircuitDistributorBox(Device):

    @handleNotSupported
    def getSupplyTemperature(self):
        return self.service.getProperty("fht.sensors.temperature.supply")["properties"]["value"]["value"]

    @handleNotSupported
    def getHeatingModeEnabled(self):
        return self.service.getProperty("fht.operating.modes.heating")["properties"]["active"]["value"]

    @handleNotSupported
    def getCoolingModeEnabled(self):
        return self.service.getProperty("fht.operating.modes.cooling")["properties"]["active"]["value"]

    def getOperationMode(self):
        return self.service.getProperty("fht.operating.modes.active")["properties"]["value"]["value"]

    @handleNotSupported
    def getLinkQualityIndicator(self):
        return self.service.getProperty("device.zigbee.lqi")["properties"]["strength"]["value"]

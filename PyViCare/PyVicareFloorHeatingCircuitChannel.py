from PyViCare.PyViCareDevice import Device
from PyViCare.PyViCareUtils import handleNotSupported


class FloorHeatingCircuitChannel(Device):

    @handleNotSupported
    def getValveState(self):
        return self.service.getProperty("fht.valve.state")["properties"]["status"]["value"]

    @handleNotSupported
    def getValvePosition(self):
        return self.service.getProperty("fht.valve.position")["properties"]["value"]["value"]

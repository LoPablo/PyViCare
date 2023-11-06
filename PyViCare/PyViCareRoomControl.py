from typing import Any, List

from PyViCare.PyViCareDevice import Device
from PyViCare.PyViCareUtils import handleAPICommandErrors, handleNotSupported


class RoomControl(Device):

    @handleNotSupported
    def getAvailableRoomIds(self):
        return self.service.getProperty("rooms")["properties"]["enabled"]["value"]
    @property
    def rooms(self) -> List[Any]:
        return list([self.getRoom(x) for x in self.getAvailableRoomIds()])

    def getRoom(self, roomId):
        return Room(self.service, roomId)


class Room(Device):

    def __init__(self,service, id):
        self.service = service
        self.id = id
    @handleNotSupported
    def getName(self):
        return self.service.getProperty("rooms." + self.id)["properties"]["name"]["value"]

    @handleNotSupported
    def getTemperature(self):
        return self.service.getProperty("rooms." + self.id + ".sensors.temperature")["properties"]["value"]["value"]

    @handleNotSupported
    def getHumidity(self):
        return self.service.getProperty("rooms." + self.id + ".sensors.humidity")["properties"]["value"]["value"]

    @handleNotSupported
    def getOperatingStateReason(self):
        return self.service.getProperty("rooms." + self.id + ".operating.state")["properties"]["reason"]["value"]

    @handleNotSupported
    def getOperatingStateDemand(self):
        return self.service.getProperty("rooms." + self.id + ".operating.state")["properties"]["demand"]["value"]

    @handleNotSupported
    def getDesiredTemperatureForProgram(self, program):
        return \
            self.service.getProperty(f"rooms.{self.id}.operating.programs.{program}")["properties"][
                "temperature"]["value"]

    @handleNotSupported
    def getCurrentDesiredTemperature(self):
        active_program = self.getActiveProgram()
        if active_program in ['standby']:
            return None
        return self.service.getProperty(f"rooms.{self.id}.operating.programs.{active_program}")[
            "properties"]["temperature"]["value"]

    @handleNotSupported
    def getActiveProgram(self):
        return self.service.getProperty(f"rooms.{self.id}.operating.programs.active")["properties"]["value"]["value"]

    # @handleNotSupported
    # def getTemperatureProgramNormal(self):
    #     return self.service.getProperty("rooms." + self.id + ".temperature.levels.normal.perceived")["properties"]["temperature"][
    #         "value"]
    #
    # @handleNotSupported
    # def getTemperatureProgramComfort(self):
    #     return self.service.getProperty("rooms." + self.id + ".temperature.levels.comfort.perceived")["properties"]["temperature"][
    #         "value"]
    #
    # @handleNotSupported
    # def getTemperatureProgramReduced(self):
    #     return self.service.getProperty("rooms." + self.id + ".temperature.levels.reduced.perceived")["properties"]["temperature"][
    #         "value"]
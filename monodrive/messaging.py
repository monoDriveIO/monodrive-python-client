import json
import random
import struct
import sys


Status_ID = u"Status_ID"
SimulatorConfig_ID = u"SimulatorConfig_ID"
EgoVehicleConfig_ID	= u"EgoVehicleConfig_ID"
EgoControl_ID = u"EgoControl_ID"
MapCommand_ID = u"MapCommand_ID"
ScenarioConfig_ID = u"ScenarioConfig_ID"
ScenarioInit_ID	= u"ScenarioInit_ID"
WaypointUpdate_ID = u"WaypointUpdate_ID"
StreamData_ID = u"StreamData_ID"
SpawnActorCommand_ID = u"SpawnActorCommand_ID"
UpdateActorCommand_ID = u"UpdateActorCommand_ID"
AttachSensorCommand_ID = u"AttachSensorCommand_ID"
DetachSensorCommand_ID = u"DetachSensorCommand_ID"
StopAllSensorsCommand_ID = u"StopAllSensorsCommand_ID"
StartAllSensorsCommand_ID = u"StartAllSensorsCommand_ID"
ActivateLicense_ID = u"ActivateLicense"
WeatherConfigCommand_ID = u"WeatherConfig"
REPLAY_ConfigureSensorsCommand_ID = "REPLAY_ConfigureSensorsCommand_ID"
REPLAY_ConfigureTrajectoryCommand_ID = "REPLAY_ConfigureTrajectoryCommand_ID"
REPLAY_StepSimulationCommand_ID = "REPLAY_StepSimulationCommand_ID"
REPLAY_StateStepSimulationCommand_ID = "REPLAY_StateStepSimulationCommand_ID"

CONTROL_HEADER = 0x6d6f6e6f
RESPONSE_HEADER = 0x6f6e6f6d


class ApiMessage:

    def __init__(self, command, args):
        self.command = command
        self.args = args
        self.ref = random.randint(1,sys.maxsize)

    def __str__(self):
        return json.dumps(self.to_json())

    def to_json(self):
        return {
            u"type": self.command,
            u"message": self.args,
            u"reference": self.ref
        }

    def read(self, client):
        data = client.read(8)
        magic, len = struct.unpack("!II", data)
        if magic == RESPONSE_HEADER and len > 0:
            data = client.read(len - 8)
            return json.loads(data.decode("utf-8"))

        return {}

    def write(self, client):
        data = str(self)
        client.write(struct.pack("!II", CONTROL_HEADER, len(data)+8))
        client.write(data.encode('utf8'))
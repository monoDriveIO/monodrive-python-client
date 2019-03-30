"""messaggin.py
Implementation of API messages for simulator communications.
"""
import json
import random
import struct
import sys


ID_STATUS = u"Status_ID"
"""Message ID for status commands"""
ID_SIMULATOR_CONFIG = u"SimulatorConfig_ID"
"""Message ID for simulator configuration commands"""
ID_EGO_VEHICLE_CONFIG = u"EgoVehicleConfig_ID"
"""Message ID for configuring the ego vehicle"""
ID_EGO_CONTROL = u"EgoControl_ID"
"""Message ID for controlling the ego vehicle"""
ID_MAP_COMMAND = u"MapCommand_ID"
"""Message ID for controlling the map"""
ID_SCENARIO_CONFIG = u"ScenarioConfig_ID"
"""Message ID for configuring the scenario"""
ID_SCENARIO_INIT = u"ScenarioInit_ID"
"""Message ID for initializing the scenario"""
ID_WAYPOINT_UPDATE = u"WaypointUpdate_ID"
"""Message ID for update the current waypoint."""
ID_STREAM_DATA = u"StreamData_ID"
"""Message ID to control the data stream"""
ID_SPAWN_ACTOR_COMMAND = u"SpawnActorCommand_ID"
"""Message ID to spawn a new actor in the current scenario"""
ID_UPDATE_ACTOR_COMMAND = u"UpdateActorCommand_ID"
"""Message ID to update an existing actor in the current scenario"""
ID_ATTACH_SENSOR_COMMAND = u"AttachSensorCommand_ID"
"""Message ID to attach a new sensor to the ego vehicle"""
ID_DETACH_SENSOR_COMMAND = u"DetachSensorCommand_ID"
"""Message ID to detach a sensor from the ego vehicle"""
ID_STOP_ALL_SENSORS_COMMAND = u"StopAllSensorsCommand_ID"
"""Message ID to stop all the sensors on the ego vehicle"""
ID_START_ALL_SENSORS_COMMAND = u"StartAllSensorsCommand_ID"
"""Message ID to start all the sensors on the ego vehicle"""
ID_ACTIVATE_LICENSE = u"ActivateLicense"
"""Message ID to activate the server license"""
ID_WEATHER_CONFIG_COMMAND = u"WeatherConfig"
"""Message ID to configure the current weather in the scenario"""
ID_REPLAY_CONFIGURE_SENSORS_COMMAND = "REPLAY_ConfigureSensorsCommand_ID"
"""Message ID to replay the current sensor configuration"""
ID_REPLAY_CONFIGURE_TRAJECTORY_COMMAND = "REPLAY_ConfigureTrajectoryCommand_ID"
"""Message ID to replay the current trajectory configuration."""
ID_REPLAY_STEP_SIMULATION_COMMAND = "REPLAY_StepSimulationCommand_ID"
"""Message ID to replay the current step in the simulation."""
ID_REPLAY_STATE_SIMULATION_COMMAND = "REPLAY_StateStepSimulationCommand_ID"
"""Message ID to replay the current state in the simulation."""
HEADER_CONTROL = 0x6d6f6e6f
"""The message prefix header for control messages to the server"""
HEADER_RESPONSE = 0x6f6e6f6d
"""The message prefix header for response messages from the server"""


class ApiMessage:
    """Class that defines message format for read/write to simulator"""

    def __init__(self, command, args):
        """Constructor.

        Args:
            command(str): The command string for this message.
            args(dict): A dictionary with string keys that map to message
            arugments.
        """
        # The string representing the type of this message
        self.__command = command
        # Arguments for this message to pass in the `message` field
        self.__args = args
        # Unique identifier for this message
        self.__uid = random.randint(1, sys.maxsize)

    @property
    def command(self):
        """Get the command this message contains.

        Returns:
            String of the command.
        """
        return self.__command

    @property
    def args(self):
        """Get the arguments this message contains.

        Returns:
            Dictionary of the command arguments.
        """
        return self.__args

    @property
    def uid(self):
        """Get the unique identifier for this message.

        Returns:
            Integer of the uid.
        """
        return self.__uid

    def __str__(self):
        """Convert the message contents to its JSON representation.

        Returns:
            String with JSON.
        """
        return json.dumps(self.to_json())

    def to_json(self):
        """Convert the message contents to its JSON representation.

        Returns:
            Dictionary with JSON.
        """
        return {
            u"type": self.command,
            u"message": self.args,
            u"reference": self.uid
        }

    @staticmethod
    def read(client):
        """Read data from the connected `client`.

        Args:
            client(Client) - The client that is connected to the simulator.

        Returns:
            The dictionary representation of the message that was read. Empty
            dictionary if nothing was read.
        """
        # Read the first 8 bytes to get the header
        data = client.read(8)
        magic, size = struct.unpack("!II", data)
        # Only read if the message was a response
        if magic == HEADER_RESPONSE and size > 0:
            # Read the rest of the message and return
            data = client.read(size - 8)
            return json.loads(data.decode("utf-8"))

        return {}

    def write(self, client):
        """Write a message to the connected client.

        Args:
            client(Client) - The client that is connected to the simulator.
        """
        data = str(self)
        client.write(struct.pack("!II", HEADER_CONTROL, len(str(self))+8))
        client.write(data.encode('utf8'))

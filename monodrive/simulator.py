"""simulator.py
A simple simulator that will read all sensor values from the connected sensors.
"""
from monodrive.configurator import Configurator
import monodrive.messaging as mmsg
from enum import Enum
from uut.client import UUT_Client
import signal


class Mode(Enum):
    """Enumeration of all simulator modes"""
    # Closed loop control of the ego vehicle
    MODE_CLOSED_LOOP = 0
    # Replay of recorded trajectory
    MODE_REPLAY = 1
    # PXI mode
    MODE_PXI = 2


class Simulator:
    """Simulator driver that will connect and read all sensors on the
    ego vehicle."""

    def __init__(self, config, trajectory, client):
        """Constructor.

        Args:
            config(dict): The configuration JSON for this simulator instance
            trajectory(dict): The configuration JSON for the trajectory to replay
            in Modes.MODE_REPLAY
        """
        self.__config = config
        self.__trajectory = trajectory
        #self.client = Configurator(config['server_ip'], config['server_port'])
        #self.client.connect()
        self.client = client

        self.__running = False

    @property
    def mode(self):
        """Get the current simulation mode.

        Returns:
            The current `Mode` that the
        """
        return self.__config['simulation_mode']

    def set_mode(self, mode):
        """Change the current simulation mode.

        Args:
            mode(Enum): One of the `Mode` to switch to.
            """
        self.__config['simulation_mode'] = mode

    def set_weather(self, weather):
        """Set the current weather profile for the simulation.

        Args:
            weather(str): The weather profile to set (e.g. "Default",
            "ClearNoon", etc.)

        Returns:
            The response message from the simulator for this configuration.
        """
        return self.configure_weather({
                                 u"set_profile": weather
                             })

    def configure_weather(self, config):
        """Configure the weather from JSON representation.

        Args:
            config(dict): The configuration JSON to send to the server

        Returns:
            The response message from the simulator for this configuration.
        """
        message = mmsg.ApiMessage(mmsg.ID_WEATHER_CONFIG_COMMAND, config)
        return self.send_command(message)

    def configure(self):
        """Configure the server with the current simulator settings"""
        self.send_command(mmsg.ApiMessage(
            mmsg.ID_SIMULATOR_CONFIG, self.__config))
        self.send_command(mmsg.ApiMessage(
            mmsg.ID_REPLAY_CONFIGURE_TRAJECTORY_COMMAND, self.__trajectory))


    def start(self):
        """Start the simulation """
        self.__running = True
        self.configure()

    def stop(self):
        """Stop the simulation"""
        self.__running = False

    def send_command(self, command):
        """Send the command to the connected simulator client.

        Args:
            command(ApiMessage): The command to send to the server.
        """
        command.write(self.client)
        return command.read(self.client)

"""simulator.py
A simple simulator that will read all sensor values from the connected sensors.
"""

# lib
from enum import Enum

# src
from monodrive.common.client import Client
from monodrive.sensors.base_sensor import Sensor
import monodrive.common.messaging as mmsg


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

    def __init__(self, config, trajectory, sensors):
        """Constructor.

        Args:
            config(dict): The configuration JSON for this simulator instance
            trajectory(dict): The configuration JSON for the trajectory to replay
            in Modes.MODE_REPLAY
            sensors(dict): The configuration JSON for the suit of sensors for
            this simulator instance.
        """
        self.__config = config
        self.__trajectory = trajectory
        self.__sensor_config = sensors
        self.__sensors = dict()
        self.__client = Client(config['server_ip'], config['server_port'])
        self.__client.connect()
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
        self.send_command(mmsg.ApiMessage(
            mmsg.ID_REPLAY_CONFIGURE_SENSORS_COMMAND, self.__sensor_config))

    def start(self):
        """Start the simulation """
        self.__running = True
        self.configure()
        self.start_sensor_listening()

    def step(self, steps=1):
        """Step the simulation the specified number of steps.

        Args:
            steps(int): The number of steps to move the simulation

        Raises:
            Exception if the simulator is not currently running
        """
        if not self.__running:
            raise Exception("Simulator is not running")

        response = self.send_command(
            mmsg.ApiMessage(
                mmsg.ID_REPLAY_STEP_SIMULATION_COMMAND,
                {u'amount': steps}
            )
        )
        return response

    def stop(self):
        """Stop the simulation and all attached sensors."""
        for sensor_id in self.__sensors.keys():
            self.__sensors[sensor_id].stop()
        self.__running = False

    def send_command(self, command):
        """Send the command to the connected simulator client.

        Args:
            command(ApiMessage): The command to send to the server.
        """
        command.write(self.__client)
        return command.read(self.__client)

    def start_sensor_listening(self):
        """Start all sensors"""
        for sc in self.__sensor_config:
            sensor = Sensor(self.__config['server_ip'], sc)
            sensor.start()
            self.__sensors[sensor.id] = sensor

    @property
    def sensors_ids(self):
        """Get the current list of all sensor ids.

        Returns:
            The list of all sensor ids.
        """
        return self.__sensors.keys()

    def subscribe_to_sensor(self, uid, callback):
        """Subscribe to a single sensor's data ouput in the simulator.

        Args:
            uid(str): The uid of the sensor to subscribe to.
            callback(func): The function that will be called when the sensor's
            data arrives. Should be of the format:
                def my_callback(data):
        """
        self.__sensors[uid].subscribe(callback)

    def send_control(self, forward, right):
        self.send_command(
            mmsg.ApiMessage(
                mmsg.ID_EGO_CONTROL,
                {
                    u'forward_amount': forward,
                    u'right_amount': right,
                    u'brake_amount': 0,
                    u'drive_mode': 1
                }
            )
        )

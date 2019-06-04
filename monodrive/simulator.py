"""simulator.py
A simple simulator that will read all sensor values from the connected sensors.
"""
from monodrive.client import Client
import monodrive.messaging as mmsg
from monodrive.sensors import Sensor
from enum import Enum
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

    def __init__(self, config, sensors, trajectory):
        """Constructor.

        Args:
            config(dict): The configuration JSON for this simulator instance
            sensors(dict): The configuration JSON for the suit of sensors for
            this simulator instance.
            trajectory(dict): The configuratio JSON for the trajectory to replay
            in Modes.MODE_REPLAY
        """
        self.__config = config
        self.__sensor_config = sensors
        self.__sensors = dict()
        self.__trajectory = trajectory
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
            mmsg.ID_REPLAY_CONFIGURE_SENSORS_COMMAND, self.__sensor_config))
        self.send_command(mmsg.ApiMessage(
            mmsg.ID_REPLAY_CONFIGURE_TRAJECTORY_COMMAND, self.__trajectory))

    def start(self):
        """Start the simulation and all attached sensors."""
        self.__running = True
        self.configure()

        for sc in self.__sensor_config:
            if sc['sensor_process']:
                sensor = Sensor(self.__config['server_ip'], sc)
                sensor.start()
                self.__sensors[sensor.id] = sensor

    def stop(self):
        """Stop the simulation and all attached sensors."""
        for sensor_id in self.__sensors.keys():
            self.__sensors[sensor_id].stop()
        self.__running = False

    def step(self, steps=1):
        """Step the simulation the specified number of steps.

        Args:
            steps(int): The number of steps to move the simulation

        Raises:
            Exception if the simulator is not currently running
        """
        if not self.__running:
            raise Exception("Simulator is not running")

        self.send_command(
            mmsg.ApiMessage(mmsg.ID_REPLAY_STEP_SIMULATION_COMMAND,
                            {
                                u'amount': steps
                            }))

    def send_control(self, forward, right):
        self.send_command(
            mmsg.ApiMessage(mmsg.ID_EGO_CONTROL,
                            {
                                u'forward_amount': forward,
                                u'right_amount': right
                            }))

    def send_command(self, command):
        """Send the command to the connected simulator client.

        Args:
            command(ApiMessage): The command to send to the server.
        """
        command.write(self.__client)
        return command.read(self.__client)

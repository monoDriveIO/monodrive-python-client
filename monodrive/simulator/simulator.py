"""simulator.py
A simple simulator that will read all sensor values from the connected sensors.
"""

# lib
import json
from enum import Enum
import objectfactory

# src
from monodrive.common.client import Client
from monodrive.sensors import SensorThread
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

    def __init__(
            self,
            config,
            scenario=None,
            sensors=None,
            weather=None,
            ego=None,
            verbose=False
    ):
        """Constructor.

        Args:
            config(dict): The configuration JSON for this simulator instance
            scenario(dict): The configuration JSON for the trajectory to replay
            in Modes.MODE_REPLAY
            sensors(dict): The configuration JSON for the suite of sensors for
            this simulator instance.
            weather(dict): The configuration JSON for weather conditions
            ego(dict): The configuration JSON for the ego vehicle
            verbose(bool):
        """
        self.__config = config
        self.__scenario = scenario
        self.__sensor_config = sensors
        self.__weather = weather
        self.__ego = ego
        self.__verbose = verbose
        self.__sensors = dict()
        self.__client = Client(config['server_ip'], config['server_port'])
        self.__running = False

    @property
    def mode(self):
        """Get the current simulation mode.

        Returns:
            The current `Mode` that the
        """
        return self.__config['simulation_mode']

    @mode.setter
    def mode(self, mode):
        """Change the current simulation mode.

        Args:
            mode(Enum): One of the `Mode` to switch to.
            """
        self.__config['simulation_mode'] = mode

    @property
    def map(self):
        """Get the current simulator map name

        Returns:
            str: simulator map name
        """
        return self.__config['map']

    @map.setter
    def map(self, map_name):
        """Set the simulator config map name

        Args:
            map_name(str): new simulator config map name
        """
        self.__config['map'] = map_name

    def configure(self):
        """Configure the server with the current simulator settings"""

        # include vehicle config if available
        if self.__ego:
            self.__config['ego_config'] = self.__ego

        # do simulator config
        res = self.send_command(
            mmsg.ApiMessage(mmsg.ID_SIMULATOR_CONFIG, self.__config)
        )
        if self.__verbose:
            print(res)

        # configure other options if set
        if self.__scenario:
            res = self.configure_scenario(self.__scenario)
            if self.__verbose:
                print(res)
        if self.__sensor_config:
            res = self.configure_sensors(self.__sensor_config)
            if self.__verbose:
                print(res)
        if self.__weather:
            res = self.configure_weather(self.__weather)
            if self.__verbose:
                print(res)

    def configure_weather(self, config, set_profile=None):
        """Configure the weather from JSON representation.

        Args:
            config(dict): The configuration JSON to send to the server
            set_profile(str): The profile id to be set

        Returns:
            The response message from the simulator for this configuration.
        """
        if set_profile:
            config['set_profile'] = set_profile
        message = mmsg.ApiMessage(
            mmsg.ID_WEATHER_CONFIG_COMMAND,
            config
        )
        return self.send_command(message)

    def configure_scenario(self, config):
        """Configure the scenario from JSON representation.

        Args:
            config(dict): The scenario configuration to send to the server

        Returns:
            The response message from the simulator for this configuration.
        """
        if self.mode == Mode.MODE_CLOSED_LOOP.value:
            message = mmsg.ApiMessage(
                mmsg.ID_CLOSED_LOOP_CONFIG_COMMAND,
                config
            )
        else:
            message = mmsg.ApiMessage(
                mmsg.ID_REPLAY_CONFIGURE_TRAJECTORY_COMMAND,
                config
            )
        return self.send_command(message)

    def configure_sensors(self, config):
        """Configure the sensor suite from JSON representation.

        Args:
            config(dict): The sensor config JSON to send to the server

        Returns:
            The response message from the simulator for this configuration.
        """
        message = mmsg.ApiMessage(
            mmsg.ID_REPLAY_CONFIGURE_SENSORS_COMMAND,
            config
        )
        return self.send_command(message)

    def reconfigure_sensor(self, config):
        """Re-Configure the sensor included in the config file.

        Args:
            config(dict): The sensor config JSON to send to the server

        Returns:
            The response message from the simulator for this configuration.
        """
        config['_type'] = config['type']
        uid = '{}_{}'.format(config['type'], config['listen_port'])
        try:
            updated_config = self.get_sensor(uid).serialize()
        except KeyError:
            updated_config = {}
        updated_config.update(config)

        sensor = objectfactory.Factory.create_object(updated_config)
        sensor.configure()
        if sensor.enable_streaming:
            if sensor.id not in self.__sensors:
                raise Exception(
                    "{} does not yet exist and cannot be reconfigured".format(sensor.id)
                )

            self.__sensors[sensor.id].set_sensor(sensor)

        message = mmsg.ApiMessage(
            mmsg.ID_REPLAY_RECONFIGURE_SENSOR_COMMAND,
            config
        )
        return self.send_command(message)

    def start(self, start_listening=True, initial_controls=(0, 0, 0, 1)):
        """
        Start the simulation

        Args:
            start_listening(bool): begin sensor threads for listening
            initial_controls(tuple): initial controls to send if
              closed loop mode. set None to skip.
        """
        self.__running = True
        self.configure()
        if self.mode == Mode.MODE_CLOSED_LOOP.value and initial_controls is not None:
            res = self.send_control(*initial_controls)
            if self.__verbose:
                print(res)
        if start_listening:
            self.start_sensor_listening()

    def step(self, steps=1):
        """Step the simulation the specified number of steps.

        Args:
            steps(int): The number of steps to move the simulation

        Raises:
            Exception if the simulator is not currently running

        Returns:
            dict: The response message from the simulator
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

    def send_state(self, frame):
        """Set the state of the simulator and step

        Args:
            frame(dict): The desired state of the simulator

        Raises:
            Exception if the simulator is not currently running

        Returns:
            dict: The response message from the simulator
        """
        if not self.__running:
            raise Exception("Simulator is not running")

        message = mmsg.ApiMessage(
            mmsg.ID_REPLAY_STATE_SIMULATION_COMMAND,
            frame
        )
        return self.send_command(message)

    def stop(self):
        """Stop the simulation and all attached sensors."""
        for sensor_id in self.__sensors.keys():
            self.__sensors[sensor_id].stop()
        self.__client.disconnect()
        self.__running = False

    def send_command(self, command):
        """Send the command to the connected simulator client.

        Args:
            command(ApiMessage): The command to send to the server.

        Returns:
            dict: The command response message from the simulator
        """
        if not self.__client.connected:
            self.__client.connect()
        command.write(self.__client)
        return command.read(self.__client)

    def start_sensor_listening(self):
        """Start all sensors"""
        for sc in self.__sensor_config:
            sc['_type'] = sc['type']
            sensor = objectfactory.Factory.create_object(sc)
            sensor.configure()
            if not sensor.enable_streaming:
                continue
            sensor_thread = SensorThread(
                self.__config['server_ip'],
                sensor,
                verbose=self.__verbose
            )
            sensor_thread.start()
            self.__sensors[sensor.id] = sensor_thread

    @property
    def sensors_ids(self):
        """Get the current list of all sensor ids.

        Returns:
            The list of all sensor ids.
        """
        return self.__sensors.keys()

    @property
    def num_steps(self):
        """Get number of steps in trajectory"""
        if self.mode == Mode.MODE_CLOSED_LOOP.value:
            return 0
        if self.__scenario is None:
            return 0
        return len(self.__scenario)

    def subscribe_to_sensor(self, uid, callback):
        """Subscribe to a single sensor's data ouput in the simulator.

        Args:
            uid(str): The uid of the sensor to subscribe to.
            callback(func): The function that will be called when the sensor's
            data arrives. Should be of the format:
                def my_callback(data):
        """
        self.__sensors[uid].subscribe(callback)

    def get_sensor(self, uid):
        """Get copy of a single sensor configuration by uid

        Args:
            uid(str): The uid of the sensor

        Returns:
            Sensor object
        """
        return self.__sensors[uid].get_sensor()

    def send_control(self, forward: float, right: float, brake: float = 0.0, mode: int = 1):
        """Send controls to ego vehicle

        Args:
            forward:
            right:
            brake:
            mode:

        Returns:
            dict: The command response message from the simulator
        """
        message = mmsg.ApiMessage(
            mmsg.ID_EGO_CONTROL,
            {
                u'forward_amount': forward,
                u'right_amount': right,
                u'brake_amount': brake,
                u'drive_mode': mode
            }
        )
        return self.send_command(message)

    def sample_sensors(self):
        """Send command to sample all sensors

        Raises:
            Exception if the simulator is not currently running

        Returns:
            dict: The command response message from the simulator
        """
        if not self.__running:
            raise Exception("Simulator is not running")

        message = mmsg.ApiMessage(
            mmsg.ID_SAMPLE_SENSORS_COMMAND,
            {}
        )
        return self.send_command(message)

    @classmethod
    def from_file(
            cls,
            simulator: str,
            scenario: str = None,
            sensors: str = None,
            weather: str = None,
            ego: str = None,
            verbose: bool = False
    ):
        """Helper method to construct simulator object from config file paths"""
        with open(simulator) as file:
            config = json.load(file)
            simulator = cls(config, verbose=verbose)
        if scenario:
            with open(scenario) as file:
                simulator.__scenario = json.load(file)
        if sensors:
            with open(sensors) as file:
                simulator.__sensor_config = json.load(file)
        if weather:
            with open(weather) as file:
                simulator.__weather = json.load(file)
        if ego:
            with open(ego) as file:
                simulator.__ego = json.load(file)
        return simulator

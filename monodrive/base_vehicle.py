"""vehicle.py
A simple simulator that will read all sensor values from the connected sensors.
"""
from monodrive.common.client import Client
import monodrive.common.messaging as mmsg
from monodrive.sensors.base_sensor import Sensor


class BaseVehicle(object):
    """Simulator driver that will connect and read all sensors on the
    ego vehicle."""

    def __init__(self, config, sensors):
        """Constructor.

        Args:
            config(dict): The configuration JSON for this simulator instance
            sensors(dict): The configuration JSON for the suit of sensors for
            this simulator instance.
        """
        self.__config = config
        self.__sensor_config = sensors
        self.__sensors = dict()
        self.__client = Client(config['server_ip'], config['server_port'])
        self.__client.connect()
        self.__running = False

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

    def configure(self):
        """Configure the server with the current simulator settings"""
        self.send_command(mmsg.ApiMessage(
            mmsg.ID_REPLAY_CONFIGURE_SENSORS_COMMAND, self.__sensor_config))

    def start(self):
        """Send the sensor configuration and start listening """
        self.__running = True
        self.configure()
        self.start_sensor_listening()

    def start_sensor_listening(self):
        """Start all sensors"""
        for sc in self.__sensor_config:
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

        response = self.send_command(
            mmsg.ApiMessage(mmsg.ID_REPLAY_STEP_SIMULATION_COMMAND,
                            {
                                u'amount': steps
                            }))
        return response

    def send_control(self, forward, right):
        self.send_command(
            mmsg.ApiMessage(mmsg.ID_EGO_CONTROL,
                            {
                                u'forward_amount': forward,
                                u'right_amount': right,
                                u'brake_amount': 0,
                                u'drive_mode': 1
                            }))

    def send_command(self, command):
        """Send the command to the connected simulator client.

        Args:
            command(ApiMessage): The command to send to the server.
        """
        command.write(self.__client)
        return command.read(self.__client)

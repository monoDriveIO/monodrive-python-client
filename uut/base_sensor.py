"""base_sensor.py
Base sensor class for processing data from the simulator
"""
from rx import Observable
import struct
import threading
import traceback
import sys

from uut.client import UUT_Client

from uut.sensors.gps import GPS
from uut.sensors.imu import IMU
from uut.sensors.rpm import RPM
from uut.sensors.radar import Radar

class Sensor(threading.Thread):
    """Base sensor class for processing sensor data from the simulator."""

    def __init__(self, server_ip, config):
        """ Constructor.

        Args:
            server_ip(str): The IP address of the server the sensor data is
            coming from.
            config(dict): A dictionary of configuration values for this sensor
        """
        threading.Thread.__init__(self)
        # The current configuration for this sensor
        self.__config = config
        # The unique ID of this sensor
        self.__id = config['type'] + "_" + str(config['listen_port'])
        # The class of this sensor -- reflection
        self.sensor_class = getattr(sys.modules[__name__], config['type'])
        # The client that is connected to the simulator
        self.__client = UUT_Client(server_ip, config['listen_port'])
        # The event that is fired off when the sensor data arrives
        self.__source = \
            Observable.create(self._init_rx).publish().auto_connect(0)
        # Flag to determine if the sensor should be connected
        self.__running = False

    def str_to_class(self, classname):
        return getattr(sys.modules[__name__], classname)

    @property
    def id(self):
        """Get the unique ID of this sensor.

        Returns:
            The string representation of the unique id.
        """
        return self.__id

    def _init_rx(self, observer):
        """Initialize the reactive publisher"""
        self.observer = observer

    def subscribe(self, callback):
        """Subscribe to the output of this sensor.

        Args:
            callback(func): The function that will be called when the sensor's
            data arrives. Should be of the format:
                def my_callback(data):
            The data will be a tuple of size 3. The first element is the time
            the data arrived, the second element is the game time the data
            occurred, and the third element is the data message.
        """
        self.__source.subscribe(lambda data: callback(data))

    def start(self):
        """Start the client connection for this sensor"""
        print("Starting {0} on {1}".format(self.id, self.name))
        self.__running = True
        self.__client.connect()
        super().start()

    def stop(self):
        """Stop the client connection for this sensor"""
        self.__running = False
        self.__client.disconnect()
        self.join()

    def run(self):
        """Overwrite the base Thread run to start the main read loop for this
        sensor"""
        print("running")
        while self.__running:
            try:
                # Read the header type of the message
                header = self.__client.read(12)
                length, time, game_time = struct.unpack("!IIf", header)
                data = self.__client.read(length - 12)
                # Publish the message to everyone else
                data_dict = self.sensor_class.parse_frame(data, time, game_time)
                self.observer.on_next((time, game_time, data_dict))
                print(self.id + str(data_dict))
            except Exception as e:
                print("{0}: exception {1}".format(self.__id, str(e)))
                traceback.print_exc()
                break

        # Log that this sensor has stopped running
        print("{0}: disconnected".format(self.__id))

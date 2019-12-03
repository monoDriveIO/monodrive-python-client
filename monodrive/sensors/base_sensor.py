"""base_sensor.py
Base sensor class for processing data from the simulator
"""
from rx import Observable
import struct
import threading
import traceback
import sys

from monodrive.common.client import Client

from monodrive.sensors.collision import Collision
from monodrive.sensors.gps import GPS
from monodrive.sensors.imu import IMU
from monodrive.sensors.rpm import RPM
from monodrive.sensors.radar import Radar
from monodrive.sensors.state import State
from monodrive.sensors.ultrasonic import Ultrasonic
from monodrive.sensors.camera import Camera
from monodrive.sensors.lidar import Lidar


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

        self.sensor_type = config['type']
        # The unique ID of this sensor
        self.__id = self.sensor_type + "_" + str(config['listen_port'])
        # The class of this sensor -- reflection
        self.sensor_class = getattr(sys.modules[__name__], config['type'])
        # The client that is connected to the simulator
        self.__client = Client(server_ip, config['listen_port'])
        # The event that is fired off when the sensor data arrives
        self.__source = Observable.create(self._init_rx).publish().auto_connect(0)

        # Flag to determine if the sensor should be connected
        self.__running = False

        self.framing = False
        self.expected_frames_per_step = 1
        self.frame_buffer = []

        if self.sensor_type == "Camera":
            self.sensor_class.width = int(config['stream_dimensions']['x'])
            self.sensor_class.height = int(config['stream_dimensions']['y'])

        if self.sensor_type == "Lidar":
            self.framing = True
            horizontal_resolution = config['horizontal_resolution']
            n_lasers = config['n_lasers']
            channels_per_block = 32
            blocks_per_packet = 12
            number_blocks = 360 / horizontal_resolution * n_lasers / channels_per_block
            number_packets = number_blocks / blocks_per_packet
            # packet_size = int(number_blocks * 1248.0)
            # frame_buffer = []
            self.expected_frames_per_step = int(number_packets)

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
        HEADER_SIZE = 12
        while self.__running:
            try:
                # Check socket for data available
                if not self.__client.data_ready():
                    continue
                # Read the header type of the message
                header = self.__client.read(HEADER_SIZE)
                length, time, game_time = struct.unpack("!IIf", header)
                data = self.__client.read(length - HEADER_SIZE)
                # Publish the message to everyone else
                package_length = length - HEADER_SIZE;
                message = self.sensor_class(self.id, package_length, data, time, game_time)
                self.frame_buffer.append(message)

                if not self.framing:
                    # self.observer.on_next((time, game_time, self.frame_buffer))
                    self.observer.on_next(self.frame_buffer)
                    self.frame_buffer = []
                    # print(self.id + str(message))
                elif self.expected_frames_per_step == len(self.frame_buffer):
                    # self.observer.on_next((time, game_time, self.frame_buffer))
                    self.observer.on_next(self.frame_buffer)
                    self.frame_buffer = []
                    # print(self.id + str(message))


            except Exception as e:
                print("{0}: exception {1}".format(self.__id, str(e)))
                traceback.print_exc()
                break

        # Log that this sensor has stopped running
        print("{0}: disconnected".format(self.__id))

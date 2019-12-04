"""
Lidar module for monoDrive simulator python client
"""

# lib
import numpy as np
import objectfactory

# src
from monodrive.sensors import Sensor, DataFrame


class LidarFrame(DataFrame):
    def __init__(self):
        self.sensor_id = None
        self.timestamp = None
        self.game_time = None
        self.data = None


@objectfactory.Factory.register_class
class Lidar(Sensor):
    """Lidar sensor"""

    horizontal_resolution = objectfactory.Field()
    n_lasers = objectfactory.Field()

    def configure(self):
        """
        configure framing and calculate expected frames per step
        """
        self.framing = True
        channels_per_block = 32
        blocks_per_packet = 12
        number_blocks = 360 / self.horizontal_resolution * self.n_lasers / channels_per_block
        number_packets = number_blocks / blocks_per_packet
        self.expected_frames_per_step = int(number_packets)

    def parse(self, data: bytes, package_length: int, time: int, game_time: int) -> DataFrame:
        """
        Parse data from lidar sensor

        Args:
            data:
            package_length:
            time:
            game_time:

        Returns:
            parsed LidarFrame object
        """
        frame = LidarFrame()
        frame.sensor_id = self.id
        frame.timestamp = time
        frame.game_time = game_time
        frame.data = data

        # TODO -- finish parser

        return frame

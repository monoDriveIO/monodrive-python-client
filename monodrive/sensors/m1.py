"""
M1 module for monoDrive simulator python client
"""

# lib
import math
import numpy as np
import struct
import objectfactory

# src
from monodrive.sensors import Sensor, DataFrame

# constants
NUM_POINTS = 78750


class M1Frame(DataFrame):
    def __init__(self):
        self.sensor_id = None
        self.timestamp = None
        self.game_time = None
        self.points: [LidarPoint] = []


class LidarPoint:
    """Class for single parsed point from LiDAR point cloud"""

    def __init__(self, time: int=0, x: float=0, y: float=0, z: float=0, intensity: int=0, laser_id: int=0):
        self.time = time
        self.x = x
        self.y = y
        self.z = z
        self.intensity = intensity
        self.laser_id = laser_id


@objectfactory.Factory.register_class
class RSM1Lidar(Sensor):
    """RSM1 sensor"""

    def configure(self):
        """
        configure framing and calculate expected frames per step
        """
        print("noop")

    def parse(self, data: [bytes], package_length: int, time: int, game_time: int) -> DataFrame:
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
        frame = M1Frame()
        frame.sensor_id = self.id
        frame.timestamp = time
        frame.game_time = game_time

        point_count, = struct.unpack(">I", data[0][:4])
        frame.points = [LidarPoint(b[0], b[1], b[2], b[3], b[4], b[5]) for b in struct.iter_unpack("IfffBB", data[0][4:])]
        # stride = 4*4+2
        # stride = 6
        # for i in range(point_count):
        #     point = LidarPoint()
        #     point.time = lidar_data[i*stride]
        #     point.x = lidar_data[i*stride+1]
        #     point.y = lidar_data[i*stride+2]
        #     point.z = lidar_data[i*stride+3]
        #     point.intensity = lidar_data[i*stride+4]
        #     point.laser_id = lidar_data[i*stride+5]
        #     frame.points.append(point)

        return frame



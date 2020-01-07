"""
Lidar module for monoDrive simulator python client
"""

# lib
import math
import numpy as np
import struct
import objectfactory

# src
from monodrive.sensors import Sensor, DataFrame

# constants
CHANNELS_PER_BLOCK = 32
BLOCKS_PER_PACKET = 12
PACKET_SIZE = 1206
LASER_ANGLES = [-10, 0.67, -8.67, 2, -7.33, 3.33, -6, 4.67, -4.67, 6, -3.33,
                7.33, -2, 8.67, -0.67, 10]
VERTICAL_CORRECTION = [7.4, -0.9, 6.5, -1.8, 5.5, -2.7, 4.6, -3.7, 3.7, -4.6,
                       2.7, -5.5, 1.8, -6.5, 0.9, -7.4]


class LidarFrame(DataFrame):
    def __init__(self):
        self.sensor_id = None
        self.timestamp = None
        self.game_time = None
        self.points: [LidarPoint] = []


class LidarPoint:
    """Class for single parsed point from LiDAR point cloud"""

    def __init__(self, x: float, y: float, z: float, intensity: float):
        self.x = x
        self.y = y
        self.z = z
        self.intensity = intensity


class LidarDataBlockPoint:
    """Class for a single data point from LiDAR"""

    def __init__(self, d: int, i: int):
        self.d = d
        self.i = i


class LidarDataBlock:
    """Class for a block of 16 data points from LiDAR"""

    def __init__(self):
        self.points = []
        self.flag = None
        self.azimuth = None


class LidarPacket:
    """Class for an entire packet of 12 data blocks from LiDAR"""

    def __init__(self):
        self.blocks = []
        self.timestamp = None
        self.flag = None


@objectfactory.Factory.register_class
class Lidar(Sensor):
    """Lidar sensor"""

    horizontal_resolution = objectfactory.Field()
    n_lasers = objectfactory.Field()

    def configure(self):
        """
        configure framing and calculate expected frames per step
        """
        number_blocks = (360. / self.horizontal_resolution
                         * self.n_lasers / CHANNELS_PER_BLOCK)
        number_packets = number_blocks / BLOCKS_PER_PACKET
        self.blocks_per_frame = math.ceil(number_packets)

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

        # parse each received packet
        for chunk in [data[i:i + PACKET_SIZE] for i in range(0, len(data), PACKET_SIZE)]:
            packet = self._parse_packet_data(chunk)

            for block in packet.blocks:
                # indicates null end of sweep from simulator
                if block.azimuth >= 36000:
                    continue
                for i, point in enumerate(block.points):
                    pitch = LASER_ANGLES[i % 16]
                    distance = point.d * 2.0
                    intensity = point.i
                    azimuth = block.azimuth / 100.0

                    # two rows of data per packet
                    if i < len(block.points) / 2:
                        azimuth += self.horizontal_resolution

                    # convert to cartesian
                    x, y, z = _spherical_to_cartesian(azimuth, pitch, distance)

                    # add to final point set for frame
                    frame.points.append(
                        LidarPoint(x, y, z, intensity)
                    )

        return frame

    def _parse_packet_data(self, packet_data):
        """
        Parse a 1206 byte packet from LiDAR into a `LidarPacket`.
        Args:
            packet_data:

        Returns:
            Parsed lidar packet object
        """
        lidar_data = struct.unpack("=" + 12 * ("HH" + 32 * "HB") + "IH", packet_data)
        lp = LidarPacket()
        lp.flag = lidar_data[-1]
        lp.timestamp = lidar_data[-2]

        stride = 2 + 32 * 2
        for i in range(12):
            lp.blocks.append(LidarDataBlock())
            lp.blocks[-1].flag = lidar_data[i * stride]
            lp.blocks[-1].azimuth = lidar_data[i * stride + 1]
            for j in range(i * stride + 2, i * stride + 65, 2):
                lp.blocks[-1].points.append(
                    LidarDataBlockPoint(lidar_data[j], lidar_data[j + 1])
                )
        return lp

    def _get_laser_angles(self):
        """
        Helper function to get pitch associated with each laser

        Returns:
        """
        # TODO: support 16 or 32 
        return LASER_ANGLES


def _spherical_to_cartesian(azimuth: float, elevation: float, distance: float):
    """Convert a LiDAR point from azimuth, elevation, distance into x, y, z
    Cartesian coordinates.

    Args:
        azimuth(float): The azimuth angle associated with this point.
        elevation(float): The elevation angle associated with this point.
        distance(float): The distance (radius) for this point
    Returns:
        A tuple of the point in x, y, z Cartesian coordinates.
    """
    # If the distance was 0, then there was no return for this point
    if distance == 0:
        return 0, 0, 0

    omega = np.radians(elevation)
    alpha = np.radians(azimuth)
    x = distance * math.cos(omega) * math.sin(alpha)
    y = distance * math.cos(omega) * math.cos(alpha)
    z = distance * math.sin(omega)
    return x, y, z

__author__ = "monoDrive"
__copyright__ = "Copyright (C) 2018 monoDrive"
__license__ = "MIT"
__version__ = "1.0"

# lib
import struct
import objectfactory

# src
from monodrive.sensors import Sensor, DataFrame


class IMUFrame(DataFrame):
    def __init__(self):
        self.sensor_id = None
        self.timestamp = None
        self.game_time = None
        self.acceleration_vector = None
        self.angular_velocity_vector = None
        self.timer = None


@objectfactory.Factory.register_class
class IMU(Sensor):
    """IMU sensor"""

    def parse(self, data: bytes, package_length: int, time: int, game_time: int) -> DataFrame:
        """
        Parse data from IMU sensor

        Args:
            data:
            package_length:
            time:
            game_time:

        Returns:
            parsed GPSFrame object
        """
        fmt = '=ffffffih'
        data = list(struct.unpack(fmt, data[1:31]))
        accel_x = data[0]
        accel_y = data[1]
        accel_z = data[2]
        ang_rate_x = data[3]
        ang_rate_y = data[4]
        ang_rate_z = data[5]
        timer = data[6]
        check_sum = data[7]

        frame = IMUFrame()
        frame.sensor_id = self.id
        frame.timestamp = time
        frame.game_time = game_time
        frame.acceleration_vector = [accel_x, accel_y, accel_z]
        frame.angular_velocity_vector = [ang_rate_x, ang_rate_y, ang_rate_z]
        frame.timer = timer

        return frame

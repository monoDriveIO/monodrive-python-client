"""
RPM sensor module for monoDrive simulator python client
"""

# lib
import struct
import objectfactory

# src
from monodrive.sensors import Sensor, DataFrame


class RPMFrame(DataFrame):
    def __init__(self):
        self.sensor_id = None
        self.timestamp = None
        self.game_time = None
        self.wheel_number = None
        self.wheel_speed = None


@objectfactory.Factory.register_class
class RPM(Sensor):
    """RPM sensor"""

    def parse(self, data: bytes, package_length: int, time: int, game_time: int) -> DataFrame:
        """
        Parse data from RPM sensor

        Args:
            data:
            package_length:
            time:
            game_time:

        Returns:
            parsed RPMFrame object
        """
        frame = RPMFrame()
        frame.wheel_number, frame.wheel_speed = list(struct.unpack('=if', data))
        frame.sensor_id = self.id
        frame.timestamp = time
        frame.game_time = game_time
        return frame

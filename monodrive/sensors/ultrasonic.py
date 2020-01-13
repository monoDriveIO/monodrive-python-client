"""
Ultrasonic sensor module for monoDrive simulator python client
"""

# lib
import json
import objectfactory

# src
from monodrive.sensors import Sensor, DataFrame


class UltrasonicFrame(DataFrame):
    def __init__(self):
        self.sensor_id = None
        self.timestamp = None
        self.game_time = None
        self.ranges = None


@objectfactory.Factory.register_class
class Ultrasonic(Sensor):
    """Ultrasonic sensor"""

    def parse(self, data: bytes, package_length: int, time: int, game_time: int) -> DataFrame:
        """
        Parse data from ultrasonic sensor

        Args:
            data:
            package_length:
            time:
            game_time:

        Returns:
            parsed UltrasonicFrame object
        """
        json_raw = data.decode('utf8').replace("'", '"')
        parsed_json = json.loads(json_raw)

        frame = UltrasonicFrame()
        frame.sensor_id = self.id
        frame.timestamp = time
        frame.game_time = game_time
        frame.ranges = parsed_json['ranges']

        # TODO -- finish parsing method

        return frame

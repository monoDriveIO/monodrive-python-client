"""
Collision sensor module for monoDrive simulator python client
"""

# lib
import json
import objectfactory

# src
from monodrive.sensors import Sensor, DataFrame


class CollisionFrame(DataFrame):
    def __init__(self):
        self.sensor_id = None
        self.timestamp = None
        self.game_time = None


@objectfactory.Factory.register_class
class Collision(Sensor):
    """Collision sensor"""

    def parse(self, data: bytes, package_length: int, time: int, game_time: int) -> DataFrame:
        """
        Parse data from collision sensor

        Args:
            data:
            package_length:
            time:
            game_time:

        Returns:
            parsed CollisionFrame object
        """
        json_raw = data.decode('utf8').replace("'", '"')
        parsed_json = json.loads(json_raw)

        frame = CollisionFrame()
        frame.sensor_id = self.id
        frame.timestamp = parsed_json['time']
        frame.game_time = parsed_json['game_time']

        return frame

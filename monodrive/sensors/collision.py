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
        self.acceleration = None
        self.brake_input = None
        self.collision = None
        self.distance = None
        self.forward_acceleration = None
        self.forward_velocity = None
        self.name = None
        self.relative_velocity = None
        self.sample_count = None
        self.targets = None
        self.throttle_input = None
        self.time_to_collision = None
        self.velocity = None
        self.wheel_input = None


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
        frame.acceleration = parsed_json['acceleration']
        frame.brake_input = parsed_json['brake_input']
        frame.collision = parsed_json['collision']
        frame.distance = parsed_json['distance']
        frame.forward_acceleration = parsed_json['forward_acceleration']
        frame.forward_velocity = parsed_json['forward_velocity']
        frame.name = parsed_json['name']
        frame.relative_velocity = parsed_json['relative_velocity']
        frame.sample_count = parsed_json['sample_count']
        frame.targets = parsed_json['targets']
        frame.throttle_input = parsed_json['throttle_input']
        frame.time_to_collision = parsed_json['time_to_collision']
        frame.velocity = parsed_json['velocity']
        frame.wheel_input = parsed_json['wheel_input']
        frame.raw_data = parsed_json
        return frame

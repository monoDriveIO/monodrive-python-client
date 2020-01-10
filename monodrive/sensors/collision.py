"""
Collision sensor module for monoDrive simulator python client
"""

# lib
import json
import objectfactory

# src
from monodrive.sensors import Sensor, DataFrame


@objectfactory.Factory.register_class
class CollisionFrameTarget(objectfactory.Serializable):
    """Data model for collision sensor target"""
    acceleration = objectfactory.Field()
    brake_input = objectfactory.Field()
    collision = objectfactory.Field()
    distance = objectfactory.Field()
    forward_acceleration = objectfactory.Field()
    forward_velocity = objectfactory.Field()
    name = objectfactory.Field()
    relative_velocity = objectfactory.Field()
    throttle_input = objectfactory.Field()
    time_to_collision = objectfactory.Field()
    velocity = objectfactory.Field()
    wheel_input = objectfactory.Field()


@objectfactory.Factory.register_class
class CollisionFrame(DataFrame, CollisionFrameTarget):
    """Data frame for collision sensor"""
    sensor_id = objectfactory.Field()
    timestamp = objectfactory.Field()
    game_time = objectfactory.Field()
    targets = objectfactory.List(field_type=CollisionFrameTarget)


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
        frame.deserialize(parsed_json)
        frame.sensor_id = self.id
        return frame

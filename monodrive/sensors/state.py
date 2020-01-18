"""
State sensor module for monoDrive simulator python client
"""

# lib
import json
import objectfactory

# src
from monodrive.sensors import Sensor, DataFrame


@objectfactory.Factory.register_class
class StateFrameWheel(objectfactory.Serializable):
    """Data model for state sensor frame item wheel"""
    wheel_id = objectfactory.Field(name="id")
    orientation = objectfactory.Field()


@objectfactory.Factory.register_class
class StateFrameItem(objectfactory.Serializable):
    """Data model for state sensor frame item"""
    name = objectfactory.Field()
    tags = objectfactory.Field()
    velocity = objectfactory.Field()
    wheel_speed = objectfactory.Field()
    position = objectfactory.Field()
    angular_velocity = objectfactory.Field()
    wheels = objectfactory.List(field_type=StateFrameWheel)


@objectfactory.Factory.register_class
class StateFrame(DataFrame, objectfactory.Serializable):
    sensor_id = objectfactory.Field()
    timestamp = objectfactory.Field()
    game_time = objectfactory.Field()
    object_list = objectfactory.List(name='frame', field_type=StateFrameItem)


@objectfactory.Factory.register_class
class State(Sensor):
    """State sensor"""

    def parse(self, data: [bytes], package_length: int, time: int, game_time: int) -> DataFrame:
        """
        Parse data from state sensor

        Args:
            data:
            package_length:
            time:
            game_time:

        Returns:
            parsed StateFrame object
        """
        data = data[0]
        json_raw = data.decode('utf8').replace("'", '"')
        parsed_json = json.loads(json_raw)
        frame = StateFrame()
        frame.deserialize(parsed_json)
        frame.sensor_id = self.id
        return frame

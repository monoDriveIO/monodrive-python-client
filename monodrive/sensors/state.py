"""
State sensor module for monoDrive simulator python client
"""

# lib
import json
import objectfactory

# src
from monodrive.sensors import Sensor, DataFrame


@objectfactory.Factory.register_class
class StateFrameObject(objectfactory.Serializable):
    """Data model for state sensor frame object"""
    name = objectfactory.Field()
    odometry = objectfactory.Field()
    tags = objectfactory.Field()
    oobbs = objectfactory.Field()


@objectfactory.Factory.register_class
class StateFrameWheel(objectfactory.Serializable):
    """Data model for state sensor frame vehicle wheel"""
    wheel_id = objectfactory.Field(name="id")
    speed = objectfactory.Field()
    pose = objectfactory.Field()


@objectfactory.Factory.register_class
class StateFrameVehicle(objectfactory.Serializable):
    """Data model for state sensor frame vehicle"""
    state = objectfactory.Nested(field_type=StateFrameObject)
    wheels = objectfactory.List(field_type=StateFrameWheel)


@objectfactory.Factory.register_class
class StateFrameData(objectfactory.Serializable):
    """Data model for state sensor frame object data"""
    objects = objectfactory.List(field_type=StateFrameObject)
    vehicles = objectfactory.List(field_type=StateFrameVehicle)


@objectfactory.Factory.register_class
class StateFrame(DataFrame, objectfactory.Serializable):
    sensor_id = objectfactory.Field()
    time = objectfactory.Field()
    game_time = objectfactory.Field()
    sample_count = objectfactory.Field()
    frame = objectfactory.Nested(field_type=StateFrameData)


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

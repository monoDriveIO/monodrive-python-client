"""
Ultrasonic sensor module for monoDrive simulator python client
"""

# lib
import json
import objectfactory

# src
from monodrive.sensors import Sensor, DataFrame


@objectfactory.Factory.register_class
class UltrasonicFrameTarget(objectfactory.Serializable):
    range = objectfactory.Field()


@objectfactory.Factory.register_class
class UltrasonicFrame(DataFrame, objectfactory.Serializable):
    sensor_id = objectfactory.Field()
    time = objectfactory.Field()
    game_time = objectfactory.Field()
    targets = objectfactory.List(field_type=UltrasonicFrameTarget)


@objectfactory.Factory.register_class
class Ultrasonic(Sensor):
    """Ultrasonic sensor"""

    send_processed_data = objectfactory.Field()

    def configure(self):
        if self.send_processed_data:
            self.blocks_per_frame = 2

    def parse(self, data: [bytes], package_length: int, time: int, game_time: int) -> DataFrame:
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
        data = data[0]

        frame = UltrasonicFrame()

        if self.send_processed_data:
            json_raw = data.decode('utf8').replace("'", '"')
            parsed_json = json.loads(json_raw)
            frame.deserialize(parsed_json)

        frame.time = time
        frame.game_time = game_time
        frame.sensor_id = self.id

        return frame

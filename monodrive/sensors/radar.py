"""
Radar module for monoDrive simulator python client
"""

# lib
import json
import objectfactory

# src
from monodrive.sensors import Sensor, DataFrame


@objectfactory.Factory.register_class
class RadarFrameTarget(objectfactory.Serializable):
    range = objectfactory.Field()
    aoa = objectfactory.Field()
    velocity = objectfactory.Field()
    rcs = objectfactory.Field()
    target_ids = objectfactory.Field()


@objectfactory.Factory.register_class
class RadarFrame(DataFrame, objectfactory.Serializable):
    sensor_id = objectfactory.Field()
    time = objectfactory.Field()
    game_time = objectfactory.Field()
    targets = objectfactory.List(
        name='target_list',
        field_type=RadarFrameTarget
    )
    groundtruth_targets = objectfactory.List(
        name='gt_targets',
        field_type=RadarFrameTarget
    )


@objectfactory.Factory.register_class
class Radar(Sensor):
    """Radar sensor"""

    def parse(self, data: [bytes], package_length: int, time: int, game_time: int) -> DataFrame:
        """
        Parse data from radar sensor

        Args:
            data:
            package_length:
            time:
            game_time:

        Returns:
            parsed RadarFrame object
        """
        data = data[0]
        json_raw = data.decode('utf8').replace("'", '"')
        parsed_json = json.loads(json_raw)

        frame = RadarFrame()
        frame.deserialize(parsed_json)
        frame.time = time
        frame.game_time = game_time
        frame.sensor_id = self.id

        return frame

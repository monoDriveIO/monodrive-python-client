"""
Radar module for monoDrive simulator python client
"""

# lib
import json
import objectfactory

# src
from monodrive.sensors import Sensor, DataFrame


class RadarFrame(DataFrame):
    def __init__(self):
        self.sensor_id = None
        self.timestamp = None
        self.game_time = None
        self.ranges = None
        self.velocities = None
        self.aoa_list = None
        self.rcs_list = None


@objectfactory.Factory.register_class
class Radar(Sensor):
    """Radar sensor"""

    def parse(self, data: bytes, package_length: int, time: int, game_time: int) -> DataFrame:
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
        json_raw = data.decode('utf8').replace("'", '"')
        parsed_json = json.loads(json_raw)

        frame = RadarFrame()
        frame.sensor_id = self.id
        frame.timestamp = parsed_json['time']
        frame.game_time = parsed_json['game_time']
        message = parsed_json['message']
        frame.ranges = message['ranges']
        frame.velocities = message['velocities']
        frame.aoa_list = message['aoas']
        frame.rcs_list = message['rcs']

        return frame

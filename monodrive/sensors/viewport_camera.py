"""
ViewportCamera sensor module (stubb) for monoDrive simulator python client
"""

# lib
import json
import objectfactory

# src
from monodrive.sensors import Sensor#, DataFrame


#class ViewportFrame(DataFrame):
#    def __init__(self):
#        self.sensor_id = None
#        self.timestamp = None
#        self.game_time = None
#        self.frame= None


@objectfactory.Factory.register_class
class ViewportCamera(Sensor):
    """ViewportCamera sensor"""

    def parse(self, data: bytes, package_length: int, time: int, game_time: int):
        """
        Parse data from ViewportCamera sensor

        Args:
            data:
            package_length:
            time:
            game_time:

        Returns:
            'fake' parsed frame object
        """
        frame = None

        return frame
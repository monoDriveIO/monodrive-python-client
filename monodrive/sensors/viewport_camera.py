"""
ViewportCamera sensor module (stubb) for monoDrive simulator python client
"""

# lib
import json
import objectfactory

# src
from monodrive.sensors import Sensor  # , DataFrame


@objectfactory.Factory.register_class
class ViewportCamera(Sensor):
    """ViewportCamera sensor"""

    def configure(self):
        """
        Configure ViewportCamera sensor
        """
        self.streamable = False

    def parse(self, data: [bytes], package_length: int, time: int, game_time: int):
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
        return None

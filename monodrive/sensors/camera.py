"""
Camera module for monoDrive simulator python client
"""

# lib
import numpy as np
import objectfactory

# src
from monodrive.sensors import Sensor, DataFrame


class CameraFrame(DataFrame):
    def __init__(self):
        self.sensor_id = None
        self.timestamp = None
        self.game_time = None
        self.image = None


@objectfactory.Factory.register_class
class CameraStreamDimensions(objectfactory.Serializable):
    """Data model for camera stream dimensions"""
    x = objectfactory.Field()
    y = objectfactory.Field()


@objectfactory.Factory.register_class
class Camera(Sensor):
    """Camera sensor"""
    stream_dimensions = objectfactory.Nested(field_type=CameraStreamDimensions)
    channels = objectfactory.Field()

    def parse(self, data: bytes, package_length: int, time: int, game_time: int) -> DataFrame:
        """
        Parse data from camera sensor

        Args:
            data:
            package_length:
            time:
            game_time:

        Returns:
            parsed CameraFrame object
        """
        frame = CameraFrame()

        frame.sensor_id = self.id
        frame.time_stamp = time
        frame.game_time = game_time

        # get num channels
        num_channels = {
            'rgba': 4,
            'bgra': 4,
            'gray': 1
        }.get(self.channels, None)
        if num_channels is None:
            raise ValueError('Camera channels type: {} not supported'.format(self.channels))

        # validate complete data
        if len(data) != self.stream_dimensions.y * self.stream_dimensions.x * num_channels:
            print("sensor:{} , received wrong image size".format(self.sensor_id))
            return frame

        # do parse
        im = np.array(bytearray(data), dtype=np.uint8)
        im = np.reshape(
            im,
            (int(self.stream_dimensions.y), int(self.stream_dimensions.x), num_channels)
        )
        im = im[:, :, :3]
        frame.image = im

        return frame

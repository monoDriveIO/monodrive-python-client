"""
Camera module for monoDrive simulator python client
"""

# lib
import numpy as np
import json
import objectfactory

# src
from monodrive.sensors import Sensor, DataFrame


class CameraFrame(DataFrame):
    def __init__(self):
        self.sensor_id = None
        self.timestamp = None
        self.game_time = None
        self.image = None
        self.annotation = None


@objectfactory.Factory.register_class
class CameraStreamDimensions(objectfactory.Serializable):
    """Data model for camera stream dimensions"""
    x = objectfactory.Field()
    y = objectfactory.Field()


@objectfactory.Factory.register_class
class AnnotationDetails(objectfactory.Serializable):
    desired_tags = objectfactory.Field(default=[])
    include_annotation = objectfactory.Field(default=False)


@objectfactory.Factory.register_class
class Camera(Sensor):
    """Camera sensor"""
    stream_dimensions = objectfactory.Nested(field_type=CameraStreamDimensions)
    annotation = objectfactory.Nested(field_type=AnnotationDetails, default=None)
    channels = objectfactory.Field()

    def parse(self, data: [bytes], package_length: int, time: int, game_time: int) -> DataFrame:
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
        if len(data[0]) != self.stream_dimensions.y * self.stream_dimensions.x * num_channels:
            print('sensor: {}, received wrong image size: {}'.format(self.id, len(data[0])))
            return frame

        # do parse
        im = np.array(bytearray(data[0]), dtype=np.uint8)
        im = np.reshape(
            im,
            (int(self.stream_dimensions.y), int(self.stream_dimensions.x), num_channels)
        )
        im = im[:, :, :3]
        frame.image = im

        if len(data) == 2:
            json_raw = data[1].decode('utf8').replace("'", '"')
            frame.annotation = json.loads(json_raw)

        return frame

    def configure(self):
        if self.annotation is None:
            return
        if self.annotation.include_annotation:
            self.blocks_per_frame = 2


@objectfactory.Factory.register_class
class SemanticCamera(Camera):
    """Semantic Camera sensor"""

    def configure(self):
        """
        configure semantic camera
        """
        self.channels = 'gray'

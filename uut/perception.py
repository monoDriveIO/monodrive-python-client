__author__ = "monoDrive"
__copyright__ = "Copyright (C) 2018 monoDrive"
__license__ = "MIT"
__version__ = "1.0"

from uut.sensors.camera import Camera
import numpy as np
import matplotlib.pyplot as plt

class Perception(object):
    def __init__(self, sensor_ids):
        self.sensor_ids = sensor_ids
        self.camera_list = []
        self.camera_list.append(Camera)

    def on_update(self, frame):
        pass

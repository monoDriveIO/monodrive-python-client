__author__ = "monoDrive"
__copyright__ = "Copyright (C) 2018 monoDrive"
__license__ = "MIT"
__version__ = "1.0"

from monodrive.sensors.camera import Camera
import matplotlib.pyplot as plt


class Perception(object):
    def __init__(self, sensor_ids):
        self.sensor_ids = sensor_ids
        self.camera_list = []
        self.camera_list.append(Camera)

    def on_update(self, frame):
        if frame:
            print("Perception system with image size {0}".format(len(frame[0].image)))
            plt.imshow(frame[0].image)
            plt.draw()
            plt.pause(0.0001)
            plt.clf()
        else:
            print("no image")

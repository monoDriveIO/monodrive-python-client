__author__ = "monoDrive"
__copyright__ = "Copyright (C) 2018 monoDrive"
__license__ = "MIT"
__version__ = "1.0"

import json
import numpy as np
import pickle


class Camera(object):

    def __init__(self, sensor_id, package_length, frame, time_stamp, game_time):
        if frame:
            self.sensor_id = sensor_id
            self.time_stamp = time_stamp
            self.game_time = game_time
            if len(frame) == self.height * self.width * 4:
                image = np.array(bytearray(frame), dtype=np.uint8).reshape(self.height, self.width, 4)
            else:
                image = None
                print("sensor:{0} , received wrong image size")
            #self.image = pickle.dumps(image, protocol=-1)
            self.image = image
__author__ = "monoDrive"
__copyright__ = "Copyright (C) 2018 monoDrive"
__license__ = "MIT"
__version__ = "1.0"


class Lidar(object):

    def __init__(self, sensor_id, package_length, frame, time_stamp, game_time):
        if frame:
            self.sensor_id = sensor_id
            self.time_stamp = time_stamp
            self.game_time = game_time
            self.block = frame


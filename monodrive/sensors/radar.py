__author__ = "monoDrive"
__copyright__ = "Copyright (C) 2018 monoDrive"
__license__ = "MIT"
__version__ = "1.0"

import json


class Radar(object):

    def __init__(self, sensor_id, package_length, frame, time_stamp, game_time):
        if frame:
            json_raw = frame.decode('utf8').replace("'", '"')
            parsed_json = json.loads(json_raw)
            self.id = sensor_id
            self.time_stamp = parsed_json['time']
            self.game_time = parsed_json['game_time']
            message = parsed_json['message']
            self.ranges = message['ranges']
            self.velocities = message['velocities']
            self.aoa_list = message['aoas']
            self.rcs_list = message['rcs']

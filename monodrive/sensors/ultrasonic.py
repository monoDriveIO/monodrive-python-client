__author__ = "monoDrive"
__copyright__ = "Copyright (C) 2018 monoDrive"
__license__ = "MIT"
__version__ = "1.0"

import json


class Ultrasonic(object):

    def __init__(self, sensor_id, package_length, frame, time_stamp, game_time):
        if frame:
            json_raw = frame.decode('utf8').replace("'", '"')
            parsed_json = json.loads(json_raw)
            print(parsed_json)
            self.sensor_id = sensor_id
            self.time_stamp = time_stamp
            self.game_time = game_time
            self.ranges = parsed_json['ranges']
            #for r in frame['ranges']:
            #    self.ranges.append(r)
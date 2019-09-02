__author__ = "monoDrive"
__copyright__ = "Copyright (C) 2018 monoDrive"
__license__ = "MIT"
__version__ = "1.0"

import struct


class RPM(object):

    @classmethod
    def parse_frame(cls, frame, time_stamp, game_time):
        wheel_number, wheel_speed = list(struct.unpack('=if', frame))
        data_dict = {
            'time_stamp': time_stamp,
            'game_time': game_time,
            'wheel_number': wheel_number,
            'wheel_rpm': wheel_speed
        }
        return data_dict
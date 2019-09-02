__author__ = "monoDrive"
__copyright__ = "Copyright (C) 2018 monoDrive"
__license__ = "MIT"
__version__ = "1.0"

import struct


class Radar(object):

    @classmethod
    def parse_frame(cls, frame, time_stamp, game_time):
        print(len(frame))
        nTargets = 10*4
        fmt = '<' + str(nTargets) + 'f'
        ranges, velocities, aoas, rcs = list(struct.unpack(fmt, frame))
        data_dict = {
            'time_stamp': time_stamp,
            'game_time': game_time,
            'ranges': ranges,
            'velocities': velocities,
            'aoas': aoas,
            'rcs' : rcs
        }
        return data_dict
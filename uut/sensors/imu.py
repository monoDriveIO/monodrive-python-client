__author__ = "monoDrive"
__copyright__ = "Copyright (C) 2018 monoDrive"
__license__ = "MIT"
__version__ = "1.0"

import struct


class IMU(object):

    @classmethod
    def parse_frame(cls, frame, time_stamp, game_time):
        fmt = '=ffffffih'
        accel_x, accel_y, accel_z, ang_rate_x, ang_rate_y, ang_rate_z, timer, check_sum = list(
            struct.unpack(fmt, frame[1:31]))
        acceleration_vector = [accel_x, accel_y, accel_z]
        angular_velocity_vector = [ang_rate_x, ang_rate_y, ang_rate_z]
        data_dict = {
            'time_stamp': time_stamp,
            'game_time': game_time,
            'acceleration_vector': acceleration_vector,
            'angular_velocity_vector': angular_velocity_vector,
            'timer': timer
        }
        return data_dict
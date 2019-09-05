__author__ = "monoDrive"
__copyright__ = "Copyright (C) 2018 monoDrive"
__license__ = "MIT"
__version__ = "1.0"

import struct


class IMU(object):
    def __init__(self, sensor_id, package_length, frame, time_stamp, game_time):
        fmt = '=ffffffih'
        data = list(struct.unpack(fmt, frame[1:31]))
        accel_x = data[0]
        accel_y = data[1]
        accel_z = data[2]
        ang_rate_x = data[3]
        ang_rate_y = data[4]
        ang_rate_z = data[5]
        self.timer = data[6]
        check_sum = data[7]

        self.acceleration_vector = [accel_x, accel_y, accel_z]
        self.angular_velocity_vector = [ang_rate_x, ang_rate_y, ang_rate_z]
        self.sensor_id = sensor_id

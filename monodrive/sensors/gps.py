__author__ = "monoDrive"
__copyright__ = "Copyright (C) 2018 monoDrive"
__license__ = "MIT"
__version__ = "1.0"

import numpy as np
import struct


class GPS(object):
    def __init__(self, sensor_id, package_length, frame, time_stamp, game_time):
        if frame:
            fmt = '=chhcdddfffffffhhcch'
            preamble, MSG_POS_LLH, sensor_id, payload_length, lat, lng, elev, loc_x, loc_y, for_x, for_y, for_z, ego_yaw, speed, \
            h_ac, v_ac, sats, status, crc = list(struct.unpack(fmt, frame))

            forward_vector = np.array([for_x, for_y, for_z])
            world_location = np.array([loc_x / 100.0, loc_y / 100.0, 0.0])
            self.time_stamp = time_stamp
            self.game_time = game_time
            self.sensor_id = sensor_id
            self.lat = lat
            self.lng = lng
            self.elevation = elev
            self.forward_vector = forward_vector
            self.world_location = world_location
            self.ego_yaw = ego_yaw
            self.speed = speed
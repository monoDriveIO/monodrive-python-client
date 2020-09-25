"""
GPS module for monoDrive simulator python client
"""

# lib
import numpy as np
import struct
import objectfactory

# src
from monodrive.sensors import Sensor, DataFrame


class GPSFrame(DataFrame):
    def __init__(self):
        self.sensor_id = None
        self.timestamp = None
        self.game_time = None
        self.lat = None
        self.lng = None
        self.elevation = None
        self.forward_vector = None
        self.world_location = None
        self.ego_yaw = None
        self.speed = None


@objectfactory.Factory.register_class
class GPS(Sensor):
    """GPS sensor"""

    def parse(self, data: [bytes], package_length: int, time: int, game_time: int) -> DataFrame:
        """
        Parse data from GPS sensor

        Args:
            data: 
            package_length: 
            time: 
            game_time: 

        Returns:
            parsed GPSFrame object
        """
        data = data[0]
        fmt = '>chhcdddfffffffhhcch'
        preamble, MSG_POS_LLH, sensor_id, payload_length, lat, lng, elev, loc_x, loc_y, for_x, for_y, for_z, ego_yaw, speed, \
        h_ac, v_ac, sats, status, crc = list(struct.unpack(fmt, data))
        forward_vector = np.array([for_x, for_y, for_z])
        world_location = np.array([loc_x / 100.0, loc_y / 100.0, 0.0])

        frame = GPSFrame()
        frame.sensor_id = self.id
        frame.timestamp = time
        frame.game_time = game_time
        frame.lat = lat
        frame.lng = lng
        frame.elevation = elev
        frame.forward_vector = forward_vector
        frame.world_location = world_location
        frame.ego_yaw = ego_yaw
        frame.speed = speed

        return frame

__author__ = "monoDrive"
__copyright__ = "Copyright (C) 2018 monoDrive"
__license__ = "MIT"
__version__ = "1.0"

import json



class State(object):

    def __init__(self, sensor_id, package_length, frame, time_stamp, game_time):
        if frame:
            json_raw = frame.decode('utf8').replace("'", '"')
            parsed_json = json.loads(json_raw)
            self.id = sensor_id
            self.time_stamp = parsed_json['time']
            self.game_time = parsed_json['game_time']
            frame = parsed_json['frame']
            self.object_list = []
            for item in frame:
                self.object_list.append(ScenarioItem(item))

'''
{'name': 'ScenarioVehicle_1', 
 'tags': ['vehicle', 'dynamic', 'ego'], 
 'velocity': [*f, *f, *f], 
 'wheel_speed': [*f, *f, *f], 
 'position': [*f, *f, *f], 
 'angular_velocity': [*f, *f, *f], 
 'wheels': [{'id': 1, 'orientation': [*f, *f, *f, *f]}
'''

class ScenarioItem(object):
    def __init__(self, item):
        self.name = item['name']
        self.tags = item['tags']
        self.velocity = item['velocity']
        self.wheel_speed = item['wheel_speed']
        self.position = item['position']
        self.angular_velocity = item['angular_velocity']
        self.wheels = []
        for wheel in item['wheels']:
            self.wheels.append(Wheel)


class Wheel(object):
    def __init__(self, wheel):
        self.id = wheel['id']
        self.orientation = wheel['orientation']


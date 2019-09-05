

class Reporting(object):
    def __init__(self, sensor_ids):
        self.sensor_ids = sensor_ids

    def on_update(self, data):
        print("Reporting Data *********** {0}".format(data[0].frame))

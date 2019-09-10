
import json
import io
import time
import json
import base64
from urllib import request


class Reporting(object):
    def __init__(self, sensor_ids):
        self.sensor_ids = sensor_ids
        self.all_stats = []

    def on_update(self,  data ):
        self.all_stats.append(json.loads(json.dumps(data[0].frame)))
        # print("Reporting Data *********** {0}".format(data[0].frame))

    def generate_report_summary(self):
        collisions = []
        sample_counts = []
        distances = []
        relative_velocities = []
        target_names = []
        for frame in self.all_stats:
            sample_count = frame["sample_count"]
            for target in frame["targets"]:
                if target["collision"]:
                    collisions.append(target["collision"])
                    distances.append(target["distance"])
                    sample_counts.append(sample_count)
                    relative_velocities.append(target["relative_velocity"])
                    target_names.append(target["name"])

        summary = {"Status": "Failed" if all(collisions) else "Passed",
                   "Collision Frames": sample_counts,
                   "Target names: ": target_names,
                   "Distance to targets: ": distances,
                   "Relative velocity to targets: ": relative_velocities}

        ##Uncomment to dump stats into a file
        # with open("all_stats.txt","w+") as file_out:
        #     for element in self.all_stats:
        #         json.dump(element, file_out)
        return summary

from uut.sensors.collision import Collision
import json
class Reporting(object):
    def __init__(self, sensor_ids):
        self.sensor_ids = sensor_ids
        self.all_stats = []

    def on_update(self,  data ):
        self.all_stats.append(json.loads(json.dumps(data[0].frame)))
        # print("Reporting Data *********** {0}".format(data[0].frame))

    def generate_report_summary(self):
        print("CREATE SUMMARY")
        collisions = []
        sample_counts = []
        distances = []
        relative_velocities = []
        for frame in self.all_stats:
            for target in frame["targets"]:
                if target["collision"]:
                    collisions.append(target["collision"])
                    sample_counts.append(target["sample_count"])
                    distances.append(target["distance"])
                    relative_velocities.append(target["relative_velocity"])

        summary = {"collisions": collisions,
                   "Frame number of collision": sample_counts,
                   "Distance to targets: ": distances,
                   "Relative velocity to targets: ": relative_velocities}
        print(summary)
        return summary

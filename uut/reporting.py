
import json
import pymongo


class Reporting(object):
    def __init__(self, sensor_ids):
        self.sensor_ids = sensor_ids
        self.all_stats = []

    def on_update(self,  data ):
        self.all_stats.append(json.loads(json.dumps(data[0].frame)))
        # print("Reporting Data *********** {0}".format(data[0].frame))

    def send_to_mongodb(self, summary):
        # init client connection
        host = '192.168.1.118'
        port = 27017
        client = pymongo.MongoClient(host, port)
        db = client['monodrive']
        collection = db['report_summary']
        doc = {
            'id': 'Report Summary',
            'data': summary,
        }
        res = collection.insert_one(doc)
        doc_id = res.inserted_id
        print('stored doc with id: {}'.format(doc_id))

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
                    print(target["distance"])
                    distances.append(target["distance"])
                    sample_counts.append(sample_count)
                    relative_velocities.append(target["relative_velocity"])
                    target_names.append(target["name"])

        summary = {"Status": "Failed" if all(collisions) else "Passed",
                   "Collision Frames": sample_counts,
                   "Target names: ": target_names,
                   "Distance to targets: ": distances,
                   "Relative velocity to targets: ": relative_velocities}

        self.send_to_mongodb(summary)
        return summary

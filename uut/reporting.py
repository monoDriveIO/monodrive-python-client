
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

        return summary


# class ElasticIngestion(Reporting):
#
#     """
#     Ingestion engine for simulator data into ELK
#
#     This class comes with a helper method to test without needing an instance of the simulator.
#
#     Example usage in python shell
#
#     ```
#     from reports.ingestion import ElasticIngestion
#     i = ElasticIngestion.test_using_report_text_file('data/sample_reports/report_nocollisionTurn.txt')
#     r = i.build_elk_request()
#     resp = i.send_elk_request(r)
#     ```
#
#     """
#     # THESE SHOULD BE IN A SETTINGS FILE SOMEWHERE
#     ELASTIC_URL = 'http://localhost:9200/_bulk'
#     ELASTIC_USER = 'elastic'
#     ELASTIC_PASS = 'E2SdjV0AZ8Enb2DgP95x'
#
#     def __init__(self, *args, **kwargs):
#         self.scenario = kwargs.pop('scenario', 'TEST')
#         self.customer = kwargs.pop('customer', 'default')
#         super().__init__()
#
#     def send_elk_request(self, elk_request):
#         """
#         Send the bytesIO object to ELK using built in python request
#         """
#         credentials = ('{0}:{1}'.format(ElasticIngestion.ELASTIC_USER, ElasticIngestion.ELASTIC_PASS))
#         encoded_credentials = base64.b64encode(credentials.encode('ascii'))
#         req_data = elk_request.read()
#         req = request.Request(ElasticIngestion.ELASTIC_URL,
#                               data=req_data, headers={
#                 'Content-Type': 'application/x-ndjson',
#                 'Authorization': 'Basic {0}'.format(encoded_credentials.decode('ascii'))})
#         resp = request.urlopen(req)
#         return resp
#
#     def build_elk_request(self):
#         """
#         retrieve the stats from the instance and build a bytesIO file to send to ELK
#         """
#         run_id = self.all_stats[0]['time']
#         gtime = time.time()
#         elk_request = io.BytesIO()
#
#         for index in range(0, len(self.all_stats)):
#             item = self.all_stats[index]
#             item_time = gtime + float(item['game_time'])
#             elk_item = self.get_elk_line_item_object(item, index, item_time, run_id)
#
#             elk_item_header = json.dumps({
#                 "create": {
#                     "_index": "report",
#                     "_type": "_doc",
#                     "_id": '{0}_{1}'.format(elk_item['run'], elk_item['step'])
#                 }
#             })
#
#             elk_request.write((elk_item_header + "\n").encode())
#             elk_request.write((json.dumps(elk_item) + "\n").encode())
#
#         elk_request.write('\n'.encode())
#         elk_request.seek(0)  # get ready for read
#         return elk_request
#
#     def get_elk_line_item_object(self, line, index_id, timestamp, run_id):
#         return {
#             "run": run_id,
#             "step": index_id,
#             "game_timestamp": timestamp,
#             "@timestamp": timestamp * 1000,
#             "scenario": self.scenario,
#             "customer": self.customer,
#             "result": line
#         }
#
#     def generate_report_summary(self):
#         super().generate_report_summary(self)
#         # hook into ELK here
#         elk_request = self.build_elk_request()
#         self.send_elk_request(elk_request)
#
#     @staticmethod
#     def test_using_report_text_file(filepath):
#         stats = open(filepath, 'rb')
#         stats_list = []
#         for line in stats.readlines():
#             stats_list.append(json.loads(line))
#         inst = ElasticIngestion()
#         inst.all_stats = stats_list
#         return inst

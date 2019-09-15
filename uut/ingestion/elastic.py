import io
import time
import json
import base64
from urllib import request

from uut.ingestion.exceptions import *
from uut.ingestion.settings import ELASTIC_URL, ELASTIC_USER, ELASTIC_PASS


class ElasticIngestion(object):
    """
    Ingestion engine for simulator data into ELK

    This class comes with a helper method to test without needing an instance of the simulator.

    Example usage in python shell
    
    ```
    from reports.ingestion import ElasticIngestion
    i = ElasticIngestion.test_using_report_text_file('data/sample_reports/report_nocollisionTurn.txt')
    r = i.build_elk_request()
    resp = i.send_elk_request(r)
    ```
    """

    def __init__(self, *args, **kwargs):
        self.scenario = kwargs.pop('scenario', 'TEST')
        self.customer = kwargs.pop('customer', 'default')
        self.fps = kwargs.pop('fps', 30)
        self.data = kwargs.pop('data', [])
        self._validated = False

    def send_elk_request(self, elk_request):
        """
        Send the bytesIO object to ELK using built in python request
        """
        credentials = ('{0}:{1}'.format(ELASTIC_USER, ELASTIC_PASS))
        encoded_credentials = base64.b64encode(credentials.encode('ascii'))
        req_data = elk_request.read()
        req = request.Request(ELASTIC_URL,
            data=req_data, headers={
                    'Content-Type': 'application/x-ndjson',
                    'Authorization': 'Basic {0}'.format(encoded_credentials.decode('ascii'))})
        resp = request.urlopen(req)
        #print("REQ: ", req)
        if resp.status != 200:
            print("RESPONSE: ", resp.read())
        return resp

    def build_elk_request(self, base_time, batch, start_id):
        """
        retrieve the stats from the instance and build a bytesIO file to send to ELK
        """
        elk_request = io.BytesIO()
    
        for index in range(0, len(batch)):
            item = batch[index]
            elk_item = self.get_elk_line_item_object(item, index, base_time, start_id)

            elk_item_header = json.dumps({
                "create": {
                    "_index": "report",
                    "_type": "_doc",
                    "_id": '{0}_{1}'.format(elk_item['run'], elk_item['step'])
                }
            })

            elk_request.write((elk_item_header + "\n").encode())
            elk_request.write((json.dumps(elk_item) + "\n").encode())

        elk_request.write('\n'.encode())
        elk_request.seek(0)  # get ready for read
        return elk_request
        
    def chunks(self, l, n):
        for i in range(0, len(l), n):
            yield l[i:i + n]

    def batch_elk_data(self, batch_size):
        return list(self.chunks(self.data, batch_size))

    def validate_data(self):
        if not isinstance(self.data, (list, tuple)) or not isinstance(self.data[0], (dict,)):
            raise ElasticIngestionDataValidationInvalidDataStructureElement

        if 'time' not in self.data[0]:
            raise ElasticIngestionDataValidationNoTimeElement

        if 'game_time' not in self.data[0]:
            raise ElasticIngestionDataValidationNoGameTimeElement
        self._validated = True

    def batch_and_send_elk_request(self, batch_size=100):
        gtime = time.time()
        batches = self.batch_elk_data(batch_size)
        responses = []
        for index in range(0, len(batches)):
            batch = batches[index]
            elk_req = self.build_elk_request(gtime, batch, (index * batch_size))
            elk_resp = self.send_elk_request(elk_req)
            responses.append(elk_resp)
        return responses

    def get_elk_line_item_object(self, line, index_id, base_time, start_id):
        step = (start_id + index_id)
        fps_timestamp = base_time + ((self.fps / 60) * step)
        timestamp = round(base_time + float(line['game_time']), 4)
        return {
            "run": self.run_id,
            "step": step,
            "game_timestamp": line['game_time'],
            "fps_timestamp": fps_timestamp * 1000,
            "@timestamp": timestamp * 1000,
            "scenario": self.scenario,
            "customer": self.customer,
            "result": line
        }

    def generate_full_report(self):
        self.validate_data()
        responses = self.batch_and_send_elk_request()
        return responses

    @property
    def run_id(self):
        if not self._validated:
            raise RuntimeError('To get a run_id you must run `.validate_data`')
        return self.data[0]['time']
    
    @staticmethod
    def test_using_report_text_file(filepath):
        stats = open(filepath, 'rb')
        stats_list = []
        for line in stats.readlines():
            stats_list.append(json.loads(line))
        inst = ElasticIngestion()
        inst.all_stats = stats_list
        return inst
        
    @staticmethod
    def test_using_report_list_file(filepath):
        stats_list = json.load(open(filepath, 'r'))
        inst = ElasticIngestion()
        inst.data = stats_list
        return inst
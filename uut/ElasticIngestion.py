import io
import time
import json
import base64
from urllib import request


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
    # THESE SHOULD BE IN A SETTINGS FILE SOMEWHERE
    ELASTIC_URL = 'http://192.168.1.120:9200/_bulk'
    ELASTIC_USER = 'ingestion'
    ELASTIC_PASS = 'm0n0drive!'

    def __init__(self, *args, **kwargs):
        self.scenario = kwargs.pop('scenario', 'TEST')
        self.customer = kwargs.pop('customer', 'default')
        self.data = kwargs.pop('data', [])


    def send_elk_request(self, elk_request):
        """
        Send the bytesIO object to ELK using built in python request
        """
        credentials = ('{0}:{1}'.format(ElasticIngestion.ELASTIC_USER, ElasticIngestion.ELASTIC_PASS))
        encoded_credentials = base64.b64encode(credentials.encode('ascii'))
        req_data = elk_request.read()
        req = request.Request(ElasticIngestion.ELASTIC_URL,
            data=req_data, headers={
                    'Content-Type': 'application/x-ndjson',
                    'Authorization': 'Basic {0}'.format(encoded_credentials.decode('ascii'))})
        resp = request.urlopen(req)
        print("REQ: ", req)
        print("RESPONSE: ", resp)
        return resp

    def build_elk_request(self, run_id, base_time, batch):
        """
        retrieve the stats from the instance and build a bytesIO file to send to ELK
        """
        elk_request = io.BytesIO()

        for index in range(0, len(batch)):
            item = batch[index]
            item_time = base_time + float(item['game_time'])
            elk_item = self.get_elk_line_item_object(item, index, item_time, run_id)

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

    def batch_and_send_elk_request(self, batch_size=100):
        run_id = self.data[0]['time']
        gtime = time.time()
        batches = [self.data[i * batch_size:(i + 1) * batch_size] \
                   for i in range((len(self.data) + batch_size - 1))]
        for batch in batches:
            elk_req = self.build_elk_request(run_id, gtime, batch)
            elk_resp = self.send_elk_request(elk_req)

    def get_elk_line_item_object(self, line, index_id, timestamp, run_id):
        return {
            "run": run_id,
            "step": index_id,
            "game_timestamp": timestamp,
            "@timestamp": timestamp * 1000,
            "scenario": "test",
            "customer": "default",
            "result": line
        }

    def generate_full_report(self):
        # hook into ELK here
        # elk_request = self.build_elk_request()
        # self.send_elk_request(elk_request)
        self.batch_and_send_elk_request()

    @staticmethod
    def test_using_report_text_file(filepath):
        stats = open(filepath, 'rb')
        stats_list = []
        for line in stats.readlines():
            stats_list.append(json.loads(line))
        inst = ElasticIngestion()
        inst.all_stats = stats_list
        return inst
import time
import json
import unittest
import urllib
import socket

from tests.test_ingestion import BaseElasticIngestionUnitTest


class TestElasticIngestionAPIs(BaseElasticIngestionUnitTest):

    def _is_elk_up(self):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        result = sock.connect_ex(('127.0.0.1',9200))
        sock.close()
        return True if result == 0 else False

    def test_elk_api_bulk_post(self):
        if not self._is_elk_up():
            print('Cannot perform test... ELK API is not alive')
            return
        inst = self.get_elastic_instance('sample_AEB_10_0_CCRS_Collision.json')

        # to make sure this data goes in we need to randomize the "run" from the sample data's hardcoded value
        inst.data[0]['time'] = 'unittest_{0}'.format(int(time.time()))

        responses = inst.generate_full_report()

        self.assertEqual([resp.status for resp in responses], [200]*len(responses))

    def test_elk_api_duplicate_post(self):
        pass

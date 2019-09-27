import os
import sys

root_client = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.realpath(__file__)))))
sys.path.insert(0, root_client)

import time
import json
import base64
import subprocess
from urllib import request

from uut.ingestion.settings import KIBANA_BACKUP_LOCATION, KIBANA_DEFAULT_INDEX_NAME, KIBANA_REPORT_INDEX_BACKUP_LOCATION
from uut.ingestion.network import KibanaNetwork, ElasticNetwork
from uut.ingestion.exceptions import ElasticNetworkAPIError
from tests.test_elastic_funcs import TestElasticIngestionAPIs


class Importer(object):
    def __init__(self):
        # ROUTINE:
        # - get to see if index with name "report" exists
        # - if not; tell user to create index from fixtures/indexes/report.txt
        # - - (maybe we can automatically do that for them)
        # - get the backup of the saved objects
        # - loop over objects and replace index id with new index id
        # - send updated items
        self.backup_index = json.load(open(KIBANA_REPORT_INDEX_BACKUP_LOCATION, 'rb'))
        self.backup_objects = open(KIBANA_BACKUP_LOCATION, 'rb')

        current_index = self.get_index()
        # TODO: add None logic
        if current_index is None:
            user_wants_index_created = self.request_user_input_expect_yes_no('We could not find an index in ElasticCache with the name `{0}`. Would you like to create one? y/N? ')
            if not user_wants_index_created:
                raise RuntimeError('ElasticCache index `{0}` required to import Kibana - Saved Objects'.format(KIBANA_DEFAULT_INDEX_NAME))
            current_index = self.create_index()
            # we need to import some data before importing the saved objects
            subprocess.Popen('python -m unittest discover -p "*elastic*"')
            time.sleep(5)

        # self.replace_backup_objects_with_new_index(current_index['id'])
        # # we now send all of the objects except the index-pattern that the customer configured themselves
        resp = self.bulk_create_objects(self.backup_objects)
        #print(resp.body)


    def request_user_input_expect_yes_no(self, message):
        user_response = input(message)
        if user_response.lower() == 'y':
            return True
        elif user_response.lower() == 'n':
            return False
        else:
            return self.request_user_input_expect_yes_no(message)

    def bulk_create_objects(self, saved_objects):
        saved_objects_request = KibanaNetwork.formpost('/api/saved_objects/_import',
            saved_objects, headers={
                'kbn-xsrf': 'true'
            })
        return saved_objects_request

    def get_index(self):
        try:
            get_index_request = ElasticNetwork.get_json('/{0}'.format(KIBANA_DEFAULT_INDEX_NAME))
        except ElasticNetworkAPIError as e:
            if e.status == 404:  # we expect a 404 if there is no index
                return None
            raise ElasticNetworkAPIError(e.status, e.message)
        return get_index_request.json
    
    def create_index(self):
        # cleanup backup to remove settings node
        del self.backup_index['settings']
        create_index_request = ElasticNetwork.put_json('/{0}'.format(KIBANA_DEFAULT_INDEX_NAME),
            self.backup_index)
        return create_index_request.json


if __name__ == '__main__':
    importer = Importer()



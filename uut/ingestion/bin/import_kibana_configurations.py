import os
import sys

root_client = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.realpath(__file__)))))
sys.path.insert(0, root_client)

import json
import base64
from urllib import request

from uut.ingestion.settings import KIBANA_BACKUP_LOCATION, KIBANA_DEFAULT_INDEX_NAME
from uut.ingestion.network import KibanaNetwork


class Importer(object):
    def __init__(self):
        # ROUTINE:
        # - get to see if index with name "report" exists
        # - if not; tell user to create index from fixtures/indexes/report.txt
        # - - (maybe we can automatically do that for them)
        # - get the backup of the saved objects
        # - loop over objects and replace index id with new index id
        # - send updated items
        self.backup_objects = json.load(open(KIBANA_BACKUP_LOCATION, 'rb'))

        current_index = self.get_current_index()
        # TODO: add None logic

    def build_post_objects(backup_objects):
        ready_objects = []
        for o in backup_objects:
            if o['type'] == 'config':
                continue

            ready_objects.append({
                'type': o['type'],
                'id': o['id'],
                'attributes': o['attributes']
            })
        return ready_objects

    def bulk_create_objects(self):
        saved_objects_request = KibanaNetwork.post_json('/api/saved_objects/_bulk_create',
            saved_objects.encode(), headers={
                'kbn-xsrf': 'reporting'
            })
        return saved_objects_request

    def get_current_index(self):
        get_index_request = KibanaNetwork.get_json('/api/saved_objects/_find', {
            'type': ['index-pattern',]
        })
        index_request_json = get_index_request.json
        report_index = None
        if not len(index_request_json['saved_objects']):
            return report_index

        for index_obj in index_request_json['saved_objects']:
            if index_obj['attributes']['title'] == KIBANA_DEFAULT_INDEX_NAME:
                report_index = index_obj
                break
        return report_index


if __name__ == '__main__':
    importer = Importer()



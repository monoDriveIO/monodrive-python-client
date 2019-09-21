import os
import sys

root_client = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.realpath(__file__)))))
sys.path.insert(0, root_client)

import json
import base64
from urllib import request

from uut.ingestion.settings import KIBANA_BACKUP_LOCATION
from uut.ingestion.network import KibanaNetwork


if __name__ == '__main__':
    # Documentation: https://www.elastic.co/guide/en/kibana/current/saved-objects-api-find.html
    saved_objects_request = KibanaNetwork.get_json('/api/saved_objects/_find', {
        'type': ['visualization', 'dashboard', 'search', 'index-pattern', 'config']
    })
    saved_objects_request_json = saved_objects_request.json
    saved_objects = saved_objects_request_json['saved_objects']

    # Save to fixture in uut module
    f = open(KIBANA_BACKUP_LOCATION, 'w')
    f.write(json.dumps(saved_objects))
    f.close()

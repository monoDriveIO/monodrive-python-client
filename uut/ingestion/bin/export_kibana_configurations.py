import os
import sys

root_client = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.realpath(__file__)))))
sys.path.insert(0, root_client)

import json
import base64
import operator
from functools import reduce  
from urllib import request

from uut.ingestion.settings import KIBANA_BACKUP_LOCATION, KIBANA_REPORT_INDEX_BACKUP_LOCATION, KIBANA_DEFAULT_INDEX_NAME
from uut.ingestion.network import KibanaNetwork, ElasticNetwork


if __name__ == '__main__':
    # Download the index and back up the response
    # Documentation: https://www.elastic.co/guide/en/elasticsearch/reference/current/indices-get-index.html
    get_index_request = ElasticNetwork.get_json('/{0}'.format(KIBANA_DEFAULT_INDEX_NAME))
    index_request_json = get_index_request.json

    # save a fixture to uut module
    f = open(KIBANA_REPORT_INDEX_BACKUP_LOCATION, 'w')
    f.write(json.dumps(index_request_json[KIBANA_DEFAULT_INDEX_NAME]))
    f.close()

    # Download the kibana objects
    # Documentation: https://www.elastic.co/guide/en/kibana/current/saved-objects-api-find.html
    saved_objects_request = KibanaNetwork.post_json('/api/saved_objects/_export',
        {
            'type': ['visualization', 'dashboard', 'search', 'index-pattern']
        }, headers={
            'kbn-xsrf': 'reporting'
        })

    saved_objects_request_json = saved_objects_request.body.read()
    print(saved_objects_request_json)
    # Save to fixture in uut module
    f = open(KIBANA_BACKUP_LOCATION, 'wb')
    f.write(saved_objects_request_json)
    f.close()

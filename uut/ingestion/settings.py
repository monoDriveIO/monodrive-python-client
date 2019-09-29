import os
from uut import BASE_PATH, BASE_FIXTURE_PATH


ELASTIC_IP = 'localhost'
ELASTIC_PORT = 9200
ELASTIC_URL  = 'http://{0}:{1}'.format(ELASTIC_IP, ELASTIC_PORT)
ELASTIC_USER = 'elastic'
ELASTIC_PASS = 'LR9AuxxDxlDW9ZXHu2Or'

KIBANA_IP = 'localhost'
KIBANA_PORT = 5601
KIBANA_URL = 'http://{0}:{1}'.format(KIBANA_IP, KIBANA_PORT)
KIBANA_USER = 'elastic'
KIBANA_PASS = 'LR9AuxxDxlDW9ZXHu2Or'

KIBANA_BACKUP_LOCATION = os.path.join(BASE_FIXTURE_PATH, 'elk', 'saved_objects_backup.json')
KIBANA_DEFAULT_INDEX_NAME = 'report'
KIBANA_REPORT_INDEX_BACKUP_LOCATION = os.path.join(BASE_FIXTURE_PATH, 'indexes', '{0}.json'.format(KIBANA_DEFAULT_INDEX_NAME))

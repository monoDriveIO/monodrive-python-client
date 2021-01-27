from datetime import datetime
from elasticsearch import Elasticsearch

elasticURL = "http://localhost:9200"
# another syntax: {'host': 'localhost', 'port': 9200}

es = Elasticsearch([elasticURL])

jobs_index = "jobs"

practice_doc = {
    "job_id": "test",
    "batch_id": 1,
    "timestamp": datetime.now(),
    "status": "COMPLETED"
}

# add document example
res1 = es.index(index=jobs_index, body=practice_doc)

#  search example
res2 = es.search(index=jobs_index, body={"query": {"match_all": {}}})
print("Got %d Hits:" % res2['hits']['total']['value'])
for hit in res2['hits']['hits']:
    print(hit["_source"])

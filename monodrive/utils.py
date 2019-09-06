import pymongo


def send_summary_to_mongodb(summary):
    # init client connection
    host = '192.168.1.118'
    port = 27017
    client = pymongo.MongoClient(host, port)
    db = client['monodrive']
    collection = db['report_summary']
    doc = {
        'id': 'Report Summary',
        'data': summary,
    }
    res = collection.insert_one(doc)
    doc_id = res.inserted_id
from flask import Flask, request, jsonify
from pprint import pprint
import json
from uuid import uuid4

ncco = [
    {
        "action": "talk",
        "text": "You have reached your Nexmo number"
    }
]

def upsert_document(cb_coll, doc):
  print("\nUpsert CAS: ")
  try:
    # key will equal: "event_uuid"
    key = "event_" + str(uuid4())
    result = cb_coll.upsert(key, doc)
    print(result.cas)
  except Exception as e:
    print(e)

# needed for any cluster connection
from couchbase.cluster import Cluster, ClusterOptions
from couchbase_core.cluster import PasswordAuthenticator

# needed to support SQL++ (N1QL) query
from couchbase.cluster import QueryOptions

# get a reference to our cluster
cluster = Cluster('couchbase://localhost', ClusterOptions(
  PasswordAuthenticator('Administrator', '090662')))

# get a reference to our bucket
cb = cluster.bucket('events')

# get a reference to the default collection
cb_coll = cb.default_collection()

app = Flask(__name__)

@app.route("/webhooks/answer")
def answer():
    params = request.args
    pprint(params)
    return jsonify(ncco)

@app.route("/webhooks/event", methods=['POST'])
def events():
    data = request.get_json() # Gets JSON string to Python object
    pprint(data) # Prints Python data structure
    event = data  # Don't even need to do json.dumps(data) to convert Python object to JSON string as the Couchbase SDK seems to do this
    upsert_document(cb_coll, event)    
    return (jsonify(data))

if __name__ == '__main__':
    print("Running locally")
    app.run(host="localhost", port=9000)

from flask import Flask, request, jsonify
from pprint import pprint
import json
from uuid import uuid4
import os
from dotenv import load_dotenv

load_dotenv()
db_password = os.getenv("DB_PASSWORD")
nexmo_number = os.getenv("NEXMO_NUMBER")
to_number = os.getenv("TO_NUMBER")

ncco = [
    {
        "action": "talk",
        "text": "Now connecting you to phone endpoint"
    },
    {
        "action": "connect",
        "from": nexmo_number,
        "endpoint": [
            {
                "type": "phone",
                "number": to_number
            }
        ]
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
  PasswordAuthenticator('Administrator', db_password)), lockmode=2) # added lockmode to avoid locking error

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
    upsert_document(cb_coll, event) # Locking issue   
    return "OK"

if __name__ == '__main__':
    print("Running locally")
    app.run(host="localhost", port=9000)

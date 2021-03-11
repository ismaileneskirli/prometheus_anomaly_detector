from flask import Response, Flask, request,render_template, jsonify
import prometheus_client
from prometheus_client.core import CollectorRegistry
from prometheus_client import Summary, Counter, Histogram, Gauge
import time
import random
import os
import googleapiclient.discovery
import logging
from sqlalchemy import create_engine

DB_NAME = 'anomaly'
DB_USER = 'admin'
DB_PASSWORD = 'admin'
DB_HOST ='db'
DB_PORT = '5432'

# connect to the database here.

db_string = 'postgres://{}:{}@{}:{}/{}'.format(DB_USER,DB_PASSWORD,DB_HOST,DB_PORT,DB_NAME)
db = create_engine(db_string)

def add_new_row(n):
    # Insert a new number into the 'numbers' table.
    db.execute("INSERT INTO numbers (number,timestamp) "+\
        "VALUES ("+ \
        str(n) + "," + \
        str(int(round(time.time() * 1000))) + ");")

def get_all():
    # Get all of the data from the db
    rows = []
    query = "SELECT * FROM numbers ORDER BY timestamp DESC offset 0 rows fetch next 20 rows only"
    result = db.execute(query)
    print(f"Selected {result.rowcount} rows.")
    for row in result.fetchall():
        rows.append(row[0])
    return(jsonify(rows))

app = Flask(__name__)

_INF = float("inf")

anomaly_series = [1,1,-1,1,1,1,1,1,1,-1]
graphs = {}
graphs['c'] = Counter('python_request_operations_total', 'The total number of processed requests')
graphs['h'] = Histogram('python_request_duration_seconds', 'Histogram for the duration in seconds.', buckets=(1, 2, 5, 6, 10, _INF))
graphs['f'] = Gauge ('anomaly_detector_output','Anomaly model outputs, -1 means outlier value')

 ########################################### Anomaly API #############################################################
def predict_json(project, model, instances, data, version=None):
    service = googleapiclient.discovery.build('ml', 'v1')
    name = 'projects/{}/models/{}'.format(project, model)

    if version is not None:
        name += '/versions/{}'.format(version)

    print("name: {}".format(name))
    response = service.projects().predict(
        name=name,
        body={'instances': instances, 'data':data}
    ).execute()

    if 'error' in response:
        raise RuntimeError(response['error'])

    return response['predictions']

# Create Dummy Data.
def generateArray(n):
    array = []
    for i in range (n):
        array.append([str(i),5])
    array.append([str(n+1),20])
    print(array)
    return array


@app.route("/")
def hello():
    start = time.time()
    graphs['c'].inc()
    time.sleep(0.600)
    end = time.time()
    graphs['h'].observe(end - start)
    return "Welcome to the Anomaly detector model."

@app.route("/metrics")
def requests_count():
    res = []
    for k,v in graphs.items():
        res.append(prometheus_client.generate_latest(v))
    return Response(res, mimetype="text/plain")
#For testing if db actually works.
@app.route("/show")
def show_db():
    for i in range (0,3):
        add_new_row(random.randint(1,10000));
    return(get_all())

# API usage and sent output to prometheus.
@app.route("/generate")
def generate_data():
    anomalyArray = generateArray(20)
    os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = 'key.json'
    try:
        ret = predict_json('datalake-name-here', model='anomaly_detector', instances=[], data=anomalyArray)
    except Exception as e:
        print(e)
    for i in range (len(ret)):
        time.sleep(0.600)
        graphs['f'].set(ret[i][1])
    return "Metrics are sent !"

if __name__ == '__main__':
    app.run(debug=True)

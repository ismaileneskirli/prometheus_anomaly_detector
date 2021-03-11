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

def get_last_twenty():
    # Get the last 20 from from the db, create an array from the first column.
    rows = []
    query = "SELECT * FROM numbers ORDER BY timestamp DESC offset 0 rows fetch next 20 rows only"
    result = db.execute(query)
    print(f"Selected {result.rowcount} rows.")
    for row in result.fetchall():
        rows.append(row[0])
    return(rows)

app = Flask(__name__)

_INF = float("inf")

anomaly_series = [1,1,-1,1,1,1,1,1,1,-1]
graphs = {}
graphs['c'] = Counter('python_request_operations_total', 'The total number of processed requests')
graphs['h'] = Histogram('python_request_duration_seconds', 'Histogram for the duration in seconds.', buckets=(1, 2, 5, 6, 10, _INF))
graphs['f'] = Gauge ('anomaly_detector_output','Anomaly model outputs, -1 means outlier value')

 ##### Anomaly API (second output is the value if -1 it means anomaly) #############################################################
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

# # Create Dummy Data. with 1 anomalie.
# def generateArray(n):
#     array = []
#     for i in range (n):
#         array.append([str(i),5])
#     array.append([str(n+1),20])
#     print(array)
#     return array

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

#For generating a data-stream
@app.route("/data-stream")
def data_stream():
    while True:
        add_new_row(random.randint(1,1000));

# send last 20 row to data and output to the prometheus.
@app.route("/generate")
def generate_data():
    # this func can also be in while true loop, with 20 sec of sleep in each loop last 20 rows are completely different., now it is just for one time.
    os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = 'datalake.json'
    try:
        ret = predict_json('coca-cola-datalake-dev', model='anomaly_detector', instances=[], data=get_last_twenty())
    except Exception as e:
        print(e)
    for i in range (len(ret)):
        time.sleep(0.600)
        graphs['f'].set(ret[i][1])
    return "Metrics are sent !"

if __name__ == '__main__':
    app.run(debug=True)

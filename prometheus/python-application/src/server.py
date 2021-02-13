from flask import Response, Flask, request,render_template
import prometheus_client
from prometheus_client.core import CollectorRegistry
from prometheus_client import Summary, Counter, Histogram, Gauge
import time
import random

app = Flask(__name__)

_INF = float("inf")

anomaly_series = [1,1,-1,1,1,1,1,1,1,-1]
graphs = {} 
graphs['c'] = Counter('python_request_operations_total', 'The total number of processed requests')
graphs['h'] = Histogram('python_request_duration_seconds', 'Histogram for the duration in seconds.', buckets=(1, 2, 5, 6, 10, _INF))
graphs['f'] = Gauge ('anomaly_detector_output','Anomaly model outputs, -1 means outlier value')
global num

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

@app.route("/generate")
def generate_data():
    num = anomaly_series[random.randint(0,9)]
    time.sleep(1.000)
    graphs['f'].set(num)
    return "data generated"

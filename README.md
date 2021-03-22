# Prometheus Application Monitoring
![architecture](https://user-images.githubusercontent.com/69651222/110786058-bdfd9400-827c-11eb-9341-979fc3d73dd3.jpg)
## Prerequisites
In order to run commands below, you need docker engine, docker-compose installed on your machine.

```
sudo snap install docker
sudo snap install docker-compose

```


To run any of the commands, please ensure you open a terminal and navigate to the path where prometheus folder is located. If you are not root user simply add sudo.

## Start Prometheus, Grafana & Dashboards

```
docker-compose up -d prometheus
docker-compose up -d grafana
docker-compose up -d grafana-dashboards

or simply arrange dependencies and then:

docker-compose up -d --build
```

## Start the example app


```
docker-compose up -d --build python-application


## Generate some requests by opening the application in the browser, Anomaly detection api takes the last 20 rows as a parameter, so db should be launched before making requests.

http://localhost:81 #Python


http://localhost:81/generate # for generating real time data to be used in anomalie detection dashboard.

```
## Check Dashboards
```
http://localhost:3000

```
## Prometheus Queries

Requests per Second over 2minutes
```
irate(go_request_operations_total[2m])
```
Request duration
```
rate(go_request_duration_seconds_sum[2m]) / rate(go_request_duration_seconds_total[2m])
```

Anomaly Detection

```
anomaly_detection_output
```


## TODO API and Postgresql Implementation.

- [x] Generate real-time data stream, with anomalies.(while loop with time.sleep(1))
- [x] Push these data into db
- [x] Pull last 20 row from db into (sorted by time stamp),
- [x] row[0] is number i want to send to API, turn the first element of query into an array.
- [x] send this array into anomaly detection api in gcp
- [x] return value of the api is an array of arrays and second element of each array is anomaly_detector_output,assign it.
- [x] when there is a value below 0 alert it. ( this needs to be configured once composed up.)

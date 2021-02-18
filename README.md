# Prometheus Application Monitoring

##Prerequisites
In order to run commands below you need docker engine, docker-compose installed on your machine.

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
```

## Start the example app 


```
docker-compose up -d --build python-application


## Generate some requests by opening the application in the browser

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



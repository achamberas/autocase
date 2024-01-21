# Autocase Simulation POC

Autocase has an industry leading simulation model to forecast energy consumption given a building configuration. That simulation model takes a long time to run, so one way to speed up the process is to simulate a lot of different configurations, predict their consumption, and then train an ML model on top of that data that will predict consumption in milliseconds.

This POC proposes a framework for simulation that will allow Autocase to simulate different building configurations and predict their energy consumption.

## Framework

High level framework diagram:

<img src="workflow.png" alt="workflow" width="500"/>

Framework has two componenets: local environment and google cloud. [Google Cloud Tasks](https://cloud.google.com/tasks/) are  used for task scheduling/menagment and [Google Big Query](https://cloud.google.com/bigquery) is used for storing simulation results. Local environment is used trigger google cloud tasks.

Here are the steps happen in order to run simulation:

* `/create_task` API endpoint gets called (this can be done through a script or an application) 
* A task is created & scheduled Google Cloud Tasks
* Once that task runs it hits `/run_simulation` endpoint that either randomly fails (this is done to illustrate retry ability of google cloud tasks) or it succeeds and triggers a logging task in Google Cloud Tasks. Also in case of a success, results gets logged to Google Big Query
  * In case of failure google cloud tasks will retry the request
* Once the the logging task is executed it hits `/log_success` endpoint that logs success in a `success.txt` file

NOTE: Local environment has to be exposed to the internet so google cloud tasks can talk to it. This can be done via ngrok (see below for setup). This local environment can be swapped with a production environment.

## Installation & Set Up

* Install [Docker](https://www.docker.com/)
* Sign up for [ngrok](https://dashboard.ngrok.com/signup) & install it locally. Make note of the forwarding address (i.e. `https://xxxx-xxx-xx-xx-xxx.ngrok-free.app`) as this will need to be used when running the Docker container.
* Once installed, open up terminal and run `ngrok http 8080`. Output similar to the one below should appear:
```
ngrok                                                                                                                                                                
Introducing Pay-as-you-go pricing: https://ngrok.com/r/payg                                                                                                                                                                                                                                                        
                                                                                                                                                                                                                                                                                                                   
Session Status                online                                                                                                                                                                                                                                                                               
Account                       Anthony Chamberas (Plan: Free)                                                                                                                                                                                                                                                       
Version                       3.5.0                                                                                                                                                                                                                                                                                
Region                        United States (us)                                                                                                                                                                                                                                                                   
Latency                       46ms                                                                                                                                                                                                                                                                                 
Web Interface                 http://127.0.0.1:4040                                                                                                                                                                                                                                                                
Forwarding                    https://948d-108-20-21-168.ngrok-free.app -> http://localhost:8080                                                                                                                                                                                                                   
                                                                                                                                                                                                                                                                                                                   
Connections                   ttl     opn     rt1     rt5     p50     p90                                                                                                                                                                                                                                          
                              131     0       0.00    0.00    3.01    6.67       
```

* Open up a new terminal window and build the docker image by running `docker build . -t autocase_poc`
* Once that's build run the docker image with this command `docker run --name autocase_poc -p 8080:8080 --env PORT=8080 --env BACKEND_URL=<ngrok forwarding address> autocase_poc` (put the forwarding address that was noted earlier)
* Test out that service is working by visiting `http://localhost:8080`. The page loaded should say `Hello World! The app is running.`


NOTE: This assumes that the process is running on a local machine. Once this gets to production ngrok would not be needed. Docker image can be used to install the process on any machine.

## Execution

* Envoke `http://localhost:8080/create_task` (either via curl or Postman) with `POST` and this payload 

```
{
    "wait": 0,
    "fail_rate": 0.3
}
```

* If the tasks are generated successfully, the response will be:

`tasks created to run simulation with 6 iterations`

## Review Results

* Open [Google Task Queue](https://console.cloud.google.com/cloudtasks/queue/us-central1/default/tasks?authuser=3&project=autocase-201317) to review tasks created for each simulation. A task for each iteration will be shown.  As the iteration completes successfully, the task will disappear from the list.  If a task fails, the number of retrys will be noted.

* In the terminal window running ngrok to see the successful (`200 OK`) and failed (`500 INTERNAL SERVER ERROR`) simulation iterations, as well as successfully logged results. 

* In the terminal window running the Docker container to see execution messages and failures.

* In [Google Big Query](https://console.cloud.google.com/bigquery?authuser=3&project=autocase-201317&ws=!1m5!1m4!4m3!1sautocase-201317!2ssimulation_poc!3ssimulation) open and review `simulation_poc.simulation` 

### Configure Cloud Tasks

To modify the configuration for the default Cloud Task queue, run this command with the Google Cloud CLI installed

```
gcloud tasks queues update default \
       --max-attempts=100 \
       --min-backoff=3s \
       --max-backoff=10s \
       --max-doublings=16 \
       --max-retry-duration=60s
```
or modify the queue in the Google Cloud UI.

### Envoke Service With Python

The following code can be run in a Jupyter notebook or Python CLI, in place of `curl` or Postman, to test the service.

```
import requests
import json

url = "http://localhost:8080/create_task"

payload = json.dumps({
  "wait": 1,
  "fail_rate": 0.75
})
headers = {
  'Content-Type': 'application/json'
}

response = requests.request("POST", url, headers=headers, data=payload)

print(response.text)
```
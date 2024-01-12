import random
import json
import time
import os

from flask import Flask, render_template, request
from utils import *
from datetime import datetime

#project = 'gristmill5'
#location = 'us-east1'
#GOOGLE_APPLICATION_CREDENTIALS = "gristmill5-55f2eabbb537.json"

# Set variables to define environment
project = 'autocase-201317'
location = 'us-central1'
key_file = 'dev-cloud-tasks.json'
queue = 'default'
backend_url = 'https://948d-108-20-21-168.ngrok-free.app'
table = 'simulation_poc.simulation'

app = Flask(__name__)

# Basic index to verify app is serving.
@app.route("/")
def hello():
    return "Hello World!  The app is running."

# Endpoint to sent tasks to task queue
@app.route("/create_task", methods=["POST"])
def ct():

    # Synthesize iteration count based on number of sample files
    root = 'sample data/scraped data'
    iterations = len([files[2] for files in os.fwalk(root)][0])

    # Create a separate task for each iteration
    for i in range(0, iterations):
        payload = request.get_data(as_text=True)
        json_payload = json.loads(payload)
        json_payload['iteration'] = i
        payload = json.dumps(json_payload)

        response = create_task('run_simulation', project, location, key_file, queue, backend_url, payload)

    return 'tasks created to run simulation with ' + str(iterations) + ' iterations'

# Endpoint to run simultion.  Called by task queue
@app.route("/run_simulation", methods=["POST"])
def run_simulation():
    # Get and parse payload sent by Task Queue
    payload = request.get_data(as_text=True) or '{"wait":0,"fail_rate":0}'
    json_payload = json.loads(payload)
    wait = json_payload['wait'] if 'wait' in json_payload else 0
    fail_rate = json_payload['fail_rate'] if 'fail_rate' in json_payload else 0
    iteration = json_payload['iteration'] if 'iteration' in json_payload else -1

    # Mock a simulation using results from sample scrape files
    root = 'sample data/scraped data'
    fs = [files[2] for files in os.fwalk(root)][0]
    f = fs[iteration]
    file = root + '/' + f

    print('Received task with payload: ' + payload + '. Simulating ' + f + ' in iteration ' + str(iteration))

    # Mock a simulation failure
    rnd = random.randrange(1,100)
    print('random', rnd)

    # Mock delay in simulation imitate simulation run time
    time.sleep(wait)
    json_payload['random'] = rnd/100

    # Check if there is a simulation failure or payload error
    if rnd <= (1 - fail_rate) * 100 and iteration > -1:
        # save simulation results (scrape file) to BigQuery
        bq_load(file, table, project, key_file)

        # Create new task to log success
        response = create_task('log_success', project, location, key_file, queue, backend_url)
        return json_payload
    else:
        # Raise error.  Log to firebase?
        raise TypeError("There was an error")
        return 'error ' + str(rnd), 500

# Endpoint to log success (failure?) to success file (eventually Firebase)
# Called from task queue via simulation
@app.route("/log_success", methods=["POST"])
def log_success():
    # Save results and timestamp to text file
    ts = datetime.now()
    file1 = open("success.txt", "a")  # append mode
    file1.write(str(ts) + ": success \n")
    file1.close()
    return "success logged"

if __name__ == "__main__":
    # This is used when running locally. Gunicorn is used to run the
    # application on Google App Engine. See entrypoint in app.yaml.
    app.run(host="127.0.0.1", port=8080, debug=True)

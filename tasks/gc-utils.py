import pandas as pd
import pandas_gbq as pdgbq
import datetime
import json
import google.auth

from google.cloud import tasks_v2
from google.protobuf import timestamp_pb2
from google.oauth2 import service_account
from google.cloud import bigquery

# load data to big query
def bq_load(file, table, project, key_file):
    # set credentials from json key file
    GOOGLE_APPLICATION_CREDENTIALS = 'creds/' + key_file

    # create data frame from scrape file
    # eventually data frame will be created from simulation result
    df = pd.read_csv(file)

    try:
        # set credentials and append data frame to specified table
        credentials = service_account.Credentials.from_service_account_file(GOOGLE_APPLICATION_CREDENTIALS)
        insert = pdgbq.to_gbq(df, table, project_id=project, if_exists='append', credentials=credentials)

        print(insert)

    except Exception as e:
        print(e)
        print('error inserting data to BigQuery')

# create task in queue
def create_task(service, project, location, key_file, queue, backend_url, payload = 'hello'):
    # Create a task for a given queue with an arbitrary payload.
    in_seconds = None
    GOOGLE_APPLICATION_CREDENTIALS = 'creds/' + key_file
    credentials = service_account.Credentials.from_service_account_file(GOOGLE_APPLICATION_CREDENTIALS)

    # Create a client.
    client = tasks_v2.CloudTasksClient(credentials=credentials)

    # Construct the fully qualified queue name.
    parent = client.queue_path(project, location, queue)

    # Construct the request body.
    task = {
        "http_request": {  # Specify the type of request.
            "http_method": tasks_v2.HttpMethod.POST,
            "url": backend_url + "/" + service,
        }
    }
    if payload is not None:
        if isinstance(payload, dict):
            # Convert dict to JSON string
            payload = json.dumps(payload)
            # specify http content-type to application/json
            task["http_request"]["headers"] = {
                "Content-type": "application/json"
            }
        # The API expects a payload of type bytes.
        converted_payload = payload.encode()

        # Add the payload to the request.
        task["http_request"]["body"] = converted_payload

    if in_seconds is not None:
        # Convert "seconds from now" into an rfc3339 datetime string.
        d = datetime.datetime.now(tz=datetime.timezone.utc) + datetime.timedelta(
            seconds=in_seconds
        )

        # Create Timestamp protobuf.
        timestamp = timestamp_pb2.Timestamp()
        timestamp.FromDatetime(d)

        # Add the timestamp to the tasks.
        task["schedule_time"] = timestamp

    # Use the client to build and send the task.
    response = client.create_task(parent=parent, task=task)

    print(f"Created task {response.name}")
    return response

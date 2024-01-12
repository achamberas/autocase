# Copyright 2021 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# Use the official Python image.
# https://hub.docker.com/_/python
FROM python:3.11

# Copy local code to the container image.
ENV APP_HOME /app
# ENV PROJECT_ID autocase-201317
# ENV QUEUE_ID default
# ENV LOCATION_ID us-central1
# ENV GOOGLE_APPLICATION_CREDENTIALS dev-cloud-tasks.json
WORKDIR $APP_HOME
COPY . .

EXPOSE 8080
ENV PORT 8080

# Install production dependencies.
RUN pip install Flask gunicorn
RUN pip install -r requirements.txt

# Run the web service on container startup. Here we use the gunicorn
# webserver, with one worker process and 8 threads.
# For environments with multiple CPU cores, increase the number of workers
# to be equal to the cores available.

# RUN python3 create_app_engine_queue_task.py --project=$PROJECT_ID --queue=$QUEUE_ID --location=$LOCATION_ID --payload=hello
CMD exec gunicorn --bind :$PORT --workers 1 --threads 8 main:app

#!/bin/bash
set -e

echo "Starting SSH ..."
service ssh start

#python
# make sure to use paths on Container, not local filesystem!
flask --app /code/classevy/web run --host 0.0.0.0 --port 8000
#uwsgi
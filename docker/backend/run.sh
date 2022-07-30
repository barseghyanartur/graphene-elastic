#!/bin/sh

cd /code/

# Pip install requirements
echo "Running Elasticsearch 7.x: Installing requirements"
pip-compile requirements/dev.in
pip install -r requirements/dev.txt

# Clean up
echo "Running Elasticsearch 7.x: Clean up"
./scripts/clean_up.sh

# Running tests
echo "Running Elasticsearch 7.x: Running app"
python examples/apps/django_app/run.py runserver 0.0.0.0:8000 --traceback -v 3

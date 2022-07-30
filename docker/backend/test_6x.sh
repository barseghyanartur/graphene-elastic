#!/bin/sh

cd /code/

# Pip install requirements
echo "Testing Elasticsearch 6.x: Installing requirements"
pip-compile requirements/testing_6x.in
pip install -r requirements/testing_6x.txt

# Clean up
echo "Testing Elasticsearch 6.x: Clean up"
./scripts/clean_up.sh

# Running tests
echo "Testing Elasticsearch 6.x: Running tests"
./runtests.py

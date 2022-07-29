#!/bin/sh

cd /code/

# Pip install requirements
echo "Testing Elasticsearch 7.x: Installing requirements"
pip-compile requirements/testing_7x.in
pip install -r requirements/testing_7x.txt

# Clean up
echo "Testing Elasticsearch 7.x: Clean up"
./scripts/clean_up.sh

# Running tests
echo "Testing Elasticsearch 7.x: Running tests"
./runtests.py

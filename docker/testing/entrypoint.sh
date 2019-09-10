#!/bin/sh

# Pip install requirements.txt
echo "Installing requirements"
pip install -r requirements.txt

# Clean up
echo "Clean up"
./scripts/clean_up.sh

# Running tests
echo "Running tests"
./runtests.py

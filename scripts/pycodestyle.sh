#!/usr/bin/env bash
reset
pycodestyle src/graphene_elastic/
pycodestyle examples/ --exclude examples/apps/django_app/local_overrides.py,examples/apps/flask_app/local_overrides.py

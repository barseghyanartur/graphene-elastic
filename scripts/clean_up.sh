#!/usr/bin/env bash
find . -name "*.pyc" -exec rm -rf {} \;
find . -name "__pycache__" -exec rm -rf {} \;
find . -name "*.orig" -exec rm -rf {} \;
rm -rf .cache/
rm -rf build/
rm -rf builddocs/
rm -rf dist/
rm -rf deb_dist/
rm src/graphene_elastic.egg-info -rf
rm builddocs.zip

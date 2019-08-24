#!/usr/bin/env bash
sudo kill $(sudo lsof -t -i:9200)

#!/usr/bin/env bash
cd examples/apps/fastapi_app/
uvicorn main:app --reload --workers 4 --host 0.0.0.0 --port 8000

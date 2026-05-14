#!/bin/bash

. ./run-fast.sh &

uvicorn router:app --host 127.0.0.1 --port 8000 &

./web-ui.sh &
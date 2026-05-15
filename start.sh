#!/bin/bash

set -e

trap 'echo "Shutting down..."; kill "$uvicorn_pid" "$webui_pid" 2>/dev/null || true' EXIT

uvicorn router:app --host 127.0.0.1 --port 8060 &
uvicorn_pid=$!

./web-ui.sh &
webui_pid=$!

wait "$uvicorn_pid" "$webui_pid"
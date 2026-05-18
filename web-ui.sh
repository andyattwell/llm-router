#!/bin/bash

# Check if docker container is running
docker compose up -d open-webui

echo "Web UI is running at http://localhost:8080"
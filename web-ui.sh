docker run -d \
  -p 3000:8080 \
  -e OPENAI_API_BASE_URL=http://host.docker.internal:8000/v1 \
  -v open-webui:/app/backend/data \
  --network host \
  --name open-webui \
  ghcr.io/open-webui/open-webui:main
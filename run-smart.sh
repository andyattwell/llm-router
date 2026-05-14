#!/bin/bash

./build/bin/llama-server \
  -m ~/models/llama-3-8b-instruct.Q5_K_M.gguf \
  --host 0.0.0.0 \
  --port 8082 \
  -ngl 999 \
  -c 4096 \
  -b 512 \
  -ub 512 \
  -t 8
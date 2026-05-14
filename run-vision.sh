#!/bin/bash

./build/bin/llama-server \
  -m ~/models/qwen2-vl-7b-instruct.Q4_K_M.gguf \
  --mmproj ~/models/mmproj-qwen2-vl-7b-instruct-f16.gguf \
  --host 0.0.0.0 \
  --port 8083 \
  -ngl 20 \
  -c 2048 \
  -b 128 \
  -ub 128 \
  -t 8
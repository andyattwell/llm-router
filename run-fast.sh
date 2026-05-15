#!/bin/bash

SCRIPT_DIR=$(dirname "$0")
LLAMA=$(realpath $SCRIPT_DIR/../llama.cpp/build-cuda/bin/)
MODEL=$(realpath $SCRIPT_DIR/models/gemma-2-2b-it-Q6_K_L.gguf)

cd "$LLAMA" && exec llama-server \
  -m ${MODEL} \
  --host 0.0.0.0 \
  --port 8081 \
  -ngl 999 \
  -c 2048 \
  -b 512 \
  -ub 512 \
  -t 8
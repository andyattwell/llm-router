#!/bin/bash

SCRIPT_DIR=$(dirname "$0")
LLAMA=$(realpath $SCRIPT_DIR/../llama.cpp/build-cuda/bin/)
MODELS_DIR=$(realpath $SCRIPT_DIR/../llama-models)

cd "$LLAMA" && exec llama-server \
  -m ${MODELS_DIR}/gemma-2-2b-it-Q6_K_L.gguf \
  --host 0.0.0.0 \
  --port 8081 \
  -ngl 999 \
  -c 2048 \
  -b 512 \
  -ub 512 \
  -t 8
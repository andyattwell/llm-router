#!/bin/bash


SCRIPT_DIR=$(dirname "$0")
LLAMA=$(realpath $SCRIPT_DIR/../llama.cpp/build-cuda/bin/)
MODELS_DIR=$(realpath $SCRIPT_DIR/../llama-models)

cd "$LLAMA" && exec llama-server \
  -m ${MODELS_DIR}/gemma-4-E4B-it-Q5_K_Mgguf \
  --mmproj ${MODELS_DIR}/gemma-4-E4B-it-Q5_K_M-mmproj-F16.gguf \
  --port 8082 \
  -ngl 999 \
  -c 4096 \
  -b 512 \
  -ub 512 \
  -t 8 \
  --timeout 600
#!/bin/bash


SCRIPT_DIR=$(dirname "$0")
LLAMA=$(realpath $SCRIPT_DIR/../llama.cpp/build-cuda/bin/)
MODEL=$(realpath $SCRIPT_DIR/models/gemma-4-E4B-it-Q5_K_M.gguf)
MMPROJ=$(realpath $SCRIPT_DIR/models/gemma-4-E4B-it-Q5_K_M-mmproj-F16.gguf)

cd "$LLAMA" && exec llama-server \
  -m ${MODEL} \
  --mmproj ${MMPROJ} \
  --port 8082 \
  -ngl 999 \
  -c 4096 \
  -b 512 \
  -ub 512 \
  -t 8 \
  --timeout 600
#!/bin/bash


SCRIPT_DIR=$(dirname "$0")
LLAMA=$(realpath $SCRIPT_DIR/../llama.cpp/build-cuda/bin/)
MODEL=$(realpath $SCRIPT_DIR/models/Qwen3-VL-8B-Instruct-Q4_K_M.gguf)
MMPROJ=$(realpath $SCRIPT_DIR/models/mmproj-qwen2-vl-7b-instruct-f16.gguf)

cd "$LLAMA" && exec llama-server \
  -m ${MODEL} \
  --mmproj ${MMPROJ} \
  --host 0.0.0.0 \
  --port 8083 \
  -ngl 20 \
  -c 2048 \
  -b 128 \
  -ub 128 \
  -t 8 \
  --timeout 300
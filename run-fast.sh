#!/bin/bash

# Get from args
BINARY_NAME="llama-server"
SCRIPT_DIR=$(dirname "$0")
LLAMA_CPP_PATH=$(realpath $SCRIPT_DIR/../llama.cpp/build-cuda/bin/) # resolve absolute path
MODELS_DIR=$(realpath $SCRIPT_DIR/../llama-models)

LLAMA_MODEL_PATH=$(realpath $MODELS_DIR/gemma-4-E4B-it-Q5_K_M.gguf) # resolve absolute
MMPROJ_PATH=$(realpath $MODELS_DIR/gemma-4-E4B-it-Q5_K_M-mmproj-F16.gguf) # resolve absolute

HOST=127.0.0.1
PORT=8081
CTX=4096
ARGS="-ngl 999 -t 8 -c 2048 --jinja -b 512 -ub 512"

ARGS+=" --host $HOST --port $PORT --sleep-idle-seconds -1"
# Keep multimodal projector on CPU unless LLAMA_MMPROJ_GPU_OFFLOAD=1 (avoids null CUDA
# buffer alloc / abort when VRAM is tight or for Gemma4 mmproj + CUDA offload quirks).
if [[ -f "$MMPROJ_PATH" && "${LLAMA_MMPROJ_GPU_OFFLOAD:-}" != "1" ]]; then
    ARGS+=" --no-mmproj-offload"
fi

cd "$LLAMA_CPP_PATH" && \

exec "$BINARY_NAME" -m "$LLAMA_MODEL_PATH" --mmproj "$MMPROJ_PATH" $ARGS

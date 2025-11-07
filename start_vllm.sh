#!/bin/bash
# Script to start vLLM on RunPod pod

# Start vLLM server with Hermes-2-Pro-Mistral-7B model
python3 -m vllm.entrypoints.openai.api_server \
    --model ${MODEL_NAME:-NousResearch/Hermes-2-Pro-Mistral-7B} \
    --host ${HOST:-0.0.0.0} \
    --port ${PORT:-8000} \
    --trust-remote-code \
    --enable-auto-tool-choice \
    --tool-call-parser hermes \
    --max-model-len ${MAX_MODEL_LEN:-4096} \
    --gpu-memory-utilization ${GPU_MEMORY_UTILIZATION:-0.95} \
    --tensor-parallel-size ${TENSOR_PARALLEL_SIZE:-1}

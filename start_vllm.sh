#!/bin/bash
# Script to start vLLM on RunPod pod

# Start vLLM server with Hermes-2-Pro-Mistral-7B model
python -m vllm.entrypoints.openai.api_server \
      --model Qwen/Qwen3-8B \
      --host 0.0.0.0 \
      --port 8000 \
      --enable-auto-tool-choice \
      --tool-call-parser hermes \
      --reasoning-parser deepseek_r1 \
      --gpu-memory-utilization 0.95 \
      --max-model-len 8192

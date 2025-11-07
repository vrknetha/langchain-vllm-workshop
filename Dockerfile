# RunPod vLLM Deployment - Hermes-2-Pro-Mistral-7B
FROM runpod/pytorch:2.4.0-py3.11-cuda12.4.1-devel-ubuntu22.04

# Install vLLM and dependencies
RUN pip install --no-cache-dir \
    vllm \
    requests \
    python-dotenv

# Set working directory
WORKDIR /workspace

# Copy startup script
COPY start_vllm.sh /workspace/start_vllm.sh
RUN chmod +x /workspace/start_vllm.sh

# Environment variables for vLLM
ENV MODEL_NAME="NousResearch/Hermes-2-Pro-Mistral-7B"
ENV HOST="0.0.0.0"
ENV PORT="8000"
ENV GPU_MEMORY_UTILIZATION="0.95"
ENV MAX_MODEL_LEN="4096"
ENV TENSOR_PARALLEL_SIZE="1"

# Expose port
EXPOSE 8000

# Start vLLM server
CMD ["/workspace/start_vllm.sh"]

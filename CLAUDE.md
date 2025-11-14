# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a LangChain v1 + vLLM + LangGraph workshop demonstrating a **Career Transition Advisor** agent. The project showcases:

- **LangGraph v1** state machine framework with simplified patterns
- **vLLM** for GPU-accelerated inference (deployed on RunPod)
- **Firecrawl MCP** tools for real-time web research
- **PostgreSQL persistence** with AsyncPostgresSaver for production-ready conversation storage
- **Thread-based memory** that persists across restarts
- **Dual UI options**: LangGraph Studio (built-in) + Next.js chat interface

Key demonstration: Multi-turn conversation agent that maintains context across turns, uses web research tools, and provides personalized career guidance.

## Common Commands

### Prerequisites

**Start PostgreSQL Database** (required):
```bash
# Start PostgreSQL in Docker
docker-compose up -d

# Verify PostgreSQL is running
docker-compose ps

# View logs if needed
docker-compose logs -f postgres
```

### Installation
```bash
# Recommended (uses uv for faster installs)
uv pip install -r requirements.txt

# Or standard pip
pip install -r requirements.txt
```

### Running the Agent

**Development Mode** (hot reload, in-memory storage):
```bash
langgraph dev --port 2024
# API: http://localhost:2024
# Studio UI: http://localhost:2024 (built-in chat interface)
# Note: Uses in-memory storage, conversation history lost on restart
```

**Production Mode** (PostgreSQL persistence):
```bash
langgraph up --port 2024
# API: http://localhost:2024
# Studio UI: http://localhost:2024 (built-in chat interface)
# Note: PostgreSQL must be running (docker-compose up -d)
# Note: Reads POSTGRES_URI from .env automatically
# Conversation history persists across restarts
```

**Alternative (explicit postgres-uri flag):**
```bash
langgraph up --port 2024 --postgres-uri "postgresql://langchain:langchain_dev_password@localhost:5432/langchain_db"
```

**Standalone Mode** (educational/testing):
```bash
python -m src.career_advisor.agent
# Initializes agent, creates tables, and prints info
# Note: This mode is for testing only
```

### Database Management

**Stop PostgreSQL**:
```bash
docker-compose down
# Data persists in postgres_data volume
```

**Reset Database** (clear all conversation history):
```bash
docker-compose down -v  # Removes volumes
docker-compose up -d    # Fresh database
```

**Access PostgreSQL CLI**:
```bash
docker exec -it langchain-postgres psql -U langchain -d langchain_db
# Then: \dt to list tables
```

### Frontend Chat UI
```bash
cd agent-chat-ui
pnpm install
pnpm dev
# Runs at http://localhost:3000
```

### vLLM Deployment (on RunPod pod)
```bash
./start_vllm.sh
# Starts OpenAI-compatible API on port 8000
# Model loads in 2-3 minutes
```

## Architecture: How Components Work Together

### High-Level Flow
```
User (Studio UI or Next.js)
  → LangGraph API Server (port 2024)
    → StateGraph with MessagesState
      → call_model() async node
        → ChatOpenAI client
          → RunPod vLLM endpoint
            → Hermes-2-Pro-Mistral-7B model
      → ToolNode (when LLM requests tools)
        → Firecrawl MCP Server (via npx)
          → firecrawl_search, firecrawl_scrape, etc.
```

### LangGraph v1 Simplifications

This codebase demonstrates **modern LangGraph v1 patterns** that replace older boilerplate:

1. **`MessagesState`** - No custom state class needed
   - Built-in message list management
   - Automatic thread-based conversation history
   - Replaces custom `class AgentState(TypedDict)` definitions

2. **`tools_condition`** - Built-in routing function
   - Automatically routes to tool node when LLM calls tools
   - Routes to END when LLM produces final response
   - Replaces ~18 lines of custom `should_continue()` logic

3. **`async call_model()`** - Async node for better I/O performance
   - Uses `ainvoke()` for non-blocking execution
   - Critical for web research tools that have network latency
   - System prompt injection handled within node

4. **PostgreSQL persistence** - Production-ready conversation storage
   - `AsyncPostgresSaver` configured in code with automatic table creation
   - Works with both `langgraph dev` and `langgraph up`
   - Requires PostgreSQL running (via Docker Compose)
   - Thread-based conversation history persists across restarts

### MCP (Model Context Protocol) Integration

The agent connects to **Firecrawl MCP server** via stdio transport:

```python
mcp_client = MultiServerMCPClient({
    "firecrawl": {
        "transport": "stdio",
        "command": "npx",
        "args": ["-y", "firecrawl-mcp"]
    }
})
```

**Available Tools:**
- `firecrawl_search` - Web search (query + limit)
- `firecrawl_scrape` - Extract content from URLs
- `firecrawl_map` - Crawl website structure
- `firecrawl_crawl` - Batch page crawling
- `firecrawl_check_crawl_status` - Monitor crawl jobs
- `firecrawl_extract` - Structured data extraction

**CRITICAL: Tool Usage Rules**
- **NEVER** use the `sources` parameter in `firecrawl_search` - it causes validation errors
- **ONLY** use `query` (required) and `limit` (optional) parameters
- Correct: `{"query": "machine learning engineer skills 2024", "limit": 5}`
- Wrong: `{"query": "...", "sources": ["web"]}` ← THIS WILL FAIL

This constraint is enforced in the system prompt in `src/career_advisor/prompts.py`.

### vLLM + RunPod Integration

The agent uses **ChatOpenAI** client pointed at a **RunPod vLLM endpoint**:

```python
llm = ChatOpenAI(
    api_key=SecretStr(RUNPOD_API_KEY),
    base_url=RUNPOD_ENDPOINT_URL,  # e.g., https://xxx-8000.proxy.runpod.net/v1
    model="NousResearch/Hermes-2-Pro-Mistral-7B",  # MUST match vLLM server model
    max_completion_tokens=2048,
    temperature=0.7,
)
```

**Important Configuration Notes:**
- Model name must **exactly match** what vLLM is serving
- Current model: `NousResearch/Hermes-2-Pro-Mistral-7B` (7B parameters)
- vLLM provides OpenAI-compatible API (chat completions endpoint)
- Model context: 4096 tokens (relatively small, prompts are optimized)
- Tool calling: Enabled via `--enable-auto-tool-choice --tool-call-parser hermes`

### Thread-Based Memory with PostgreSQL Persistence

Conversation history is managed by **thread IDs** and stored in **PostgreSQL**:

- Each thread maintains isolated conversation context
- LangGraph CLI automatically handles thread routing
- Messages persist across turns **and across server restarts** (stored in PostgreSQL)
- New thread = fresh conversation (no memory of previous threads)
- Database tables auto-created on first run: `checkpoints`, `checkpoint_blobs`, `checkpoint_writes`

**Demo Example:**
```
Thread A, Turn 1: "I'm Sarah, a Python developer"
Thread A, Turn 2: "What's my name?" → "You're Sarah"

[Server restart - conversation history preserved in PostgreSQL]

Thread A, Turn 3: "What was my job?" → "You're a Python developer"
Thread B, Turn 1: "What's my name?" → "I don't have that information"
```

**PostgreSQL Schema:**
```python
async def create_checkpointer():
    db_uri = f"postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}"
    checkpointer = AsyncPostgresSaver.from_conn_string(db_uri)
    await checkpointer.setup()  # Creates tables automatically
    return checkpointer
```

## Critical Configuration

### Environment Variables (.env)

**Required:**
```bash
# Firecrawl API (get from https://www.firecrawl.dev/)
FIRECRAWL_API_KEY=your-key

# RunPod Configuration
RUNPOD_ENDPOINT_URL=https://your-pod-id-8000.proxy.runpod.net/v1
RUNPOD_API_KEY=your-runpod-key

# PostgreSQL Configuration (for conversation persistence)
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_DB=langchain_db
POSTGRES_USER=langchain
POSTGRES_PASSWORD=langchain_dev_password
```

**Optional (for demo configuration):**
```bash
# Static thread ID for simple demo (default: demo-user-001)
DEFAULT_THREAD_ID=demo-user-001
```

**Optional (for vLLM deployment):**
```bash
MODEL_NAME=NousResearch/Hermes-2-Pro-Mistral-7B
HOST=0.0.0.0
PORT=8000
GPU_MEMORY_UTILIZATION=0.95
MAX_MODEL_LEN=4096
```

### LangGraph CLI Configuration (langgraph.json)

```json
{
  "dependencies": ["."],
  "graphs": {
    "agent": "./src/career_advisor/agent.py:agent"
  },
  "env": ".env"
}
```

Points to the compiled graph object in `src/career_advisor/agent.py`. The graph is built with PostgreSQL checkpointer:
```python
agent = workflow.compile(checkpointer=checkpointer)
```

### External Dependencies

- **Docker & Docker Compose** - Required for PostgreSQL database
- **Node.js** - Required for `npx firecrawl-mcp` (MCP server)
- **RunPod Account** - GPU instance provider
- **Firecrawl API Key** - Free tier available at firecrawl.dev
- **GPU Hardware** - Recommended: NVIDIA A4000 or better

## Development Workflow

### Demo Use Case: Career Transition Advisor

The primary demonstration shows a **multi-turn career advisory conversation**:

1. **Turn 1**: User shares background (current role, experience, goals)
   - Agent acknowledges and builds rapport

2. **Turn 2**: User asks about skills gaps
   - Agent uses `firecrawl_search` to research job requirements
   - Analyzes delta between current skills and target role

3. **Turn 3**: User requests learning resources
   - Agent **remembers** specific skills from Turn 2 (thread memory)
   - Searches for relevant courses/tutorials

4. **Turn 4**: User asks about job targeting
   - Agent synthesizes full conversation history
   - Provides personalized timeline and targets

This demonstrates:
- Thread-based memory (context maintained across turns)
- Tool usage (web research via Firecrawl)
- Multi-step reasoning (synthesis of prior conversation)

### Testing Thread Isolation

Create two separate threads and verify memory isolation:

```python
# Thread 1
{"thread_id": "thread-1", "input": {"messages": [{"role": "user", "content": "I'm Sarah"}]}}
{"thread_id": "thread-1", "input": {"messages": [{"role": "user", "content": "What's my name?"}]}}
# Response: "You're Sarah"

# Thread 2
{"thread_id": "thread-2", "input": {"messages": [{"role": "user", "content": "What's my name?"}]}}
# Response: "I don't have that information"
```

## Docker Setup

This project uses **two separate Dockerfiles** for different purposes:

1. **`Dockerfile`** - LangGraph API application (runs locally via docker-compose)
2. **`Dockerfile.vllm`** - vLLM inference server (deploys to RunPod GPU pods)

### Local Development with Docker Compose

Start all services locally (PostgreSQL, Redis, LangGraph API):
```bash
docker-compose up -d
```

This runs:
- PostgreSQL on port 5432
- Redis on port 6379
- LangGraph API on port 2024 (when using `langgraph dev --port 2024`)

### RunPod vLLM Deployment

#### Option A: Build and Deploy Custom Image
```bash
# Build vLLM Docker image
docker build -f Dockerfile.vllm -t your-dockerhub-username/vllm-hermes:latest .

# Push to Docker Hub
docker push your-dockerhub-username/vllm-hermes:latest

# Deploy on RunPod Console:
# 1. Select GPU (A40, A4000, or A5000)
# 2. Use your custom image
# 3. Expose port 8000
# 4. Wait 2-3 minutes for model to load
```

#### Option B: Deploy via RunPod MCP
```python
# Using RunPod MCP tools
mcp__runpod__create-pod({
    "imageName": "your-dockerhub-username/vllm-hermes:latest",
    "name": "vllm-inference-server",
    "gpuTypeIds": ["NVIDIA A40", "NVIDIA RTX A4000", "NVIDIA RTX A5000"],
    "gpuCount": 1,
    "cloudType": "SECURE",
    "containerDiskInGb": 50,
    "ports": ["8000/http"]
})
```

#### Option C: Use Pre-built Image
```bash
# In RunPod Console:
# 1. Container Image: vrknetha/langchain-vllm-workshop:latest
# 2. Expose port 8000
# 3. Copy endpoint URL to .env as RUNPOD_ENDPOINT_URL
```

**After deployment:**
1. Get pod ID from response (e.g., `403xady32x2mbe`)
2. Endpoint URL format: `https://[pod-id]-8000.proxy.runpod.net/v1`
3. Update `.env` with `RUNPOD_ENDPOINT_URL`
4. Wait 2-3 minutes for vLLM model to load
5. Test: `curl https://[endpoint]/v1/models`

**Dockerfile.vllm Configuration:**
The vLLM server runs with these flags:
- `--model NousResearch/Hermes-2-Pro-Mistral-7B` - 7B parameter model
- `--enable-auto-tool-choice` - Function calling support
- `--tool-call-parser hermes` - Hermes model tool format
- `--gpu-memory-utilization 0.95` - 95% GPU memory usage
- `--max-model-len 4096` - Context window size

## File Structure

### Key Files
- `src/career_advisor/` - LangGraph agent package (Career Advisor)
  - `agent.py` - Graph construction and compilation
  - `config.py` - Configuration management
  - `checkpointer.py` - PostgreSQL persistence setup
  - `tools.py` - MCP tools initialization
  - `prompts.py` - System prompts
  - `nodes.py` - Graph node functions
  - `__init__.py` - Package exports
- `docker-compose.yml` - Multi-service orchestration (PostgreSQL, Redis, LangGraph API)
- `Dockerfile` - LangGraph API application container (for local docker-compose)
- `Dockerfile.vllm` - vLLM inference server container (for RunPod deployment)
- `langgraph.json` - CLI configuration
- `requirements.txt` - Python dependencies (includes langgraph-checkpoint-postgres)
- `.env` - Environment configuration (gitignored)
- `lanchain-vllm.ipynb` - Jupyter notebook demo

### Frontend
- `agent-chat-ui/` - Next.js chat interface
  - Connects to any LangGraph server with MessagesState
  - Configurable API URL and assistant ID

### Generated Files (gitignored)
- `postgres_data/` - Docker volume for PostgreSQL data persistence
- `.langgraph_api/` - CLI cache
- `__pycache__/` - Python bytecode

## Model Configuration

**Current Model**: `NousResearch/Hermes-2-Pro-Mistral-7B`

This model is specifically chosen for:
- Tool calling support (function calling)
- 32,768 token context window
- Good performance on mid-range GPUs (7B parameters)
- Hermes instruction tuning (conversational quality)

**Recommended GPUs** (tested and verified):
- **NVIDIA A40** - 48GB VRAM ($0.40/hr on RunPod) ✅ Primary recommendation
- **NVIDIA RTX A4000** - 16GB VRAM ($0.29/hr on RunPod)
- **NVIDIA RTX A5000** - 24GB VRAM ($0.34/hr on RunPod)

**GPU Requirements**:
- Minimum VRAM: 16GB (for 7B model with FP16)
- Recommended VRAM: 24GB+ (for optimal batch sizes and context length)
- GPU Memory Utilization: 0.95 (95% of VRAM used by vLLM)
- Expected model load time: 2-3 minutes

**If changing models:**
1. Update `MODEL_NAME` in `.env` (for vLLM server)
2. Update `model=` in `src/career_advisor/config.py` (for ChatOpenAI client)
3. Update notebook cell in `lanchain-vllm.ipynb`
4. Verify new model supports tool calling
5. Restart vLLM server with new model

**Note**: Model name must **exactly match** between vLLM server and ChatOpenAI client, or you'll get 404 errors.

## Troubleshooting

### PostgreSQL Connection Errors
**Error: "POSTGRES_PASSWORD environment variable is required"**
- Copy `.env.example` to `.env` and fill in PostgreSQL credentials
- Ensure PostgreSQL password is set in `.env`

**Error: Connection refused to localhost:5432**
- PostgreSQL not running: `docker-compose up -d`
- Check container status: `docker-compose ps`
- View logs: `docker-compose logs -f postgres`

**Error: "relation 'checkpoints' does not exist"**
- Tables are auto-created on first run via `checkpointer.setup()`
- Verify the agent initialized successfully
- Check PostgreSQL logs for permission issues

**Error: psycopg connection errors**
- Ensure `psycopg[binary,pool]>=3.0.0` is installed
- Verify PostgreSQL credentials in `.env` match `docker-compose.yml`

### "Model does not exist" 404 Error
- Check model name matches exactly in `src/agent.py` and vLLM server
- Verify vLLM server has finished loading (takes 2-3 minutes)
- Test endpoint: `curl https://your-pod-8000.proxy.runpod.net/v1/models`

### MCP Tool Validation Errors
- Ensure you're NOT using the `sources` parameter in `firecrawl_search`
- Only use `query` and optionally `limit` parameters
- Check that Node.js is installed (required for `npx firecrawl-mcp`)

### Frontend Not Connecting
- Verify `LANGGRAPH_API_URL` in `agent-chat-ui/.env.local`
- Ensure LangGraph server is running (`langgraph dev`)
- Ensure PostgreSQL is running (`docker-compose up -d`)
- Check CORS settings if deploying to different domain

### Memory/Persistence Issues
- All conversation history now persists in PostgreSQL (both `langgraph dev` and `langgraph up`)
- Thread IDs must be consistent across requests for conversation continuity
- To reset conversation history: `docker-compose down -v && docker-compose up -d`
- Verify PostgreSQL tables exist: `docker exec -it langchain-postgres psql -U langchain -d langchain_db -c "\dt"`

## Resources

- LangGraph Documentation: https://langchain-ai.github.io/langgraph/
- vLLM Documentation: https://docs.vllm.ai/
- Model Context Protocol: https://modelcontextprotocol.io/
- Firecrawl MCP: https://github.com/mendableai/firecrawl-mcp
- RunPod Documentation: https://docs.runpod.io/

# LangGraph + vLLM: Career Advisor with PostgreSQL Memory

An intelligent career transition advisor built with LangGraph, featuring production-ready persistent memory powered by PostgreSQL and vLLM inference.

## Overview

This project demonstrates a stateful AI agent with conversation memory:
- **PostgreSQL Persistence** - Production-ready conversation storage with AsyncPostgresSaver
- **Multi-turn Reasoning** - Maintains context across conversation turns and server restarts
- **Web Research Tools** - Search and scrape capabilities via Firecrawl MCP
- **Live API + Chat UI** - Built-in LangGraph Studio interface
- **Production-ready** - vLLM backend for fast inference + PostgreSQL for scalable persistence

## Key Technologies

- **LangGraph** - State machine framework with built-in memory
- **PostgreSQL** - Production-grade persistent conversation storage
- **AsyncPostgresSaver** - Async checkpointer with connection pooling
- **vLLM** - Fast LLM inference on GPUs (4-24x faster than HuggingFace)
- **Hermes-2-Pro-Mistral-7B** - 7B parameter model with excellent tool calling
- **Firecrawl MCP** - Production web scraping via Model Context Protocol
- **LangGraph CLI** - Built-in API server and Studio UI

## Architecture

```
User Query → LangGraph Agent → [Memory Check] → vLLM + Tools → Response
                                      ↓
                            PostgreSQL Checkpointer
                            (Persistent Memory)
                                      ↓
                            Docker Container
                            (postgres:16-alpine)
```

**Key Features:**
- **Stateful Conversations** - Every message is saved in PostgreSQL
- **Thread-based Memory** - Multiple concurrent conversations with separate memory
- **Persistent Across Restarts** - Conversation history survives server restarts
- **Multi-turn Reasoning** - Agent remembers context from previous turns
- **Tool Integration** - Web search and scraping via Firecrawl MCP
- **Auto-table Creation** - Database schema created automatically on first run

## Quick Start

### 1. Clone the Repository

```bash
git clone <your-repo-url>
cd langchain-vllm
```

### 2. Start PostgreSQL Database

```bash
# Start PostgreSQL in Docker
docker-compose up -d

# Verify it's running
docker-compose ps
```

This creates a PostgreSQL 16 container with:
- Database: `langchain_db`
- User: `langchain`
- Port: `5432`
- Persistent volume: `postgres_data`

### 3. Install Dependencies

```bash
uv pip install -r requirements.txt
```

Or with pip:
```bash
pip install -r requirements.txt
```

### 4. Configure Environment

```bash
cp .env.example .env
# Edit .env with your API keys, RunPod endpoint, and PostgreSQL credentials
```

Required variables:
- `FIRECRAWL_API_KEY` - Get from [firecrawl.dev](https://www.firecrawl.dev/)
- `RUNPOD_ENDPOINT_URL` - Your RunPod vLLM endpoint
- `RUNPOD_API_KEY` - Your RunPod API key
- `POSTGRES_PASSWORD` - Set to `langchain_dev_password` (matches docker-compose.yml)

### 5. Deploy vLLM on RunPod

**Option A: Use Pre-built Docker Image (Fastest):**

1. Go to RunPod Console → Deploy Pod
2. Select GPU (A4000 or better recommended)
3. Under "Container Image", enter: `vrknetha/langchain-vllm-workshop:latest`
4. Set Container Disk: 50GB+
5. Expose port: 8000
6. Deploy and wait for startup
7. Copy the endpoint URL to `.env`

**Option B: Build Custom Image:**
```bash
# Build vLLM Docker image
docker build -f Dockerfile.vllm -t your-dockerhub-username/vllm-hermes:latest .

# Push to Docker Hub
docker push your-dockerhub-username/vllm-hermes:latest

# Deploy on RunPod using your custom image
```

See [DEPLOYMENT.md](DEPLOYMENT.md) for detailed instructions.

### 6. Start the LangGraph Server

**For Development (Hot Reload, In-Memory):**
```bash
langgraph dev --port 2024
# Uses in-memory storage, conversation history lost on restart
```

**For Production (PostgreSQL Persistence):**
```bash
langgraph up --port 2024
# Reads POSTGRES_URI from .env automatically
# Conversation history persists across restarts
```

**Alternative (explicit postgres-uri):**
```bash
langgraph up --port 2024 --postgres-uri "postgresql://langchain:langchain_dev_password@localhost:5432/langchain_db"
```

Both modes now use PostgreSQL for persistence. The server will start at:
- **API**: http://localhost:2024
- **Studio UI**: http://localhost:2024 (built-in chat interface)

On first run, the agent automatically creates PostgreSQL tables:
- `checkpoints` - Conversation state snapshots
- `checkpoint_blobs` - Large binary data
- `checkpoint_writes` - Checkpoint write operations

## 🎯 Demo: Career Transition Advisor

This project showcases a **Career Transition Advisor** - a compelling demo that demonstrates LangGraph v1's memory and state management features through a real-world use case.

### What It Does

The Career Advisor helps professionals navigate career transitions by:
- **Understanding context**: Captures background, skills, and goals through conversation
- **Real-time research**: Uses Firecrawl to search job markets, requirements, and learning resources
- **Skills gap analysis**: Compares current skills with target role requirements
- **Personalized guidance**: Creates tailored learning paths and job targets
- **Persistent memory**: Maintains full context across multiple conversation turns within a thread

### Why It's Compelling

1. **Universal Appeal** - Everyone thinks about career growth and skill development
2. **Emotional Resonance** - Career anxiety and uncertainty are widely relatable
3. **Multi-turn Intelligence** - Showcases the power of persistent conversation memory
4. **Practical Value** - Solves a real problem people face daily
5. **Technical Showcase** - Demonstrates all key LangGraph v1 features elegantly

### Demo Script

See **[DEMO_CAREER.md](DEMO_CAREER.md)** for the complete 10-minute demo script with:
- Pre-demo checklist
- Turn-by-turn conversation flow with expected behaviors
- What to highlight at each step
- LangGraph Studio UI walkthrough
- Thread isolation demonstration
- Troubleshooting common issues
- Q&A preparation

### Quick Demo Example

```
Turn 1: "I'm Sarah, a Python developer with 5 years experience, wanting to transition into AI/ML"
→ Agent: Acknowledges background, begins building relationship

Turn 2: "What skills am I missing?"
→ Agent: Searches job requirements, analyzes skills gap, leverages Python as foundation

Turn 3: "Find me courses for those skills"
→ Agent: Remembers specific skills from Turn 2, finds relevant learning resources

Turn 4: "What jobs can I target in 6 months?"
→ Agent: Synthesizes full conversation context, suggests realistic targets

Thread Isolation Test:
→ New thread: "What's my name?" → "I don't have that information"
→ Original thread: "What's my name?" → "You're Sarah, the Python developer..."
```

### Key Features Demonstrated

- **MessagesState** - LangGraph v1's prebuilt state class (no custom classes needed)
- **tools_condition** - Automatic routing (replaces 18 lines of custom logic)
- **Platform Persistence** - Thread-based memory managed by LangGraph CLI
- **Async Patterns** - Better I/O performance with ainvoke()
- **MCP Integration** - Standardized tool protocol with Firecrawl

### Alternative Demo: Short-Term Memory Research Assistant

For a simpler, generic research demo, see below.

### Example Conversation Flow

Here's how to demonstrate the memory features:

**Turn 1: Set Context**
```
User: "My name is Alex and I'm interested in electric vehicles"
Agent: "Nice to meet you, Alex! I'd be happy to help you learn about electric vehicles..."
```

**Turn 2: Follow-up (Uses Memory)**
```
User: "What are the top 3 options?"
Agent: [Searches for electric vehicles, remembers Alex is interested in EVs]
```

**Turn 3: Deep Dive (Uses Full Context)**
```
User: "Which one is best for long road trips?"
Agent: [Analyzes previous search results, considers Alex's needs, provides recommendation]
```

**Turn 4: New Thread Test**
```
User: [In a new thread] "What's my name?"
Agent: "I don't have that information yet..."
[Demonstrates thread isolation - each conversation has separate memory]
```

### Memory Features Demonstrated

1. **Conversation Continuity** - Agent remembers what was discussed
2. **Thread Isolation** - Each conversation thread has separate memory
3. **Persistence** - Memory survives server restarts (with `langgraph up`)
4. **State Inspection** - View full conversation history in Studio UI

## What You'll Learn

1. **LangGraph State Machines** - Building agents with StateGraph
2. **Checkpointing** - SQLite-based persistent memory
3. **Multi-turn Reasoning** - Context-aware conversations
4. **MCP Integration** - Direct tool access for web search/scraping
5. **Production Deployment** - API + UI with LangGraph CLI

## Requirements

- Python 3.10+
- Docker & Docker Compose (for PostgreSQL database)
- Node.js (for npx/Firecrawl MCP)
- Firecrawl API key (get free at [firecrawl.dev](https://www.firecrawl.dev/))
- RunPod account with GPU credits

## Understanding Memory Modes

### Development Mode: `langgraph dev`
- **Memory**: In-memory storage (langgraph_runtime_inmem)
- **Persistence**: NOT persistent - conversation history lost on restart
- **Reload**: Hot reload on code changes
- **Use case**: Fast development iteration

### Production Mode: `langgraph up --postgres-uri`
- **Memory**: PostgreSQL checkpointer
- **Persistence**: Survives server restarts (stored in PostgreSQL)
- **Reload**: Requires rebuild for code changes
- **Use case**: Development and testing
- **Pros**: Fast iteration + persistent memory
- **Requires**: PostgreSQL running (`docker-compose up -d`)

### Production Mode: `langgraph up`
- **Memory**: PostgreSQL checkpointer
- **Persistence**: Full production persistence in PostgreSQL
- **Reload**: Manual restart required
- **Use case**: Production deployments and demos
- **Pros**: Production-ready with persistent memory
- **Requires**: PostgreSQL running (`docker-compose up -d`)

### Standalone Mode: `python src/agent.py`
- **Memory**: PostgreSQL checkpointer
- **Persistence**: PostgreSQL database
- **Use case**: Testing agent initialization and table creation
- **Note**: This mode initializes the agent and displays configuration info
- **Requires**: PostgreSQL running (`docker-compose up -d`)

### Database Management

**View conversation history:**
```bash
docker exec -it langchain-postgres psql -U langchain -d langchain_db

# List tables
\dt

# View checkpoints
SELECT thread_id, checkpoint_id FROM checkpoints;

# Exit
\q
```

**Reset all conversations:**
```bash
docker-compose down -v  # Removes volumes
docker-compose up -d    # Fresh database
```

**Stop PostgreSQL:**
```bash
docker-compose down  # Data persists in volume
```

## Project Structure

```
langchain-vllm/
├── src/
│   └── career_advisor/     # LangGraph agent package
│       ├── __init__.py     # Package exports
│       ├── config.py       # Configuration management
│       ├── checkpointer.py # PostgreSQL persistence
│       ├── tools.py        # MCP tools setup
│       ├── prompts.py      # System prompts
│       ├── nodes.py        # Graph nodes
│       └── agent.py        # Graph construction
├── docker-compose.yml      # PostgreSQL database configuration
├── langgraph.json          # LangGraph CLI configuration
├── requirements.txt        # Python dependencies (includes postgres libs)
├── .env                    # Environment variables (API keys + DB config)
├── start_vllm.sh           # vLLM startup script
└── README.md               # This file
```

## Troubleshooting

### PostgreSQL Issues

**"POSTGRES_PASSWORD environment variable is required"**
- Copy `.env.example` to `.env`
- Set `POSTGRES_PASSWORD=langchain_dev_password`

**Connection refused to localhost:5432**
- Start PostgreSQL: `docker-compose up -d`
- Check status: `docker-compose ps`
- View logs: `docker-compose logs -f postgres`

**"relation 'checkpoints' does not exist"**
- Tables are auto-created on first run via `checkpointer.setup()`
- Verify agent initialized successfully
- Check logs for PostgreSQL permissions issues

**Memory not persisting?**
- PostgreSQL must be running (`docker-compose up -d`)
- Verify the same `thread_id` is used across requests
- Check PostgreSQL tables exist: `docker exec -it langchain-postgres psql -U langchain -d langchain_db -c "\dt"`

### vLLM Issues

**Model loading slow?**
- First request takes 2-3 minutes to load model into vLLM
- Pre-warm the endpoint before presentations with a test query

**"Model does not exist" 404 error**
- Check model name matches in `src/agent.py` and vLLM server
- Verify vLLM has finished loading (2-3 minutes)
- Test: `curl https://your-pod-8000.proxy.runpod.net/v1/models`

### MCP/Tools Issues

**Firecrawl search errors?**
- If you see "sources parameter validation failed", this is expected - the system prompt instructs the LLM to avoid using the `sources` parameter
- Verify `FIRECRAWL_API_KEY` is set in `.env`
- Check that Node.js is installed (required for `npx`)
- Ensure `npx -y firecrawl-mcp` can run manually

**Tools not working?**
- Verify all required environment variables are set in `.env`
- Check that Node.js is installed (required for `npx`)
- Review the server logs for any MCP connection errors

### Server Issues

**Server not starting?**
- Verify all dependencies installed: `uv pip install -r requirements.txt`
- Ensure PostgreSQL is running: `docker-compose ps`
- Check port 8123 is not already in use
- Look for errors in the console output

## Resources

- [LangGraph Documentation](https://langchain-ai.github.io/langgraph/)
- [LangGraph Memory Guide](https://langchain-ai.github.io/langgraph/concepts/persistence/)
- [LangGraph CLI Documentation](https://langchain-ai.github.io/langgraph/concepts/langgraph_cli/)
- [vLLM Documentation](https://docs.vllm.ai/)
- [Model Context Protocol](https://modelcontextprotocol.io/)
- [Firecrawl MCP Server](https://github.com/mendableai/firecrawl-mcp)
- [RunPod Documentation](https://docs.runpod.io/)

## License

MIT License - See LICENSE file for details

## Contributing

Contributions welcome! Please open an issue or PR.

## Acknowledgments

- LangChain team for the excellent framework
- vLLM team for blazing-fast inference
- NousResearch for Hermes-2-Pro-Mistral-7B
- Firecrawl for production-ready web scraping

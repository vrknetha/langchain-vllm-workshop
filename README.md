# LangGraph + vLLM: Research Assistant with Memory

An intelligent research assistant built with LangGraph, featuring persistent short-term memory powered by SQLite and vLLM inference.

## Overview

This project demonstrates a stateful AI agent with conversation memory:
- **Persistent Memory** - Platform-managed persistence with configurable backends
- **Multi-turn Reasoning** - Maintains context across conversation turns
- **Web Research Tools** - Search and scrape capabilities via Firecrawl MCP
- **Live API + Chat UI** - Built-in LangGraph Studio interface
- **Production-ready** - vLLM backend for fast inference

## Key Technologies

- **LangGraph** - State machine framework with built-in memory
- **Platform-managed Persistence** - Automatic conversation storage
- **vLLM** - Fast LLM inference on GPUs (4-24x faster than HuggingFace)
- **Hermes-2-Pro-Mistral-7B** - 7B parameter model with excellent tool calling
- **Firecrawl MCP** - Production web scraping via Model Context Protocol
- **LangGraph CLI** - Built-in API server and Studio UI

## Architecture

```
User Query → LangGraph Agent → [Memory Check] → vLLM + Tools → Response
                                      ↓
                              SQLite Checkpointer
                              (Persistent Memory)
```

**Key Features:**
- **Stateful Conversations** - Every message is saved with platform persistence
- **Thread-based Memory** - Multiple concurrent conversations with separate memory
- **Multi-turn Reasoning** - Agent remembers context from previous turns
- **Tool Integration** - Web search and scraping via Firecrawl MCP

## Quick Start

### 1. Clone the Repository

```bash
git clone <your-repo-url>
cd langchain-vllm
```

### 2. Install Dependencies

```bash
uv pip install -r requirements.txt
```

Or with pip:
```bash
pip install -r requirements.txt
```

### 3. Configure Environment

```bash
cp .env.example .env
# Edit .env with your API keys and RunPod endpoint
```

### 4. Deploy vLLM on RunPod

**Option A: Use Pre-built Docker Image (Fastest):**

1. Go to RunPod Console → Deploy Pod
2. Select GPU (A4000 or better recommended)
3. Under "Container Image", enter: `vrknetha/langchain-vllm-workshop:latest`
4. Set Container Disk: 50GB+
5. Expose port: 8000
6. Deploy and wait for startup
7. Copy the endpoint URL to `.env`

**Option B: Manual Setup:**
1. Deploy a RunPod pod with PyTorch template
2. SSH in and run `./start_vllm.sh`
3. Copy the endpoint URL to `.env`

See [DEPLOYMENT.md](DEPLOYMENT.md) for detailed instructions.

### 5. Start the LangGraph Server

**For Development (In-Memory, Hot Reload):**
```bash
langgraph dev
```

**For Demo (SQLite Persistence):**
```bash
langgraph up
```

The server will start at:
- **API**: http://localhost:8123
- **Studio UI**: http://localhost:8123 (built-in chat interface)

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
- Node.js (for npx/Firecrawl MCP)
- Firecrawl API key (get free at [firecrawl.dev](https://www.firecrawl.dev/))
- RunPod account with GPU credits

## Understanding Memory Modes

### Development Mode: `langgraph dev`
- **Memory**: Platform-managed (in-memory runtime)
- **Persistence**: In-memory only (lost on restart)
- **Reload**: Hot reload on code changes
- **Use case**: Development and testing
- **Pros**: Fast iteration, no setup required
- **Cons**: Memory doesn't persist across restarts

### Production Mode: `langgraph up`
- **Memory**: Platform-managed (can configure PostgreSQL)
- **Persistence**: Configurable via `POSTGRES_URI` environment variable
- **Reload**: Manual restart required
- **Use case**: Demos and production deployments
- **Pros**: Persistent memory, production-ready
- **Cons**: No hot reload

### Standalone Mode: `python main.py`
- **Memory**: Custom SQLite checkpointer
- **Persistence**: SQLite database (`checkpoints.db`)
- **Use case**: Testing without server, educational purposes
- **Note**: This mode is for understanding the code structure. Use server modes for actual demos.

**Important**: When using LangGraph CLI (`langgraph dev` or `langgraph up`), the platform automatically handles persistence. The code detects this and disables the custom checkpointer to avoid conflicts.

### When to Use Each

**Use `langgraph dev` when:**
- Actively developing/debugging
- Making code changes frequently
- Memory persistence not needed

**Use `langgraph up` when:**
- Giving a demo
- Need to show persistent memory
- Testing production behavior
- Want conversation history across restarts

## Project Structure

```
langchain-vllm/
├── main.py                 # LangGraph agent with SQLite memory
├── langgraph.json          # LangGraph CLI configuration
├── requirements.txt        # Python dependencies
├── .env                    # Environment variables (API keys)
├── checkpoints.db          # SQLite memory database (generated)
├── start_vllm.sh           # vLLM startup script
└── README.md               # This file
```

## Troubleshooting

**Memory not persisting?**
- Make sure you're using `langgraph up` (not `langgraph dev`)
- Check that `checkpoints.db` file is created in the project directory
- Verify the same `thread_id` is used across requests

**Model loading slow?**
- First request takes 2-3 minutes to load model into vLLM
- Pre-warm the endpoint before presentations with a test query

**Firecrawl search errors?**
- If you see "sources parameter validation failed", this is expected - the system prompt instructs the LLM to avoid using the `sources` parameter
- Verify `FIRECRAWL_API_KEY` is set in `.env`
- Check that Node.js is installed (required for `npx`)
- Ensure `npx -y firecrawl-mcp` can run manually

**Tools not working?**
- Verify all required environment variables are set in `.env`
- Check that Node.js is installed (required for `npx`)
- Review the server logs for any MCP connection errors

**Server not starting?**
- Verify all dependencies installed: `uv pip install -r requirements.txt`
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

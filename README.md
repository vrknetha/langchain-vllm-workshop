# LangChain v1 + vLLM Workshop: AI Job Application Assistant

A hands-on workshop demonstrating how to build intelligent agents using LangChain v1, vLLM, and Model Context Protocol (MCP).

## Overview

This workshop teaches you to build an AI agent that helps students with job applications:
- **Find real jobs** by scraping live job boards using Firecrawl MCP
- **Score resume fit** by analyzing skills match
- **Generate personalized cover letters** tailored to each role
- **Make intelligent decisions** using autonomous multi-step reasoning

## Key Technologies

- **LangChain v1** - Modern agent framework with `create_agent()`
- **vLLM** - Fast LLM inference on GPUs (4-24x faster than HuggingFace)
- **Hermes-2-Pro-Mistral-7B** - 7B parameter model with excellent tool calling
- **Firecrawl MCP** - Production web scraping via Model Context Protocol
- **RunPod** - GPU infrastructure for vLLM deployment

## Architecture

```
User Query → vLLM Agent → MCP Tools → Real Job Data
                ↓
        [Firecrawl Scraping | LLM Reasoning | Response Generation]
```

**Key Design Principle:** The agent receives MCP tools directly and uses its intelligence to decide when/how to use them. No unnecessary wrapper functions!

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

See [DEPLOYMENT.md](DEPLOYMENT.md) for detailed instructions.

**Quick option:**
1. Deploy a RunPod pod with PyTorch template
2. SSH in and run `./start_vllm.sh`
3. Copy the endpoint URL to `.env`

### 5. Run the Workshop

```bash
jupyter notebook lanchain-vllm.ipynb
```

## What You'll Learn

1. **LangChain v1 Architecture** - Modern agent patterns with `create_agent()`
2. **MCP Integration** - Direct tool access without wrapper functions
3. **Agentic AI Principles** - Let LLMs reason, use tools for external data only
4. **vLLM Deployment** - Fast inference on GPU infrastructure
5. **Multi-step Reasoning** - Autonomous planning and execution

## Notebook Structure

1. **Setup** - Install dependencies and load environment
2. **Connect to MCP** - Get Firecrawl tools for web scraping
3. **Initialize vLLM** - Connect to RunPod endpoint
4. **Build Agent** - Create LangChain v1 agent with direct tool access
5. **Live Demos** - Progressive complexity demonstrations

## Demo Scenarios

**Demo 1: Simple Job Search**
- Agent constructs URL and scrapes job listings

**Demo 2: Multi-step Reasoning**
- Agent searches jobs, analyzes fit, recommends best match

**Demo 3: Full Autonomous Workflow**
- Agent finds jobs, scores resume, writes cover letter

## Requirements

- Python 3.10+
- Jupyter Notebook
- Firecrawl API key (get free at [firecrawl.dev](https://www.firecrawl.dev/))
- RunPod account with GPU credits

## Deployment Options

### For Presentations (Recommended):
- Use RunPod pre-deployed pod
- Quick setup: 5 minutes
- Cost: ~$0.29/hr (A4000 spot instance)

### For Production:
- Custom Docker image with model baked in
- Zero cold start time
- See [DEPLOYMENT.md](DEPLOYMENT.md)

## Project Structure

```
langchain-vllm/
├── lanchain-vllm.ipynb    # Workshop notebook
├── requirements.txt        # Python dependencies
├── .env.example           # Environment template
├── Dockerfile             # RunPod deployment
├── start_vllm.sh          # vLLM startup script
├── DEPLOYMENT.md          # Deployment guide
└── README.md              # This file
```

## Troubleshooting

**Model loading slow?**
- First request takes 2-3 minutes to load model
- Pre-warm the endpoint before presentations

**Firecrawl timeouts?**
- Default timeout is 60 seconds
- Some job sites take longer to scrape
- Use simpler sites for demos

**Out of memory?**
- Reduce `GPU_MEMORY_UTILIZATION` to 0.85
- Use A5000 or better GPU
- Enable quantization if needed

## Resources

- [LangChain v1 Documentation](https://python.langchain.com/)
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

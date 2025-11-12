"""
LangGraph Agent with vLLM, Firecrawl MCP Tools, and SQLite Memory
This module creates a stateful agent with persistent memory that can be served by LangGraph CLI
"""
import os
from langchain_openai import ChatOpenAI
from langchain_mcp_adapters.client import MultiServerMCPClient
from langgraph.graph import StateGraph, MessagesState, START
from langgraph.prebuilt import ToolNode, tools_condition
from pydantic import SecretStr
from dotenv import load_dotenv
import asyncio

# Load environment variables from .env file
load_dotenv()

# Get API keys from environment with validation
RUNPOD_ENDPOINT_URL = os.getenv("RUNPOD_ENDPOINT_URL")
RUNPOD_API_KEY = os.getenv("RUNPOD_API_KEY")
FIRECRAWL_API_KEY = os.getenv("FIRECRAWL_API_KEY")

# Validate required environment variables
if not RUNPOD_ENDPOINT_URL:
    raise ValueError("RUNPOD_ENDPOINT_URL environment variable is required")
if not RUNPOD_API_KEY:
    raise ValueError("RUNPOD_API_KEY environment variable is required")
if not FIRECRAWL_API_KEY:
    raise ValueError("FIRECRAWL_API_KEY environment variable is required")

# Initialize vLLM model via OpenAI-compatible API
llm = ChatOpenAI(
    api_key=SecretStr(RUNPOD_API_KEY),
    base_url=RUNPOD_ENDPOINT_URL,
    model="Qwen/Qwen3-8B",
    max_completion_tokens=2048,
    temperature=0.7,
)

# Enhanced system prompt for career advising with multi-turn reasoning
system_prompt = """You are an expert career advisor and learning coach with access to real-time web research tools.

Your role is to help professionals transition their careers by:
- Understanding their current skills, experience, and goals
- Researching job market trends and requirements
- Identifying skills gaps and learning paths
- Finding quality learning resources
- Tracking progress over multiple conversations

## Your Capabilities:
- Use firecrawl_search to find job postings, market trends, course offerings
- Use firecrawl_scrape to get detailed content from career sites, job boards, learning platforms
- Remember everything from previous messages in this conversation
- Provide personalized, actionable advice based on the user's unique background

## Conversation Style:
- Start by understanding their background (current role, experience, target role)
- Ask clarifying questions when needed
- Be encouraging and supportive about career transitions
- Provide specific, actionable next steps
- Reference previous conversations ("You mentioned Python experience...")

## CRITICAL TOOL USAGE RULES for firecrawl_search:
- NEVER use the 'sources' parameter - it will cause an error
- ONLY use 'query' (required) and 'limit' (optional) parameters
- The sources parameter is broken and must be avoided completely
- Correct example: {"query": "machine learning engineer skills 2024", "limit": 5}
- Wrong example: {"query": "...", "sources": ["web"]} ← THIS WILL FAIL

Be conversational, empathetic, and practical."""

# Create MCP client and get tools
async def create_mcp_tools():
    """Initialize MCP client and retrieve Firecrawl tools"""
    mcp_client = MultiServerMCPClient({
        "firecrawl": {
            "transport": "stdio",
            "command": "npx",
            "args": ["-y", "firecrawl-mcp"]
        }
    })
    return await mcp_client.get_tools()

# Initialize tools using asyncio.run() at module level
tools = asyncio.run(create_mcp_tools())

# Bind tools to the LLM
llm_with_tools = llm.bind_tools(tools)

# Define the agent node with async support
async def call_model(state: MessagesState):
    """
    Career Advisor agent node that processes messages with context awareness.

    - Maintains conversation history for personalized career guidance
    - Uses async invocation for better performance with web research tools
    - Automatically includes system prompt for consistent career advisor behavior
    """
    from langchain_core.messages import SystemMessage

    messages = state["messages"]

    # Add system prompt if this is the first message in the conversation
    if not messages or messages[0].type != "system":
        messages = [SystemMessage(content=system_prompt)] + messages

    response = await llm_with_tools.ainvoke(messages)
    return {"messages": [response]}

# Create the graph using MessagesState directly
workflow = StateGraph(MessagesState)

# Add nodes
workflow.add_node("agent", call_model)
workflow.add_node("tools", ToolNode(tools))

# Add edges
workflow.add_edge(START, "agent")

# Use built-in tools_condition for routing
workflow.add_conditional_edges("agent", tools_condition)
workflow.add_edge("tools", "agent")

agent = workflow.compile()

if __name__ == "__main__":
    print("🎯 Career Transition Advisor initialized successfully!")
    print(f"Available research tools: {[tool.name for tool in tools]}")
    print("Memory: Platform-managed persistence (thread-based)")
    print("\nDemo: Help professionals transition careers with personalized guidance")
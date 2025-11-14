"""LangGraph agent construction for Career Transition Advisor."""

import asyncio
from langgraph.graph import StateGraph, MessagesState, START
from langgraph.prebuilt import ToolNode, tools_condition

from .nodes import create_llm, create_call_model_node
from .tools import create_mcp_tools



# Initialize tools using asyncio.run() at module level
tools = asyncio.run(create_mcp_tools())

# Create LLM and bind tools
llm = create_llm()
llm_with_tools = llm.bind_tools(tools)



# Create the call_model node
call_model = create_call_model_node(llm_with_tools)

# Build the graph
workflow = StateGraph(MessagesState)

# Add nodes
workflow.add_node("agent", call_model)
workflow.add_node("tools", ToolNode(tools))

# Add edges
workflow.add_edge(START, "agent")

# Use built-in tools_condition for routing
workflow.add_conditional_edges("agent", tools_condition)
workflow.add_edge("tools", "agent")

# Compile graph - LangGraph CLI handles persistence when --postgres-uri is provided
agent = workflow.compile()


if __name__ == "__main__":
    print("Career Transition Advisor initialized successfully!")
    print(f"Available research tools: {[tool.name for tool in tools]}")
    print("Memory: Thread-based conversation history with PostgreSQL storage")
    print("\nDemo: Help professionals transition careers with personalized guidance")
    print("\nPostgreSQL tables auto-created: checkpoints, checkpoint_blobs, checkpoint_writes")

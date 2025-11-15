"""MCP tools initialization for web research capabilities."""

import os

from dotenv import load_dotenv
from langchain_mcp_adapters.client import MultiServerMCPClient

load_dotenv()


async def create_mcp_tools():
    """
    Initialize MCP client and retrieve Firecrawl tools.

    Available tools:
    - firecrawl_search: Web search (query + limit)
    - firecrawl_scrape: Extract content from URLs
    - firecrawl_map: Crawl website structure
    - firecrawl_crawl: Batch page crawling
    - firecrawl_check_crawl_status: Monitor crawl jobs
    - firecrawl_extract: Structured data extraction

    Returns:
        List of LangChain tools from Firecrawl MCP server
    """
    firecrawl_api_key = os.getenv("FIRECRAWL_API_KEY")
    if not firecrawl_api_key:
        raise ValueError("FIRECRAWL_API_KEY environment variable is required for Firecrawl MCP")

    mcp_client = MultiServerMCPClient({
        "firecrawl": {
            "transport": "stdio",
            "command": "npx",
            "args": ["-y", "firecrawl-mcp"],
            "env": {
                "FIRECRAWL_API_KEY": firecrawl_api_key
            }
        }
    })
    return await mcp_client.get_tools()

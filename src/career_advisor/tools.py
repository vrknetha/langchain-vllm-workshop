"""MCP tools initialization for web research capabilities."""

from langchain_mcp_adapters.client import MultiServerMCPClient


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
    mcp_client = MultiServerMCPClient({
        "firecrawl": {
            "transport": "stdio",
            "command": "npx",
            "args": ["-y", "firecrawl-mcp"]
        }
    })
    return await mcp_client.get_tools()

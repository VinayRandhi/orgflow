from fastmcp import FastMCP
from duckduckgo_search import DDGS
import asyncio

mcp = FastMCP("DuckDuckGo-Agent")

@mcp.tool(description="Answer questions with live DuckDuckGo Web search")
def web_search(query: str, max_results: int = 5) -> str:
    ddg = DDGS()                       # free, no key required
    hits = ddg.text(query, max_results=max_results)
    if not hits:
        return "No web results."
    return "\n\n".join(
        f"{i+1}. {hit['title']} – {hit['href']}\n{hit['body']}"
        for i, hit in enumerate(hits)
    )

async def main():
    await mcp.run_async(transport="streamable-http",host = "127.0.0.1", port = 8001, path="/mcp")

if __name__ == "__main__":
    asyncio.run(main())

# from mcp.server.fastmcp import FastMCP
# from my_rag_app import rag   # <- your existing RAG module
from rag_agent import RAGAgent
from fastmcp import FastMCP
import asyncio
import os
from dotenv import load_dotenv

rag = RAGAgent()
mcp = FastMCP("RAG-Agent")

@mcp.tool(description="Query the internal knowledge base with RAG")
def rag_search(query: str) -> str:           # <- will appear to the client as a tool
    return rag.query(query)

async def main():
    await mcp.run_async(transport="streamable-http",host = "127.0.0.1", port = 8000, path="/mcp")

if __name__ == "__main__":
    load_dotenv()

    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
    # default transport = streamable HTTP on http://127.0.0.1:8000/mcp
    # mcp.settings.host = "127.0.0.1"
    # mcp.settings.port = 8000
    # mcp.run(transport="streamable-http")
    # mcp.run(transport="http",host = "127.0.0.1", port = 8001, path="/mcp")
    asyncio.run(main())
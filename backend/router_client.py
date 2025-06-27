# import os
# import json
# import asyncio
# from openai import OpenAI
# from fastmcp import Client
# from fastmcp.client.transports import StreamableHttpTransport
# from dotenv import load_dotenv

# load_dotenv()

# # URLs for your MCP servers
# RAG_URL = os.getenv("RAG_URL", "http://127.0.0.1:8000/mcp")
# DDG_URL = os.getenv("DDG_URL", "http://127.0.0.1:8001/mcp")

# # Set up two MCP client transports
# rag_transport = StreamableHttpTransport(url=RAG_URL)
# ddg_transport = StreamableHttpTransport(url=DDG_URL)

# # Create two Client instances
# rag_client = Client(rag_transport)
# ddg_client = Client(ddg_transport)

# # OpenAI client
# openai = OpenAI(api_key=os.getenv("OPENAI_API_KEY", ""))

# tools = [
#     {
#         "type": "function",
#         "function": {
#             "name": "rag_search",
#             "description": "Query internal knowledge base with RAG.",
#             "parameters": {
#                 "type": "object",
#                 "properties": {"query": {"type": "string"}},
#                 "required": ["query"]
#             },
#         }
#     },
#     {
#         "type": "function",
#         "function": {
#             "name": "web_search",
#             "description": "Search with DuckDuckGo.",
#             "parameters": {
#                 "type": "object",
#                 "properties": {"query": {"type": "string"}, "max_results": {"type": "integer"}},
#                 "required": ["query"]
#             },
#         }
#     },
# ]

# SYSTEM_PROMPT = (
#     "You can call rag_search or web_search to answer user queries when needed."
# )


# def mcp_call(base_url: str, tool_name: str, args: dict) -> str:
#     """
#     Synchronously invoke a tool on an MCP server and return its text.
#     Opens a fresh session every call to avoid 'Session terminated'.
#     """
#     async def _once() -> str:
#         async with Client(StreamableHttpTransport(url=base_url)) as client:
#             resp = await client.call_tool(tool_name, arguments=args)
#             # resp.result holds the return value *exactly* as the tool sent it
#             # print('\n\n')
#             # print(resp)
#             # print('\n\n')
#             value = resp[0]
            
#             # FastMCP helper classes (TextContent, JsonContent…) stringify fine
#             return value.text if hasattr(value, "text") else str(value)

#     return asyncio.run(_once())

    
# def ask(user_query: str, model: str = "gpt-4o"):
#     """Return a dict with keys:
#         response (str) – final answer to user
#         agent_types (List[str]) – identifiers such as 'rag', 'web', 'llm'
#         agents_used (List[str]) – human-friendly agent names
#         agent_results (List[dict]) – raw results for trace/diagnostics
#     """

#     # Helper to format the final output consistently
#     def _final(reply: str, agent_types: list[str], agents_used: list[str], agent_results: list[dict]):
#         return {
#             "response": reply,
#             "agent_types": agent_types,
#             "agents_used": agents_used,
#             "agent_results": agent_results,
#         }

#     # No OpenAI key → direct RAG only
#     if not os.getenv("OPENAI_API_KEY"):
#         rag_answer = mcp_call(RAG_URL, "rag_search", {"query": user_query})
#         return _final(
#             rag_answer,
#             ["rag"],
#             ["RAG Agent"],
#             [{
#                 "agent_type": "rag",
#                 "agent_name": "RAG Agent",
#                 "result": {"success": True, "context": rag_answer},
#             }],
#         )

#     messages = [
#         {"role": "system", "content": SYSTEM_PROMPT},
#         {"role": "user", "content": user_query},
#     ]

#     try:
#         # 1. Let GPT decide whether to call a tool
#         resp = openai.chat.completions.create(
#             model=model,
#             messages=messages,
#             tools=tools,
#             tool_choice="auto",
#         )
#     except Exception:
#         # If OpenAI fails (auth/network/model), fall back to RAG search
#         rag_answer = mcp_call(RAG_URL, "rag_search", {"query": user_query})
#         return _final(
#             rag_answer,
#             ["rag"],
#             ["RAG Agent"],
#             [{
#                 "agent_type": "rag",
#                 "agent_name": "RAG Agent",
#                 "result": {"success": True, "context": rag_answer},
#             }],
#         )

#     assistant_msg = resp.choices[0].message

#     if assistant_msg.tool_calls:
#         # Add the assistant message **exactly as returned**
#         messages.append({"role": "assistant", "tool_calls": assistant_msg.tool_calls})

#         agent_types: list[str] = []
#         agents_used: list[str] = []
#         agent_results: list[dict] = []

#         # 2. Execute each tool and append its response
#         for call in assistant_msg.tool_calls:
#             fn = call.function
#             args = json.loads(fn.arguments or "{}")

#             if fn.name == "rag_search":
#                 base_url = RAG_URL
#                 agent_type = "rag"
#                 agent_name = "RAG Agent"
#             else:
#                 base_url = DDG_URL
#                 agent_type = "web"
#                 agent_name = "Web Search Agent"

#             result = mcp_call(base_url, fn.name, args)

#             agent_types.append(agent_type)
#             agents_used.append(agent_name)
#             agent_results.append({
#                 "agent_type": agent_type,
#                 "agent_name": agent_name,
#                 "result": {
#                     "success": True,
#                     "context": result,
#                 },
#             })

#             # Append tool response for LLM context
#             messages.append({
#                 "role": "tool",
#                 "name": fn.name,
#                 "tool_call_id": call.id,
#                 "content": result,
#             })

#         # 3. Final assistant answer—no more tools
#         final = openai.chat.completions.create(
#             model=model,
#             messages=messages,
#             # tool_choice="none",
#         ).choices[0].message

#         return _final(final.content, agent_types, agents_used, agent_results)

#     else:
#         # The model answered directly, no tools invoked
#         return _final(
#             assistant_msg.content,
#             ["llm"],
#             ["LLM"],
#             [{
#                 "agent_type": "llm",
#                 "agent_name": "LLM",
#                 "result": {"success": True, "context": assistant_msg.content},
#             }],
#         )


"""
hybrid_agent.py
================
Single‑file agent that combines an internal RAG tool with a DuckDuckGo
search‑and‑fetch tool pair (search, fetch_content).  The web tool definitions
and automatic fallback logic are adapted from `azure_ddg_agent.py`.

Run a DDG Fast‑MCP server on port 8001 and a RAG Fast‑MCP server on port 8000,
then call ask("your question") or run as a script:

    $ python hybrid_agent.py "Who won the last Ballon d'Or and why?"
"""

from __future__ import annotations

import os
import json
import asyncio
import re
from typing import List

from dotenv import load_dotenv
from openai import OpenAI
from fastmcp import Client
from fastmcp.client.transports import StreamableHttpTransport

load_dotenv()

# ---------------------------------------------------------------------------
# MCP endpoints
# ---------------------------------------------------------------------------
RAG_URL = os.getenv("RAG_URL", "http://127.0.0.1:8000/mcp")
DDG_URL = os.getenv("DDG_URL", "http://127.0.0.1:8001/mcp")

# ---------------------------------------------------------------------------
# Helper clients (each call opens a fresh session to avoid \"Session terminated\")
# ---------------------------------------------------------------------------

def _make_transport(url: str) -> StreamableHttpTransport:
    return StreamableHttpTransport(url=url)

# ---------------------------------------------------------------------------
# OpenAI client
# ---------------------------------------------------------------------------
openai = OpenAI(api_key=os.getenv("OPENAI_API_KEY", ""))

# ---------------------------------------------------------------------------
# Tool schemas (rag_search, search, fetch_content)
# ---------------------------------------------------------------------------
rag_tool_schema = {
    "type": "function",
    "function": {
        "name": "rag_search",
        "description": "Query the internal knowledge base using retrieval‑augmented generation (RAG).",
        "parameters": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "Natural‑language question for the knowledge base.",
                }
            },
            "required": ["query"],
        },
    },
}

search_tool_schema = {
    "type": "function",
    "function": {
        "name": "search",
        "description": "Perform a DuckDuckGo search and return a formatted list of results.",
        "parameters": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "Search query string to send to DuckDuckGo.",
                },
                "max_results": {
                    "type": "integer",
                    "description": "Maximum number of search results to return (1‑10).",
                    "default": 10,
                },
            },
            "required": ["query"],
        },
    },
}

fetch_tool_schema = {
    "type": "function",
    "function": {
        "name": "fetch_content",
        "description": "Fetch and return the plain‑text content of a given URL.",
        "parameters": {
            "type": "object",
            "properties": {
                "url": {
                    "type": "string",
                    "format": "uri",
                    "description": "The URL of the page to retrieve.",
                }
            },
            "required": ["url"],
        },
    },
}

tools = [rag_tool_schema, search_tool_schema, fetch_tool_schema]

SYSTEM_PROMPT = SYSTEM_PROMPT = (
    "You are an AI assistant. You have access to two tools:\n"
    "- `rag_search`: Use this for questions that may require internal or private knowledge (e.g. company policies, meeting notes, proprietary data).\n"
    "- `search` + `fetch_content`: `search` for DuckDuckGo and `fetch_content` for loading page text. "
                                    "When answering factual or timely questions, feel free to use these "
                                    "tools. If a URL fails to fetch, try another until you get useful "
                                    "content (max 5 attempts). Once you have sufficient information, "
                                    "present a concise, cited answer. Cite sources as [\u2713] after the "
                                    "sentence they support. Add date when the information is published."
    "Always use `rag_search` first when the user asks about internal documents or known proprietary information."
)


# ---------------------------------------------------------------------------
# Utility helpers
# ---------------------------------------------------------------------------
MAX_URL_RETRIES = 5


def extract_urls(text: str) -> List[str]:
    """Extract http/https URLs from the supplied text."""
    return re.findall(r"https?://[^\s]+", text)


def mcp_call(base_url: str, tool_name: str, args: dict) -> str:
    """
    Synchronously invoke a tool on an MCP server and return its string result.
    A new session is opened for each call to avoid 'Session terminated'.
    """

    async def _once() -> str:
        async with Client(_make_transport(base_url)) as client:
            resp = await client.call_tool(tool_name, arguments=args)
            # Fast‑MCP returns a list‑like ToolResult.  The first element is the payload.
            value = resp[0]
            return value.text if hasattr(value, "text") else str(value)

    return asyncio.run(_once())


# ---------------------------------------------------------------------------
# Core entry‑point
# ---------------------------------------------------------------------------

def ask(user_query: str, model: str = "gpt-4o") -> dict:
    """
    Execute a conversation with optional tool use and return a trace dictionary.

    Keys:
        response      – assistant's final answer (str)
        agent_types   – ['rag', 'web', 'llm', …]  in order of appearance
        agents_used   – human‑friendly agent names
        agent_results – raw tool results for diagnostics
    """

    def _final(reply: str, agent_types: list[str], agents_used: list[str], agent_results: list[dict]):
        return {
            "response": reply,
            "agent_types": agent_types,
            "agents_used": agents_used,
            "agent_results": agent_results,
        }

    # Fallback: if no OpenAI key, use direct RAG search
    if not os.getenv("OPENAI_API_KEY"):
        rag_answer = mcp_call(RAG_URL, "rag_search", {"query": user_query})
        return _final(
            rag_answer,
            ["rag"],
            ["RAG Agent"],
            [{
                "agent_type": "rag",
                "agent_name": "RAG Agent",
                "result": {"success": True, "context": rag_answer},
            }],
        )

    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": user_query},
    ]

    # State for automatic URL retry
    last_search_urls: List[str] = []
    attempted_urls: List[str] = []

    agent_types: list[str] = []
    agents_used: list[str] = []
    agent_results: list[dict] = []

    while True:
        # Let GPT decide next action
        try:
            resp = openai.chat.completions.create(
                model=model,
                messages=messages,
                tools=tools,
                tool_choice="auto",
            )
        except Exception as exc:  # Network/auth/model errors → pure RAG fallback
            rag_answer = mcp_call(RAG_URL, "rag_search", {"query": user_query})
            return _final(
                rag_answer,
                ["rag"],
                ["RAG Agent"],
                [{
                    "agent_type": "rag",
                    "agent_name": "RAG Agent",
                    "result": {"success": True, "context": rag_answer, "error": str(exc)},
                }],
            )

        assistant_msg = resp.choices[0].message

        # --------------------------------------------------
        # CASE 1 – GPT wants to call tool(s)
        # --------------------------------------------------
        if assistant_msg.tool_calls:
            # Record the assistant message verbatim so call IDs line up
            messages.append({"role": "assistant", "tool_calls": assistant_msg.tool_calls})

            for call in assistant_msg.tool_calls:
                fn = call.function
                args = json.loads(fn.arguments or "{}")

                # Route according to tool
                if fn.name == "rag_search":
                    base_url = RAG_URL
                    agent_type = "rag"
                    agent_name = "RAG Agent"
                else:  # search or fetch_content
                    base_url = DDG_URL
                    agent_type = "web"
                    agent_name = "Web Search Agent"

                result = mcp_call(base_url, fn.name, args)

                # Automatic retry logic for fetch_content
                if fn.name == "search":
                    last_search_urls = extract_urls(result)
                    attempted_urls = []  # Reset between search batches
                elif fn.name == "fetch_content":
                    attempted_urls.append(args.get("url"))
                    if (
                        ("Error:" in result or len(result) < 200) and
                        last_search_urls and
                        len(attempted_urls) < MAX_URL_RETRIES
                    ):
                        next_url = next((u for u in last_search_urls if u not in attempted_urls), None)
                        if next_url:
                            alt_result = mcp_call(
                                DDG_URL,
                                "fetch_content",
                                {"url": next_url},
                            )
                            attempted_urls.append(next_url)
                            result = alt_result  # Override with alt content

                # Track agents used for trace/debug
                agent_types.append(agent_type)
                agents_used.append(agent_name)
                agent_results.append({
                    "agent_type": agent_type,
                    "agent_name": agent_name,
                    "result": {"success": True, "context": result},
                })

                # Append tool response to conversation
                messages.append({
                    "role": "tool",
                    "name": fn.name,
                    "tool_call_id": call.id,
                    "content": result,
                })

            # Loop again so GPT can read tool outputs
            continue

        # --------------------------------------------------
        # CASE 2 – Normal assistant answer → done
        # --------------------------------------------------
        final_reply = assistant_msg.content or ""
        if not agent_types:  #  No tools ever used
            agent_types.append("llm")
            agents_used.append("LLM")
            agent_results.append({
                "agent_type": "llm",
                "agent_name": "LLM",
                "result": {"success": True, "context": final_reply},
            })

        return _final(final_reply, agent_types, agents_used, agent_results)


# ---------------------------------------------------------------------------
# CLI helper
# ---------------------------------------------------------------------------
# if __name__ == "__main__":
#     import argparse

#     parser = argparse.ArgumentParser(description="Mixed RAG + DuckDuckGo web‑enabled chat")
#     parser.add_argument("question", help="User question to answer.")
#     args = parser.parse_args()

#     answer_payload = ask(args.question)
#     print("\n========== FINAL ANSWER =========="\n)
#     print(answer_payload["response"])

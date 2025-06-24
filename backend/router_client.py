import os
import json
import asyncio
from openai import OpenAI
from fastmcp import Client
from fastmcp.client.transports import StreamableHttpTransport
from dotenv import load_dotenv

load_dotenv()

# URLs for your MCP servers
RAG_URL = os.getenv("RAG_URL", "http://127.0.0.1:8000/mcp")
DDG_URL = os.getenv("DDG_URL", "http://127.0.0.1:8001/mcp")

# Set up two MCP client transports
rag_transport = StreamableHttpTransport(url=RAG_URL)
ddg_transport = StreamableHttpTransport(url=DDG_URL)

# Create two Client instances
rag_client = Client(rag_transport)
ddg_client = Client(ddg_transport)

# OpenAI client
openai = OpenAI(api_key=os.getenv("OPENAI_API_KEY", ""))

tools = [
    {
        "type": "function",
        "function": {
            "name": "rag_search",
            "description": "Query internal knowledge base with RAG.",
            "parameters": {
                "type": "object",
                "properties": {"query": {"type": "string"}},
                "required": ["query"]
            },
        }
    },
    {
        "type": "function",
        "function": {
            "name": "web_search",
            "description": "Search with DuckDuckGo.",
            "parameters": {
                "type": "object",
                "properties": {"query": {"type": "string"}, "max_results": {"type": "integer"}},
                "required": ["query"]
            },
        }
    },
]

SYSTEM_PROMPT = (
    "You can call rag_search or web_search to answer user queries when needed."
)


def mcp_call(base_url: str, tool_name: str, args: dict) -> str:
    """
    Synchronously invoke a tool on an MCP server and return its text.
    Opens a fresh session every call to avoid 'Session terminated'.
    """
    async def _once() -> str:
        async with Client(StreamableHttpTransport(url=base_url)) as client:
            resp = await client.call_tool(tool_name, arguments=args)
            # resp.result holds the return value *exactly* as the tool sent it
            # print('\n\n')
            # print(resp)
            # print('\n\n')
            value = resp[0]
            
            # FastMCP helper classes (TextContent, JsonContent…) stringify fine
            return value.text if hasattr(value, "text") else str(value)

    return asyncio.run(_once())

    
def ask(user_query: str, model: str = "gpt-4o"):
    """Return a dict with keys:
        response (str) – final answer to user
        agent_types (List[str]) – identifiers such as 'rag', 'web', 'llm'
        agents_used (List[str]) – human-friendly agent names
        agent_results (List[dict]) – raw results for trace/diagnostics
    """

    # Helper to format the final output consistently
    def _final(reply: str, agent_types: list[str], agents_used: list[str], agent_results: list[dict]):
        return {
            "response": reply,
            "agent_types": agent_types,
            "agents_used": agents_used,
            "agent_results": agent_results,
        }

    # No OpenAI key → direct RAG only
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

    try:
        # 1. Let GPT decide whether to call a tool
        resp = openai.chat.completions.create(
            model=model,
            messages=messages,
            tools=tools,
            tool_choice="auto",
        )
    except Exception:
        # If OpenAI fails (auth/network/model), fall back to RAG search
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

    assistant_msg = resp.choices[0].message

    if assistant_msg.tool_calls:
        # Add the assistant message **exactly as returned**
        messages.append({"role": "assistant", "tool_calls": assistant_msg.tool_calls})

        agent_types: list[str] = []
        agents_used: list[str] = []
        agent_results: list[dict] = []

        # 2. Execute each tool and append its response
        for call in assistant_msg.tool_calls:
            fn = call.function
            args = json.loads(fn.arguments or "{}")

            if fn.name == "rag_search":
                base_url = RAG_URL
                agent_type = "rag"
                agent_name = "RAG Agent"
            else:
                base_url = DDG_URL
                agent_type = "web"
                agent_name = "Web Search Agent"

            result = mcp_call(base_url, fn.name, args)

            agent_types.append(agent_type)
            agents_used.append(agent_name)
            agent_results.append({
                "agent_type": agent_type,
                "agent_name": agent_name,
                "result": {
                    "success": True,
                    "context": result,
                },
            })

            # Append tool response for LLM context
            messages.append({
                "role": "tool",
                "name": fn.name,
                "tool_call_id": call.id,
                "content": result,
            })

        # 3. Final assistant answer—no more tools
        final = openai.chat.completions.create(
            model=model,
            messages=messages,
            # tool_choice="none",
        ).choices[0].message

        return _final(final.content, agent_types, agents_used, agent_results)

    else:
        # The model answered directly, no tools invoked
        return _final(
            assistant_msg.content,
            ["llm"],
            ["LLM"],
            [{
                "agent_type": "llm",
                "agent_name": "LLM",
                "result": {"success": True, "context": assistant_msg.content},
            }],
        )


if __name__ == "__main__":
    q = input("❓> ")
    print(ask(q))

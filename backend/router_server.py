from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from router_client import ask
import os
import asyncio

app = FastAPI(title="Router Client API")

class ChatRequest(BaseModel):
    message: str

class ChatResponse(BaseModel):
    success: bool = True
    response: str
    agents_used: list = []
    agent_types: list = []
    agent_results: list = []

@app.post("/api/chat", response_model=ChatResponse)
async def chat(req: ChatRequest):
    try:
        # Run blocking ask() in a separate thread to avoid nested event-loop issues
        loop = asyncio.get_running_loop()
        result = await loop.run_in_executor(None, ask, req.message)

        # Ensure minimal required keys exist
        response_text = result.get("response", "") if isinstance(result, dict) else str(result)
        agent_types = result.get("agent_types", []) if isinstance(result, dict) else []
        agents_used = result.get("agents_used", []) if isinstance(result, dict) else []
        agent_results = result.get("agent_results", []) if isinstance(result, dict) else []

        return ChatResponse(
            response=response_text,
            agent_types=agent_types,
            agents_used=agents_used,
            agent_results=agent_results,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Run with: python backend/router_server.py
if __name__ == "__main__":
    import uvicorn

    port = int(os.getenv("ROUTER_SERVER_PORT", "8002"))
    uvicorn.run("router_server:app", host="0.0.0.0", port=port, reload=True) 

# from __future__ import annotations
# """router_server_refactored.py
# ================================

# FastAPI wrapper that exposes the *router client* (internal RAG + web‑search
# agent) over an HTTP endpoint suitable for your front‑end chat UI.

# Why a refactor?
# ---------------
# * **Imports the new `answer()` API** from *router_client_refactored.py* but still
#   gracefully falls back to the legacy module name.  This makes hot‑swapping
#   implementations painless.
# * **Type hints throughout** – your editor/CI will catch mismatches early.
# * **Cleaner error surfacing** – maps internal exceptions to consistent 500
#   responses.
# * **No nested event‑loop issues** – the blocking `answer()` call is executed in
#   a thread pool via ``run_in_executor``.
# * **Fully self‑contained** – run with ``python router_server_refactored.py`` or
#   integrate in uvicorn/gunicorn as needed.
# """

# import asyncio
# import os
# from typing import Any, Dict, List

# from fastapi import FastAPI, HTTPException
# from pydantic import BaseModel, Field

# # ---------------------------------------------------------------------------
# # Try the new client first; fall back to legacy for compatibility.
# # ---------------------------------------------------------------------------
# try:
#     from router_client import answer  # type: ignore
# except ImportError:  # pragma: no cover – legacy fallback
#     from router_client import answer  # type: ignore

# # ---------------------------------------------------------------------------
# # FastAPI app and data‑models
# # ---------------------------------------------------------------------------
# app = FastAPI(title="Router Client API")


# class ChatRequest(BaseModel):
#     message: str = Field(..., description="User's chat message/question")


# class ChatResponse(BaseModel):
#     success: bool = True
#     response: str
#     agent_types: List[str] = []
#     agents_used: List[str] = []
#     agent_results: List[Dict[str, Any]] = []


# # ---------------------------------------------------------------------------
# # Endpoint
# # ---------------------------------------------------------------------------
# @app.post("/api/chat", response_model=ChatResponse)
# async def chat(req: ChatRequest) -> ChatResponse:  # noqa: D401
#     """Process a chat request through the tool‑enabled agent."""

#     loop = asyncio.get_running_loop()
#     try:
#         # Execute blocking *answer()* in a thread to keep event‑loop free.
#         result = await loop.run_in_executor(None, answer, req.message)

#         # *answer()* may return either a plain string or the rich diagnostics
#         # dict.  Normalise to our ChatResponse schema.
#         if isinstance(result, str):
#             return ChatResponse(response=result)

#         return ChatResponse(
#             response=result.get("response", ""),
#             agent_types=result.get("agent_types", []),
#             agents_used=result.get("agents_used", []),
#             agent_results=result.get("agent_results", []),
#         )

#     except Exception as exc:  # pragma: no cover – surface error cleanly
#         raise HTTPException(status_code=500, detail=str(exc)) from exc


# # ---------------------------------------------------------------------------
# # CLI convenience
# # ---------------------------------------------------------------------------
# if __name__ == "__main__":
#     import uvicorn

#     port = int(os.getenv("ROUTER_SERVER_PORT", "8002"))
#     uvicorn.run("router_server_refactored:app", host="0.0.0.0", port=port, reload=True)

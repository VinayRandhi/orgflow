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
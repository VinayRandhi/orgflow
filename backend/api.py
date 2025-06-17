from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, Any, Optional, List
from agent_manager import agent_manager

app = FastAPI(title="Agentic Chatbot API")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class QueryRequest(BaseModel):
    message: str

class AgentResult(BaseModel):
    agent_type: str
    agent_name: str
    result: Dict[str, Any]

class QueryResponse(BaseModel):
    success: bool
    response: str
    agents_used: List[str]
    agent_types: List[str]
    agent_results: List[AgentResult]
    timestamp: str

class StatusResponse(BaseModel):
    rag_documents: int
    openai_connected: bool
    max_search_results: int
    similarity_threshold: float

@app.post("/api/chat", response_model=QueryResponse)
async def process_query(request: QueryRequest) -> Dict[str, Any]:
    """Process a chat query through the orchestrator agent"""
    try:
        result = await agent_manager.process_query(request.message)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/status", response_model=StatusResponse)
async def get_status() -> Dict[str, Any]:
    """Get the current status of the agents"""
    try:
        return agent_manager.get_agent_status()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 
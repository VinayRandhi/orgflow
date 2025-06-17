import os
from dotenv import load_dotenv
from typing import Dict, Any, List
from orchestrator_agent import Config, OrchestratorAgent, RAGAgent, WebSearchAgent
from datetime import datetime
from lightrag.llm.openai import gpt_4o_complete

class AgentManager:
    _instance = None
    _initialized = False

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(AgentManager, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        if not self._initialized:
            load_dotenv()
            
            # Initialize configuration
            self.config = Config(
                openai_api_key=os.getenv("OPENAI_API_KEY", ""),
                max_search_results=int(os.getenv("MAX_SEARCH_RESULTS", "5")),
                similarity_threshold=float(os.getenv("SIMILARITY_THRESHOLD", "0.7"))
            )
            
            # Initialize agents
            self.rag_agent = RAGAgent(llm_model_func=gpt_4o_complete)
            self.web_agent = WebSearchAgent(self.config)
            self.orchestrator = OrchestratorAgent(
                self.config,
                self.rag_agent,
                self.web_agent
            )
            
            self._initialized = True

    async def process_query(self, query: str) -> Dict[str, Any]:
        """Process a query through the orchestrator agent"""
        try:
            result = await self.orchestrator.process(query)
            
            # Ensure the response matches the expected structure
            return {
                "success": result["success"],
                "response": result["response"],
                "agents_used": result["agents_used"],
                "agent_types": result["agent_types"],
                "agent_results": result["agent_results"],
                "timestamp": result["timestamp"]
            }
        except Exception as e:
            return {
                "success": False,
                "response": f"Error processing query: {str(e)}",
                "agents_used": [],
                "agent_types": [],
                "agent_results": [],
                "timestamp": datetime.now().isoformat()
            }

    def get_agent_status(self) -> Dict[str, Any]:
        """Get the current status of the agents"""
        return {
            "rag_documents": len(self.rag_agent.rag.knowledge_base) if hasattr(self.rag_agent.rag, 'knowledge_base') else 0,
            "openai_connected": bool(self.config.openai_api_key),
            "max_search_results": self.config.max_search_results,
            "similarity_threshold": self.config.similarity_threshold
        }

# Create a singleton instance
agent_manager = AgentManager() 
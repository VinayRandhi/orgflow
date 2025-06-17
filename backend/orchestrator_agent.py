import os
from dotenv import load_dotenv
from openai import AzureOpenAI, OpenAI
from typing import Dict, Any, List
from datetime import datetime
import logging
from dataclasses import dataclass
import asyncio
# import openai

# Configuration
@dataclass
class Config:
    openai_api_key: str = os.getenv("OPENAI_API_KEY", "")
    embedding_model: str = os.getenv("EMBEDDING_MODEL", "all-MiniLM-L6-v2")
    max_search_results: int = int(os.getenv("MAX_SEARCH_RESULTS", "5"))
    similarity_threshold: float = float(os.getenv("SIMILARITY_THRESHOLD", "0.7"))
    model_name: str = os.getenv("MODEL_NAME", "gpt-4o")

# # Dummy RAG Agent for testing
# class RAGAgent:
#     def __init__(self, config: Config):
#         self.config = config
#         self.knowledge_base = ["dummy document 1", "dummy document 2"]  # Dummy knowledge base
    
#     def process(self, query: str) -> Dict[str, Any]:
#         return {
#             "success": True,
#             "context": "This is a dummy response from the RAG agent. The query was: " + query,
#             "message": "Successfully retrieved information from knowledge base"
#         }

import os
import asyncio
from lightrag import LightRAG, QueryParam
from lightrag.llm.openai import gpt_4o_mini_complete, gpt_4o_complete, openai_embed
from lightrag.kg.shared_storage import initialize_pipeline_status
from lightrag.utils import setup_logger

class RAGAgent:
    def __init__(self, embedding_func: callable = openai_embed, llm_model_func: callable = gpt_4o_mini_complete, working_dir= "./rag_storage"):
        setup_logger("lightrag", level="INFO")
        self.working_dir = working_dir
        self.embedding_func = embedding_func
        self.llm_model_func = llm_model_func
        self.rag = None
        
        # Create working directory if it doesn't exist
        if not os.path.exists(working_dir):
            os.makedirs(working_dir, exist_ok=True)
            logging.info(f"Created RAG working directory at {working_dir}")

    async def initialize(self):
        """Initialize the RAG system asynchronously"""
        if self.rag is not None:
            return  # Already initialized
            
        try:
            self.rag = LightRAG(
                working_dir=self.working_dir,
                embedding_func=self.embedding_func,
                llm_model_func=self.llm_model_func,
            )
            
            # Initialize storage and pipeline status
            await self.rag.initialize_storages()
            await initialize_pipeline_status()
            logging.info("RAG system initialized successfully")
        except Exception as e:
            logging.error(f"Failed to initialize RAG system: {str(e)}")
            raise

    async def query(self, query: str, mode: str = "hybrid"):
        """Query the RAG system asynchronously"""
        try:
            # Ensure RAG is initialized
            if self.rag is None:
                await self.initialize()
                
            result = await self.rag.aquery(query, param=QueryParam(mode=mode))
            
            return {
                "success": True,
                "context": result,
                "message": "Successfully retrieved information from knowledge base"
            }
        except Exception as e:
            logging.error(f"Error querying knowledge base: {str(e)}")
            return {
                "success": False,
                "context": "",
                "message": f"Error querying knowledge base: {str(e)}"
            }



# Dummy Web Search Agent for testing
class WebSearchAgent:
    def __init__(self, config: Config):
        self.config = config
    
    def process(self, query: str) -> Dict[str, Any]:
        return {
            "success": True,
            "results": [
                {
                    "title": "Dummy Web Result 1",
                    "snippet": "This is a dummy web search result for: " + query,
                    "url": "https://example.com/dummy1"
                },
                {
                    "title": "Dummy Web Result 2",
                    "snippet": "Another dummy web search result for: " + query,
                    "url": "https://example.com/dummy2"
                }
            ],
            "message": "Successfully retrieved web search results"
        }

class OrchestratorAgent:
    """Orchestrator Agent using OpenAI for routing decisions"""
    
    def __init__(self, config: Config, rag_agent: 'RAGAgent', web_agent: 'WebSearchAgent'):
        self.config = config
        self.rag_agent = rag_agent
        self.web_agent = web_agent
        
        # Initialize OpenAI client only if API key is available
        if self.config.openai_api_key:
            self.llm_client = OpenAI(
                # api_version=os.getenv("AZURE_OPENAI_API_VERSION", "2024-02-15-preview"),
                # azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT", ""),
                api_key=self.config.openai_api_key
            )
        else:
            self.llm_client = None
            logging.warning("OpenAI API key not found. Running in fallback mode.")
    
    def _classify_query(self, query: str) -> List[str]:
        """Classify query to determine which agents to use"""
        if not self.llm_client:
            # Fallback classification without OpenAI
            org_keywords = ["company", "organization", "policy", "procedure", "benefit", "employee", "hr", "faq", "guideline"]
            web_keywords = ["news", "current", "latest", "today", "weather", "stock", "price", "recent"]
            
            query_lower = query.lower()
            selected_agents = []
            
            # Check for organization-related queries
            if any(keyword in query_lower for keyword in org_keywords):
                selected_agents.append("rag")
            
            # Check for current events queries
            if any(keyword in query_lower for keyword in web_keywords):
                selected_agents.append("web")
            
            # If no agents selected, default to RAG
            if not selected_agents:
                selected_agents.append("rag")
            
            return selected_agents
        
        try:
            prompt = f"""
            You are an intelligent query router for an organization's chatbot system. Your task is to determine which service(s) should handle the user's query.

            Available Services:
            1. RAG Agent (Organization Knowledge Base):
               - Handles questions about company policies, procedures, and guidelines
               - Provides information about employee benefits, HR policies, and organizational structure
               - Answers FAQs about the organization
               - Offers internal knowledge and documentation
               - Best for questions about how things work within the organization

            2. Web Search Agent:
               - Provides real-time information and current events
               - Handles questions about weather, news, and market updates
               - Offers external information and public data
               - Best for questions about the world outside the organization

            User Query: "{query}"

            Based on the query, determine which service(s) should handle it. A query might need multiple services if it combines internal and external information needs.

            Respond with a comma-separated list of service names (e.g., "rag", "web", or "rag,web").
            """
            
            logging.info("Triggering LLM for query classification.")
            response = self.llm_client.chat.completions.create(
                model=self.config.model_name,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=10,
                temperature=0
            )
            print(response)

            classification = response.choices[0].message.content.strip().lower()
            selected_agents = [agent.strip() for agent in classification.split(",")]

            logging.info(f"Query: {query} -> Selected agents: {selected_agents}")
            
            # Validate and filter agents
            valid_agents = [agent for agent in selected_agents if agent in ["rag", "web"]]
            return valid_agents if valid_agents else ["rag"]  # Default to RAG if no valid agents
        
        except Exception as e:
            logging.warning(f"OpenAI classification failed: {str(e)}. Using fallback classification.")
            return ["rag"]  # Default to RAG on error
    
    async def _process_with_agent(self, query: str, agent_type: str) -> Dict[str, Any]:
        """Process query with a specific agent"""
        try:
            if agent_type == "rag":
                result = await self.rag_agent.query(query, mode="naive")
                return {
                    "agent_type": "rag",
                    "agent_name": "RAG Agent",
                    "result": result
                }
            else:  # web
                result = self.web_agent.process(query)
                return {
                    "agent_type": "web",
                    "agent_name": "Web Search Agent",
                    "result": result
                }
        except Exception as e:
            logging.error(f"Error processing with {agent_type} agent: {str(e)}")
            return {
                "agent_type": agent_type,
                "agent_name": f"{agent_type.title()} Agent",
                "result": {
                    "success": False,
                    "context": "",
                    "message": f"Error: {str(e)}"
                }
            }
    
    def _generate_response(self, query: str, agent_results: List[Dict[str, Any]]) -> str:
        """Generate final response using OpenAI"""
        # If only RAG agent was used and it was successful, return its response directly
        if len(agent_results) == 1 and agent_results[0]["agent_type"] == "rag" and agent_results[0]["result"].get("success"):
            return agent_results[0]["result"].get("context", "")
            
        if not self.llm_client:
            # Fallback response generation
            responses = []
            for result in agent_results:
                if result["agent_type"] == "rag" and result["result"].get("success"):
                    responses.append(f"From our organization knowledge base:\n{result['result'].get('context', '')}")
                elif result["agent_type"] == "web" and result["result"].get("success"):
                    web_results = result["result"].get("results", [])
                    web_response = f"From web search:\n"
                    for i, res in enumerate(web_results, 1):
                        web_response += f"{i}. {res['title']}\n{res['snippet']}\n"
                    responses.append(web_response)
            
            if responses:
                return "\n\n".join(responses)
            return f"I couldn't find relevant information for: {query}"
        
        try:
            # Prepare context from all agent results
            context_parts = []
            for result in agent_results:
                if result["agent_type"] == "rag" and result["result"].get("success"):
                    context_parts.append(f"Organization Knowledge Base:\n{result['result'].get('context', '')}")
                elif result["agent_type"] == "web" and result["result"].get("success"):
                    results = result["result"].get("results", [])
                    web_context = "\n".join([f"Title: {r['title']}\nContent: {r['snippet']}" for r in results])
                    context_parts.append(f"Web Search Results:\n{web_context}")
            
            if not context_parts:
                return f"I couldn't find relevant information for your query: {query}"
            
            context = "\n\n".join(context_parts)
            prompt = f"""
            Based on the following information from multiple sources, please provide a comprehensive answer to the user's question.
            If the information from different sources conflicts, prioritize the organization's knowledge base.
            
            Information Sources:
            {context}
            
            Question: {query}
            
            Please provide a clear, well-structured answer that combines relevant information from all available sources.
            """
            
            logging.info("Triggering LLM for response generation.")
            response = self.llm_client.chat.completions.create(
                model=self.config.model_name,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=500,
                temperature=0.7
            )
            
            return response.choices[0].message.content.strip()
        
        except Exception as e:
            logging.warning(f"OpenAI response generation failed: {str(e)}. Using fallback response.")
            return f"I encountered an error while processing your query: {query}"
    
    async def process(self, query: str) -> Dict[str, Any]:
        """Process user query through the orchestrator"""
        try:
            # Step 1: Classify the query
            agent_types = self._classify_query(query)
            
            # Step 2: Process with all selected agents in parallel
            agent_tasks = [self._process_with_agent(query, agent_type) for agent_type in agent_types]
            agent_results = await asyncio.gather(*agent_tasks)
            
            # Step 3: Generate final response
            final_response = self._generate_response(query, agent_results)
            
            return {
                "success": True,
                "response": final_response,
                "agents_used": [result["agent_name"] for result in agent_results],
                "agent_types": agent_types,
                "agent_results": agent_results,
                "timestamp": datetime.now().isoformat()
            }
        
        except Exception as e:
            logging.error(f"Error processing query: {str(e)}")
            return {
                "success": False,
                "response": f"Error processing query: {str(e)}",
                "agents_used": [],
                "agent_types": [],
                "agent_results": [],
                "timestamp": datetime.now().isoformat()
            }
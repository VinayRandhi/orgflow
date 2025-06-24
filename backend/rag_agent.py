import logging
from dataclasses import dataclass
import os
import asyncio
from lightrag import LightRAG, QueryParam
from lightrag.llm.openai import gpt_4o_mini_complete, gpt_4o_complete, openai_embed
from lightrag.kg.shared_storage import initialize_pipeline_status
from lightrag.utils import setup_logger


# # Configuration
# @dataclass
# class Config:
#     openai_api_key: str = os.getenv("OPENAI_API_KEY", "")
#     embedding_model: str = os.getenv("EMBEDDING_MODEL", "all-MiniLM-L6-v2")
#     max_search_results: int = int(os.getenv("MAX_SEARCH_RESULTS", "5"))
#     similarity_threshold: float = float(os.getenv("SIMILARITY_THRESHOLD", "0.7"))
#     model_name: str = os.getenv("MODEL_NAME", "gpt-4o")


class RAGAgent:
    def __init__(self, embedding_func: callable = openai_embed, llm_model_func: callable = gpt_4o_complete, working_dir= "./rag_storage"):
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
        

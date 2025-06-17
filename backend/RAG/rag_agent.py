import os
import asyncio
from lightrag import LightRAG, QueryParam
from lightrag.utils import EmbeddingFunc
import numpy as np
from dotenv import load_dotenv
import logging
from openai import AzureOpenAI
from lightrag.kg.shared_storage import initialize_pipeline_status
from pdf_parser.pdf_parser_rag import PDFParserRAG
from typing import Dict, Any, Optional

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

load_dotenv()

class RAGAgent:
    """RAG Agent for handling knowledge base queries"""
    
    def __init__(self):
        self.azure_openai_api_version = os.getenv("AZURE_OPENAI_API_VERSION")
        self.azure_openai_deployment = os.getenv("AZURE_OPENAI_DEPLOYMENT")
        self.azure_openai_api_key = os.getenv("AZURE_OPENAI_API_KEY")
        self.azure_openai_endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
        self.embedding_model = os.getenv("EMBEDDING_MODEL")
        self.azure_embedding_deployment = os.getenv("AZURE_EMBEDDING_DEPLOYMENT")
        self.azure_embedding_api_version = os.getenv("AZURE_EMBEDDING_API_VERSION")
        self.working_dir = "./temp_test"
        self.rag = None
        self.embedding_dimension = 1536
        
        # Create working directory if it doesn't exist
        if not os.path.exists(self.working_dir):
            os.makedirs(self.working_dir)
    
    async def initialize(self) -> None:
        """Initialize the RAG agent with necessary components"""
        try:
            self.rag = LightRAG(
                working_dir=self.working_dir,
                llm_model_func=self._llm_model_func,
                embedding_func=EmbeddingFunc(
                    embedding_dim=self.embedding_dimension,
                    max_token_size=8192,
                    func=self._embedding_func,
                ),
            )
            
            await self.rag.initialize_storages()
            await initialize_pipeline_status()
            logger.info("RAG agent initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize RAG agent: {str(e)}")
            raise
    
    async def _llm_model_func(
        self, 
        prompt: str, 
        system_prompt: Optional[str] = None, 
        history_messages: list = [], 
        **kwargs
    ) -> str:
        """Internal LLM model function for text generation"""
        client = AzureOpenAI(
            api_key=self.azure_openai_api_key,
            api_version=self.azure_openai_api_version,
            azure_endpoint=self.azure_openai_endpoint,
        )

        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        if history_messages:
            messages.extend(history_messages)
        messages.append({"role": "user", "content": prompt})

        chat_completion = client.chat.completions.create(
            model=self.azure_openai_deployment,
            messages=messages,
            temperature=kwargs.get("temperature", 0),
            top_p=kwargs.get("top_p", 1),
            n=kwargs.get("n", 1),
        )
        return chat_completion.choices[0].message.content

    async def _embedding_func(self, texts: list[str]) -> np.ndarray:
        """Internal embedding function for text vectorization"""
        client = AzureOpenAI(
            api_key=self.azure_openai_api_key,
            api_version=self.azure_embedding_api_version,
            azure_endpoint=self.azure_openai_endpoint,
        )
        embedding = client.embeddings.create(
            model=self.azure_embedding_deployment, 
            input=texts
        )

        embeddings = [item.embedding for item in embedding.data]
        return np.array(embeddings)
    
    async def process_document(self, file_path: str) -> Dict[str, Any]:
        """Process a document and add it to the knowledge base"""
        try:
            pdf_parser = PDFParserRAG(openai_api_key=self.azure_openai_api_key)
            pdf_list = await pdf_parser.process_pdf(file_path)
            
            pdf_text = ' '.join(chunk.text for chunk in pdf_list)
            self.rag.insert(pdf_text)
            
            return {
                "success": True,
                "message": f"Successfully processed document: {file_path}",
                "chunks_processed": len(pdf_list)
            }
            
        except Exception as e:
            logger.error(f"Failed to process document {file_path}: {str(e)}")
            return {
                "success": False,
                "message": f"Failed to process document: {str(e)}",
                "chunks_processed": 0
            }
    
    async def query(self, query_text: str, mode: str = "hybrid") -> Dict[str, Any]:
        """Query the knowledge base with the given text"""
        try:
            if not self.rag:
                raise ValueError("RAG agent not initialized")
            
            result = self.rag.query(
                query_text, 
                param=QueryParam(mode=mode)
            )
            
            return {
                "success": True,
                "response": result,
                "mode": mode
            }
            
        except Exception as e:
            logger.error(f"Failed to process query: {str(e)}")
            return {
                "success": False,
                "response": f"Error processing query: {str(e)}",
                "mode": mode
            }
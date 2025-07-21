import os
from typing import List, Dict, Optional
from pathlib import Path
import logging

from llama_index.core import (
    VectorStoreIndex, 
    SimpleDirectoryReader, 
    StorageContext,
    load_index_from_storage
)
from llama_index.vector_stores.chroma import ChromaVectorStore
from llama_index.embeddings.openai import OpenAIEmbedding
from llama_index.core.node_parser import SentenceSplitter
from llama_index.llms.openai import OpenAI
import chromadb

class LlamaIndexRAGService:
    """
    True vector embeddings RAG service using LlamaIndex and ChromaDB.
    This provides semantic search capabilities with proper vector embeddings.
    """
    
    def __init__(self, knowledge_base_path: str = "app/knowledge_base"):
        self.knowledge_base_path = Path(knowledge_base_path)
        self.index = None
        self.query_engine = None
        self.chroma_client = None
        self.vector_store = None
        
        # Initialize components
        self._initialize_components()
        self._load_knowledge_base()
    
    def _initialize_components(self):
        """Initialize LlamaIndex components"""
        try:
            # Initialize OpenAI embedding model
            embedding_model = OpenAIEmbedding(
                model="text-embedding-ada-002",
                api_key=os.getenv("OPENAI_API_KEY")
            )
            
            # Initialize LLM
            llm = OpenAI(
                model="gpt-4",
                api_key=os.getenv("OPENAI_API_KEY"),
                temperature=0.1
            )
            
            # Initialize ChromaDB
            self.chroma_client = chromadb.PersistentClient(
                path="./chroma_db_llama",
                settings=chromadb.config.Settings(anonymized_telemetry=False)
            )
            
            # Create or get collection
            chroma_collection = self.chroma_client.get_or_create_collection(
                name="resume_knowledge_llama",
                metadata={"description": "Resume writing knowledge base with LlamaIndex"}
            )
            
            # Create vector store
            self.vector_store = ChromaVectorStore(chroma_collection=chroma_collection)
            
            # Create storage context
            storage_context = StorageContext.from_defaults(vector_store=self.vector_store)
            
            # Try to load existing index
            try:
                self.index = load_index_from_storage(
                    storage_context=storage_context
                )
                print("✅ Loaded existing LlamaIndex from storage")
            except:
                # Create new index if none exists
                self.index = VectorStoreIndex.from_vector_store(
                    vector_store=self.vector_store,
                    storage_context=storage_context
                )
                print("✅ Created new LlamaIndex")
            
            # Create query engine
            self.query_engine = self.index.as_query_engine(
                similarity_top_k=5,
                response_mode="compact"
            )
            
            print("✅ LlamaIndex RAG service initialized successfully")
            
        except Exception as e:
            print(f"⚠️  Failed to initialize LlamaIndex components: {e}")
            self.index = None
            self.query_engine = None
    
    def _load_knowledge_base(self):
        """Load and index knowledge base files using LlamaIndex"""
        if not self.index:
            print("⚠️  Skipping knowledge base loading - index not initialized")
            return
        
        try:
            # Check if index already has data
            if hasattr(self.index, 'docstore') and self.index.docstore.docs:
                print(f"✅ Knowledge base already loaded ({len(self.index.docstore.docs)} documents)")
                return
            
            # Load knowledge base files using SimpleDirectoryReader
            documents = SimpleDirectoryReader(
                input_dir=str(self.knowledge_base_path),
                filename_as_id=True,
                recursive=False
            ).load_data()
            
            if documents:
                # Create index from documents
                self.index = VectorStoreIndex.from_documents(
                    documents=documents,
                    vector_store=self.vector_store,
                    storage_context=self.index.storage_context
                )
                
                # Persist the index
                self.index.storage_context.persist()
                
                print(f"✅ Loaded {len(documents)} knowledge documents into LlamaIndex")
            else:
                print("⚠️  No documents found to load")
                
        except Exception as e:
            print(f"⚠️  Failed to load knowledge base: {e}")
    
    def query(self, query_text: str, n_results: int = 5) -> List[Dict]:
        """
        Query the knowledge base using LlamaIndex semantic search
        
        Args:
            query_text: The query text
            n_results: Number of results to return
            
        Returns:
            List of relevant documents with metadata
        """
        if not self.query_engine:
            print("⚠️  Query engine not initialized, returning empty results")
            return []
        
        try:
            # Use LlamaIndex query engine for semantic search
            response = self.query_engine.query(query_text)
            
            # Extract source nodes from response
            formatted_results = []
            if hasattr(response, 'source_nodes') and response.source_nodes:
                for node in response.source_nodes[:n_results]:
                    formatted_results.append({
                        'content': node.text,
                        'metadata': {
                            'source': node.metadata.get('file_name', 'unknown'),
                            'type': 'knowledge_base'
                        },
                        'score': node.score if hasattr(node, 'score') else 0
                    })
            
            return formatted_results
            
        except Exception as e:
            print(f"⚠️  Query failed: {e}")
            return []
    
    def get_template_guidelines(self, template_id: int) -> str:
        """Get guidelines for a specific template using semantic search"""
        query = f"template {template_id} guidelines style formatting rules"
        results = self.query(query, n_results=3)
        
        if results:
            return "\n\n".join([r['content'] for r in results])
        else:
            # Fallback to basic guidelines
            return f"Use professional tone and clear structure for {template_id} template"
    
    def get_industry_guidelines(self, industry: str) -> str:
        """Get guidelines for a specific industry using semantic search"""
        query = f"{industry} industry resume guidelines keywords jargon terminology"
        results = self.query(query, n_results=3)
        
        if results:
            return "\n\n".join([r['content'] for r in results])
        else:
            return f"Use industry-specific terminology and focus on relevant achievements for {industry}"
    
    def get_best_practices(self, section: str) -> str:
        """Get best practices for a specific resume section using semantic search"""
        query = f"{section} resume best practices tips guidelines examples"
        results = self.query(query, n_results=3)
        
        if results:
            return "\n\n".join([r['content'] for r in results])
        else:
            # Fallback practices
            practices = {
                "work": "Use strong action verbs, quantify achievements, focus on results",
                "education": "Include degree, institution, graduation date, relevant coursework",
                "skills": "Group by category, include proficiency levels, focus on relevant skills",
                "projects": "Describe impact, use metrics, highlight technical skills"
            }
            return practices.get(section, "Use clear, professional language and focus on achievements")
    
    def get_action_verbs(self, industry: str = "general") -> str:
        """Get relevant action verbs using semantic search"""
        query = f"{industry} action verbs resume writing strong verbs"
        results = self.query(query, n_results=2)
        
        if results:
            return "\n\n".join([r['content'] for r in results])
        else:
            # Fallback verbs
            return "Managed, Led, Developed, Implemented, Created, Designed, Analyzed, Optimized, Increased, Improved"
    
    def health_check(self) -> Dict:
        """Check the health of the LlamaIndex RAG system"""
        status = {
            "index_initialized": self.index is not None,
            "query_engine_ready": self.query_engine is not None,
            "vector_store_ready": self.vector_store is not None,
            "documents_loaded": 0,
            "status": "healthy"
        }
        
        if self.index and hasattr(self.index, 'docstore'):
            try:
                status["documents_loaded"] = len(self.index.docstore.docs)
            except:
                status["documents_loaded"] = 0
        
        if not all([status["index_initialized"], status["query_engine_ready"]]):
            status["status"] = "unhealthy"
        
        return status
    
    def test_query(self, query_text: str = "resume best practices") -> Dict:
        """Test the RAG system with a sample query"""
        try:
            results = self.query(query_text, n_results=3)
            return {
                "query": query_text,
                "results_count": len(results),
                "results": results,
                "status": "success"
            }
        except Exception as e:
            return {
                "query": query_text,
                "error": str(e),
                "status": "failed"
            } 
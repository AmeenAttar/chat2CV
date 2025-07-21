import os
import json
from typing import List, Dict, Optional
from pathlib import Path
import chromadb
from chromadb.config import Settings
from sentence_transformers import SentenceTransformer
import numpy as np

class SimpleRAGService:
    """
    Simple RAG service using sentence transformers and ChromaDB.
    This provides the core functionality needed for Epic 5 without complex dependencies.
    """
    
    def __init__(self, knowledge_base_path: str = "app/knowledge_base"):
        self.knowledge_base_path = Path(knowledge_base_path)
        self.embedding_model = None
        self.chroma_client = None
        self.collection = None
        
        # Initialize components
        self._initialize_embedding_model()
        self._initialize_vector_store()
        self._load_knowledge_base()
    
    def _initialize_embedding_model(self):
        """Initialize the sentence transformer model for embeddings"""
        try:
            # Use a lightweight model for faster processing
            self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
            print("✅ Embedding model initialized successfully")
        except Exception as e:
            print(f"⚠️  Failed to initialize embedding model: {e}")
            self.embedding_model = None
    
    def _initialize_vector_store(self):
        """Initialize ChromaDB client and collection"""
        try:
            # Create a persistent ChromaDB client
            self.chroma_client = chromadb.PersistentClient(
                path="./chroma_db",
                settings=Settings(anonymized_telemetry=False)
            )
            
            # Create or get the collection
            self.collection = self.chroma_client.get_or_create_collection(
                name="resume_knowledge",
                metadata={"description": "Resume writing knowledge base"}
            )
            print("✅ Vector store initialized successfully")
        except Exception as e:
            print(f"⚠️  Failed to initialize vector store: {e}")
            self.chroma_client = None
            self.collection = None
    
    def _load_knowledge_base(self):
        """Load and index knowledge base files"""
        if not self.embedding_model or not self.collection:
            print("⚠️  Skipping knowledge base loading - components not initialized")
            return
        
        try:
            # Check if collection already has data
            if self.collection.count() > 0:
                print(f"✅ Knowledge base already loaded ({self.collection.count()} documents)")
                return
            
            # Load knowledge base files
            knowledge_files = [
                "best_practices.md",
                "industry_guidelines.md", 
                "resume_best_practices.md",
                "template_guidelines.md"
            ]
            
            documents = []
            metadatas = []
            ids = []
            
            for filename in knowledge_files:
                file_path = self.knowledge_base_path / filename
                if file_path.exists():
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    # Split content into chunks (simple approach)
                    chunks = self._split_text(content, chunk_size=500, overlap=50)
                    
                    for i, chunk in enumerate(chunks):
                        if chunk.strip():  # Only add non-empty chunks
                            documents.append(chunk)
                            metadatas.append({
                                "source": filename,
                                "chunk_id": i,
                                "type": "knowledge_base"
                            })
                            ids.append(f"{filename}_{i}")
            
            if documents:
                # Generate embeddings
                embeddings = self.embedding_model.encode(documents)
                
                # Add to collection
                self.collection.add(
                    documents=documents,
                    embeddings=embeddings.tolist(),
                    metadatas=metadatas,
                    ids=ids
                )
                
                print(f"✅ Loaded {len(documents)} knowledge chunks into vector store")
            else:
                print("⚠️  No documents found to load")
                
        except Exception as e:
            print(f"⚠️  Failed to load knowledge base: {e}")
    
    def _split_text(self, text: str, chunk_size: int = 500, overlap: int = 50) -> List[str]:
        """Split text into overlapping chunks"""
        if len(text) <= chunk_size:
            return [text]
        
        chunks = []
        start = 0
        
        while start < len(text):
            end = start + chunk_size
            
            # Try to break at sentence boundaries
            if end < len(text):
                # Look for sentence endings
                for i in range(end, max(start, end - 100), -1):
                    if text[i] in '.!?':
                        end = i + 1
                        break
            
            chunk = text[start:end].strip()
            if chunk:
                chunks.append(chunk)
            
            start = end - overlap
            if start >= len(text):
                break
        
        return chunks
    
    def query(self, query_text: str, n_results: int = 5) -> List[Dict]:
        """
        Query the knowledge base for relevant information
        
        Args:
            query_text: The query text
            n_results: Number of results to return
            
        Returns:
            List of relevant documents with metadata
        """
        if not self.embedding_model or not self.collection:
            print("⚠️  RAG components not initialized, returning empty results")
            return []
        
        try:
            # Generate query embedding
            query_embedding = self.embedding_model.encode([query_text])
            
            # Search in collection
            results = self.collection.query(
                query_embeddings=query_embedding.tolist(),
                n_results=n_results
            )
            
            # Format results
            formatted_results = []
            if results['documents'] and results['documents'][0]:
                for i, doc in enumerate(results['documents'][0]):
                    formatted_results.append({
                        'content': doc,
                        'metadata': results['metadatas'][0][i] if results['metadatas'] and results['metadatas'][0] else {},
                        'distance': results['distances'][0][i] if results['distances'] and results['distances'][0] else 0
                    })
            
            return formatted_results
            
        except Exception as e:
            print(f"⚠️  Query failed: {e}")
            return []
    
    def get_template_guidelines(self, template_id: int) -> str:
        """Get guidelines for a specific template"""
        query = f"template {template_id} guidelines style formatting"
        results = self.query(query, n_results=3)
        
        if results:
            return "\n\n".join([r['content'] for r in results])
        else:
            # Fallback to basic guidelines
            return f"Use professional tone and clear structure for {template_id} template"
    
    def get_industry_guidelines(self, industry: str) -> str:
        """Get guidelines for a specific industry"""
        query = f"{industry} industry resume guidelines keywords jargon"
        results = self.query(query, n_results=3)
        
        if results:
            return "\n\n".join([r['content'] for r in results])
        else:
            return f"Use industry-specific terminology and focus on relevant achievements for {industry}"
    
    def get_best_practices(self, section: str) -> str:
        """Get best practices for a specific resume section"""
        query = f"{section} resume best practices tips guidelines"
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
        """Get relevant action verbs"""
        query = f"{industry} action verbs resume writing"
        results = self.query(query, n_results=2)
        
        if results:
            return "\n\n".join([r['content'] for r in results])
        else:
            # Fallback verbs
            return "Managed, Led, Developed, Implemented, Created, Designed, Analyzed, Optimized, Increased, Improved"
    
    def health_check(self) -> Dict:
        """Check the health of the RAG system"""
        status = {
            "embedding_model": self.embedding_model is not None,
            "vector_store": self.collection is not None,
            "documents_loaded": 0,
            "status": "healthy"
        }
        
        if self.collection:
            try:
                status["documents_loaded"] = self.collection.count()
            except:
                status["status"] = "error"
        
        if not status["embedding_model"] or not status["vector_store"]:
            status["status"] = "unhealthy"
        
        return status 
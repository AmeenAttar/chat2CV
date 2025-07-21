import os
import json
import re
from typing import List, Dict, Optional
from pathlib import Path
from difflib import SequenceMatcher

class SimpleRAGService:
    """
    Simple RAG service using basic text processing and keyword matching.
    This provides the core functionality needed for Epic 5 without complex dependencies.
    """
    
    def __init__(self, knowledge_base_path: str = "app/knowledge_base"):
        self.knowledge_base_path = Path(knowledge_base_path)
        self.knowledge_base = {}
        self.keyword_index = {}
        
        # Initialize knowledge base
        self._load_knowledge_base()
        self._build_keyword_index()
    
    def _load_knowledge_base(self):
        """Load knowledge base files into memory"""
        try:
            knowledge_files = [
                "best_practices.md",
                "industry_guidelines.md", 
                "resume_best_practices.md",
                "template_guidelines.md"
            ]
            
            for filename in knowledge_files:
                file_path = self.knowledge_base_path / filename
                if file_path.exists():
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    # Split content into chunks
                    chunks = self._split_text(content, chunk_size=300, overlap=30)
                    
                    self.knowledge_base[filename] = {
                        'content': content,
                        'chunks': chunks
                    }
            
            print(f"✅ Loaded {len(self.knowledge_base)} knowledge base files")
            
        except Exception as e:
            print(f"⚠️  Failed to load knowledge base: {e}")
    
    def _build_keyword_index(self):
        """Build a simple keyword index for faster searching"""
        try:
            for filename, data in self.knowledge_base.items():
                self.keyword_index[filename] = {}
                
                for i, chunk in enumerate(data['chunks']):
                    # Extract keywords (simple approach)
                    words = re.findall(r'\b\w+\b', chunk.lower())
                    keywords = [word for word in words if len(word) > 3]  # Filter short words
                    
                    for keyword in keywords:
                        if keyword not in self.keyword_index[filename]:
                            self.keyword_index[filename][keyword] = []
                        self.keyword_index[filename][keyword].append(i)
            
            print("✅ Keyword index built successfully")
            
        except Exception as e:
            print(f"⚠️  Failed to build keyword index: {e}")
    
    def _split_text(self, text: str, chunk_size: int = 300, overlap: int = 30) -> List[str]:
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
    
    def _calculate_similarity(self, query: str, text: str) -> float:
        """Calculate text similarity using sequence matching"""
        query_lower = query.lower()
        text_lower = text.lower()
        
        # Simple keyword matching
        query_words = set(re.findall(r'\b\w+\b', query_lower))
        text_words = set(re.findall(r'\b\w+\b', text_lower))
        
        if not query_words:
            return 0.0
        
        # Calculate word overlap
        overlap = len(query_words.intersection(text_words))
        word_similarity = overlap / len(query_words)
        
        # Calculate sequence similarity
        sequence_similarity = SequenceMatcher(None, query_lower, text_lower).ratio()
        
        # Combine both metrics
        return (word_similarity * 0.7) + (sequence_similarity * 0.3)
    
    def query(self, query_text: str, n_results: int = 5) -> List[Dict]:
        """
        Query the knowledge base for relevant information
        
        Args:
            query_text: The query text
            n_results: Number of results to return
            
        Returns:
            List of relevant documents with metadata
        """
        if not self.knowledge_base:
            print("⚠️  Knowledge base not loaded, returning empty results")
            return []
        
        try:
            results = []
            
            for filename, data in self.knowledge_base.items():
                for i, chunk in enumerate(data['chunks']):
                    similarity = self._calculate_similarity(query_text, chunk)
                    
                    if similarity > 0.1:  # Only include relevant results
                        results.append({
                            'content': chunk,
                            'metadata': {
                                'source': filename,
                                'chunk_id': i,
                                'type': 'knowledge_base'
                            },
                            'similarity': similarity
                        })
            
            # Sort by similarity and return top results
            results.sort(key=lambda x: x['similarity'], reverse=True)
            return results[:n_results]
            
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
        # For now, return a curated list of action verbs
        # In a full implementation, this would query the knowledge base
        action_verbs = {
            "general": "Managed, Led, Developed, Implemented, Created, Designed, Analyzed, Optimized, Increased, Improved",
            "technology": "Developed, Engineered, Built, Designed, Implemented, Deployed, Optimized, Scaled, Automated, Integrated",
            "marketing": "Launched, Managed, Increased, Generated, Developed, Coordinated, Executed, Optimized, Analyzed, Improved",
            "finance": "Managed, Analyzed, Developed, Implemented, Optimized, Increased, Reduced, Generated, Coordinated, Led",
            "healthcare": "Provided, Managed, Coordinated, Developed, Implemented, Improved, Analyzed, Led, Facilitated, Enhanced"
        }
        
        return action_verbs.get(industry.lower(), action_verbs["general"])
    
    def health_check(self) -> Dict:
        """Check the health of the RAG system"""
        status = {
            "knowledge_base_loaded": len(self.keyword_index) > 0,
            "files_loaded": len(self.knowledge_base),
            "total_chunks": sum(len(data['chunks']) for data in self.knowledge_base.values()),
            "status": "healthy"
        }
        
        if not status["knowledge_base_loaded"]:
            status["status"] = "unhealthy"
        
        return status
    
    def test_query(self, query: str) -> str:
        """Test the RAG system with a sample query"""
        results = self.query(query, n_results=2)
        
        if results:
            return f"Found {len(results)} relevant results:\n\n" + "\n\n---\n\n".join([
                f"**Source:** {r['metadata']['source']}\n**Similarity:** {r['similarity']:.2f}\n\n{r['content']}"
                for r in results
            ])
        else:
            return "No relevant results found for this query." 
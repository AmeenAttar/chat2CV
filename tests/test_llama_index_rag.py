#!/usr/bin/env python3
"""
Test script for LlamaIndex RAG service with true vector embeddings
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Add the app directory to the path
sys.path.append(str(Path(__file__).parent / "app"))

from app.services.llama_index_rag import LlamaIndexRAGService

def test_llama_index_rag():
    """Test the LlamaIndex RAG service"""
    print("🧪 Testing LlamaIndex RAG Service with True Vector Embeddings")
    print("=" * 60)
    
    # Check if OpenAI API key is set
    if not os.getenv("OPENAI_API_KEY"):
        print("❌ OPENAI_API_KEY not set. Please set it in your environment.")
        return False
    
    try:
        # Initialize the RAG service
        print("📦 Initializing LlamaIndex RAG Service...")
        rag_service = LlamaIndexRAGService()
        
        # Check health
        print("\n🏥 Health Check:")
        health = rag_service.health_check()
        for key, value in health.items():
            print(f"  {key}: {value}")
        
        if health["status"] != "healthy":
            print("❌ RAG service is not healthy")
            return False
        
        # Test queries
        test_queries = [
            "resume best practices",
            "work experience section guidelines",
            "professional template style",
            "tech industry keywords",
            "action verbs for resume"
        ]
        
        print("\n🔍 Testing Semantic Search Queries:")
        for query in test_queries:
            print(f"\nQuery: '{query}'")
            results = rag_service.query(query, n_results=2)
            
            if results:
                print(f"  ✅ Found {len(results)} results")
                for i, result in enumerate(results[:2], 1):
                    content_preview = result['content'][:100] + "..." if len(result['content']) > 100 else result['content']
                    print(f"  {i}. {content_preview}")
                    print(f"     Source: {result['metadata'].get('source', 'unknown')}")
            else:
                print("  ⚠️  No results found")
        
        # Test specific methods
        print("\n🎯 Testing Specific Methods:")
        
        # Test template guidelines
        template_guidelines = rag_service.get_template_guidelines("professional")
        print(f"  Template Guidelines: {template_guidelines[:100]}...")
        
        # Test best practices
        best_practices = rag_service.get_best_practices("work")
        print(f"  Work Experience Best Practices: {best_practices[:100]}...")
        
        # Test action verbs
        action_verbs = rag_service.get_action_verbs("tech")
        print(f"  Tech Action Verbs: {action_verbs[:100]}...")
        
        # Test industry guidelines
        industry_guidelines = rag_service.get_industry_guidelines("tech")
        print(f"  Tech Industry Guidelines: {industry_guidelines[:100]}...")
        
        print("\n✅ All tests completed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_llama_index_rag()
    sys.exit(0 if success else 1) 
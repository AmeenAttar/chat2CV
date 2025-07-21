#!/usr/bin/env python3
"""
Test script for LlamaIndex RAG service structure (without API key)
"""

import os
import sys
from pathlib import Path

# Add the app directory to the path
sys.path.append(str(Path(__file__).parent / "app"))

def test_imports():
    """Test that all imports work correctly"""
    print("🧪 Testing LlamaIndex RAG Service Imports")
    print("=" * 50)
    
    try:
        # Test basic imports
        from app.services.llama_index_rag import LlamaIndexRAGService
        print("✅ LlamaIndexRAGService import successful")
        
        # Test LlamaIndex imports
        from llama_index.core import VectorStoreIndex, SimpleDirectoryReader, ServiceContext
        print("✅ LlamaIndex core imports successful")
        
        from llama_index.vector_stores.chroma import ChromaVectorStore
        print("✅ ChromaVectorStore import successful")
        
        from llama_index.embeddings.openai import OpenAIEmbedding
        print("✅ OpenAIEmbedding import successful")
        
        from llama_index.core.node_parser import SentenceSplitter
        print("✅ SentenceSplitter import successful")
        
        from llama_index.llms.openai import OpenAI
        print("✅ OpenAI LLM import successful")
        
        print("\n✅ All imports successful!")
        return True
        
    except Exception as e:
        print(f"❌ Import failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_class_structure():
    """Test that the class can be instantiated (without API key)"""
    print("\n🏗️  Testing Class Structure")
    print("=" * 30)
    
    try:
        from app.services.llama_index_rag import LlamaIndexRAGService
        
        # Test class definition
        print("✅ LlamaIndexRAGService class definition found")
        
        # Test that we can create an instance (it will fail on API key, but that's expected)
        try:
            rag_service = LlamaIndexRAGService()
            print("❌ Unexpected: Service initialized without API key")
            return False
        except Exception as e:
            if "OPENAI_API_KEY" in str(e) or "api_key" in str(e).lower():
                print("✅ Expected: Service correctly requires API key")
                return True
            else:
                print(f"❌ Unexpected error: {e}")
                return False
                
    except Exception as e:
        print(f"❌ Class structure test failed: {e}")
        return False

if __name__ == "__main__":
    print("🧪 LlamaIndex RAG Service Structure Test")
    print("=" * 50)
    
    success1 = test_imports()
    success2 = test_class_structure()
    
    if success1 and success2:
        print("\n🎉 All structure tests passed!")
        print("The LlamaIndex RAG service is properly structured and ready for use.")
        print("To test with actual functionality, set OPENAI_API_KEY and run test_llama_index_rag.py")
        sys.exit(0)
    else:
        print("\n❌ Some tests failed. Check the errors above.")
        sys.exit(1) 
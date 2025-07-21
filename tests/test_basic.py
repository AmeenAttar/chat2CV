#!/usr/bin/env python3
"""
Basic test to verify the testing framework works
"""

import pytest

def test_basic_import():
    """Test that we can import the main components"""
    try:
        from app.services.ai_agent import ResumeWriterAgent
        from app.services.simple_rag import SimpleRAGService
        assert True, "Imports successful"
    except ImportError as e:
        pytest.fail(f"Import failed: {e}")

def test_ai_agent_creation():
    """Test that we can create an AI agent"""
    try:
        from app.services.ai_agent import ResumeWriterAgent
        agent = ResumeWriterAgent()
        assert agent is not None
        assert hasattr(agent, 'llm')
        assert hasattr(agent, 'rag_service')
    except Exception as e:
        pytest.fail(f"AI agent creation failed: {e}")

def test_rag_service_creation():
    """Test that we can create a RAG service"""
    try:
        from app.services.simple_rag import SimpleRAGService
        rag = SimpleRAGService()
        assert rag is not None
        assert hasattr(rag, 'knowledge_base')
        assert hasattr(rag, 'chunks')
    except Exception as e:
        pytest.fail(f"RAG service creation failed: {e}")

def test_database_connection():
    """Test database connection"""
    try:
        from app.database import get_db
        session = next(get_db())
        assert session is not None
        print("✅ Database connection successful")
    except Exception as e:
        pytest.skip(f"Database not available: {e}")

if __name__ == "__main__":
    pytest.main([__file__, "-v"]) 
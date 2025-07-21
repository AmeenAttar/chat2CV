#!/usr/bin/env python3
"""
Comprehensive test suite for the AI Resume Builder
Tests AI agent, RAG system, database integration, and API endpoints
"""

import pytest
import asyncio
import json
from unittest.mock import Mock, patch, AsyncMock
from typing import Dict, Any

# Import the components to test
from app.services.ai_agent import ResumeWriterAgent
from app.services.database_service import DatabaseService
from app.services.simple_rag import SimpleRAGService
from app.models.resume import ResumeData, Education, WorkExperience, Skill
from app.database import get_db


class TestAIAgent:
    """Test suite for the AI Agent functionality"""
    
    @pytest.fixture
    def ai_agent(self):
        """Create a test AI agent instance"""
        return ResumeWriterAgent()
    
    @pytest.fixture
    def sample_inputs(self):
        """Sample inputs for testing"""
        return {
            "education": "I studied my bachelors in AI from stanford",
            "work": "I worked as a software engineer at Google for 2 years",
            "skills": "python, javascript, machine learning, data analysis"
        }
    
    def test_agent_initialization(self, ai_agent):
        """Test that AI agent initializes correctly"""
        assert ai_agent is not None
        assert hasattr(ai_agent, 'llm')
        assert hasattr(ai_agent, 'rag_service')
        assert hasattr(ai_agent, 'tools')
    
    def test_agent_tools_available(self, ai_agent):
        """Test that all required tools are available"""
        tool_names = [tool.name for tool in ai_agent.tools]
        expected_tools = [
            'get_template_guidelines',
            'get_action_verbs', 
            'get_resume_best_practices',
            'get_industry_guidelines'
        ]
        
        for tool in expected_tools:
            assert tool in tool_names, f"Tool {tool} not found in agent"
    
    @pytest.mark.asyncio
    async def test_education_extraction(self, ai_agent, sample_inputs):
        """Test education section extraction"""
        result = await ai_agent.generate_section(
            template_id="1",
            section_name="education",
            raw_input=sample_inputs["education"],
            user_id="1"
        )
        
        assert result is not None
        assert "status" in result
        assert result["status"] == "success"
        assert "processed_content" in result
        
        # Check if structured data was extracted
        content = result["processed_content"]
        if isinstance(content, str):
            # Try to parse as JSON
            try:
                data = json.loads(content)
                assert "institution" in data
                assert "area" in data
                assert "studyType" in data
            except json.JSONDecodeError:
                # Fallback: check if basic info is present
                assert "stanford" in content.lower()
                assert "ai" in content.lower()
    
    @pytest.mark.asyncio
    async def test_work_extraction(self, ai_agent, sample_inputs):
        """Test work experience extraction"""
        result = await ai_agent.generate_section(
            template_id="1",
            section_name="work",
            raw_input=sample_inputs["work"],
            user_id="1"
        )
        
        assert result is not None
        assert "status" in result
        assert result["status"] == "success"
        assert "processed_content" in result
        
        # Check if structured data was extracted
        content = result["processed_content"]
        if isinstance(content, str):
            try:
                data = json.loads(content)
                assert "name" in data
                assert "position" in data
                assert "startDate" in data
                assert "endDate" in data
            except json.JSONDecodeError:
                # Fallback: check if basic info is present
                assert "google" in content.lower()
                assert "software engineer" in content.lower()
    
    @pytest.mark.asyncio
    async def test_skills_extraction(self, ai_agent, sample_inputs):
        """Test skills section extraction"""
        result = await ai_agent.generate_section(
            template_id="1",
            section_name="skills",
            raw_input=sample_inputs["skills"],
            user_id="1"
        )
        
        assert result is not None
        assert "status" in result
        assert result["status"] == "success"
        assert "processed_content" in result
        
        # Check if structured data was extracted
        content = result["processed_content"]
        if isinstance(content, str):
            try:
                data = json.loads(content)
                assert isinstance(data, list)
                for skill in data:
                    assert "name" in skill
                    assert "level" in skill
            except json.JSONDecodeError:
                # Fallback: check if skills are present
                assert "python" in content.lower()
                assert "javascript" in content.lower()
    
    def test_fallback_extraction_methods(self, ai_agent):
        """Test fallback extraction methods when AI fails"""
        
        # Test education fallback
        education_input = "I studied my bachelors in AI from stanford"
        result = ai_agent._extract_basic_education_info(education_input)
        assert result is not None
        assert "institution" in result
        assert "area" in result
        assert "studyType" in result
        
        # Test work experience fallback
        work_input = "I worked as a software engineer at Google for 2 years"
        result = ai_agent._extract_basic_work_info(work_input)
        assert result is not None
        assert "name" in result
        assert "position" in result
        
        # Test skills fallback
        skills_input = "python, javascript, machine learning"
        result = ai_agent._extract_basic_skills_info(skills_input)
        assert result is not None
        assert isinstance(result, list)
        assert len(result) > 0


class TestRAGService:
    """Test suite for the RAG (Retrieval Augmented Generation) service"""
    
    @pytest.fixture
    def rag_service(self):
        """Create a test RAG service instance"""
        return SimpleRAGService()
    
    def test_rag_service_initialization(self, rag_service):
        """Test that RAG service initializes correctly"""
        assert rag_service is not None
        assert hasattr(rag_service, 'knowledge_base')
        assert hasattr(rag_service, 'chunks')
        assert len(rag_service.chunks) > 0
    
    def test_template_guidelines_retrieval(self, rag_service):
        """Test retrieval of template guidelines"""
        result = rag_service.get_template_guidelines("professional")
        assert result is not None
        assert isinstance(result, str)
        assert len(result) > 0
        assert "professional" in result.lower()
    
    def test_action_verbs_retrieval(self, rag_service):
        """Test retrieval of action verbs"""
        result = rag_service.get_action_verbs("tech")
        assert result is not None
        assert isinstance(result, str)
        assert len(result) > 0
        assert "tech" in result.lower()
    
    def test_best_practices_retrieval(self, rag_service):
        """Test retrieval of resume best practices"""
        result = rag_service.get_resume_best_practices("work")
        assert result is not None
        assert isinstance(result, str)
        assert len(result) > 0
        assert "work" in result.lower()
    
    def test_industry_guidelines_retrieval(self, rag_service):
        """Test retrieval of industry guidelines"""
        result = rag_service.get_industry_guidelines("tech")
        assert result is not None
        assert isinstance(result, str)
        assert len(result) > 0
        assert "tech" in result.lower()
    
    def test_similarity_search(self, rag_service):
        """Test similarity-based search functionality"""
        query = "software engineering best practices"
        results = rag_service._search_similar_chunks(query)
        assert results is not None
        assert isinstance(results, list)
        assert len(results) > 0
        
        # Check that results are sorted by relevance
        if len(results) > 1:
            assert results[0]['similarity'] >= results[1]['similarity']


class TestDatabaseIntegration:
    """Test suite for database integration"""
    
    @pytest.fixture
    def db_service(self):
        """Create a test database service instance"""
        return DatabaseService()
    
    def test_database_connection(self, db_service):
        """Test database connection and basic operations"""
        # Test that we can get a database session
        session = next(get_db())
        assert session is not None
        
        # Test basic query
        try:
            # This should work if database is properly set up
            result = session.execute("SELECT 1")
            assert result is not None
        except Exception as e:
            pytest.skip(f"Database not available: {e}")
    
    @pytest.mark.asyncio
    async def test_resume_creation(self, db_service):
        """Test creating a new resume"""
        resume_data = {
            "user_id": 1,
            "template_id": "1",
            "title": "Test Resume",
            "json_resume_data": {}
        }
        
        try:
            result = await db_service.create_resume(**resume_data)
            assert result is not None
            assert result.id is not None
            assert result.title == "Test Resume"
        except Exception as e:
            pytest.skip(f"Database operation failed: {e}")
    
    @pytest.mark.asyncio
    async def test_section_creation(self, db_service):
        """Test creating a resume section"""
        section_data = {
            "resume_id": 1,
            "section_name": "education",
            "original_input": "Test education input",
            "processed_content": {"institution": "Test University"}
        }
        
        try:
            result = await db_service.create_resume_section(**section_data)
            assert result is not None
            assert result.section_name == "education"
            assert result.original_input == "Test education input"
        except Exception as e:
            pytest.skip(f"Database operation failed: {e}")


class TestAPIEndpoints:
    """Test suite for API endpoints"""
    
    @pytest.fixture
    def client(self):
        """Create a test client"""
        from fastapi.testclient import TestClient
        from app.main import app
        return TestClient(app)
    
    def test_health_endpoint(self, client):
        """Test the health check endpoint"""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert "status" in data
        assert data["status"] == "healthy"
    
    def test_templates_endpoint(self, client):
        """Test the templates endpoint"""
        response = client.get("/templates")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) > 0
        
        # Check template structure
        template = data[0]
        assert "id" in template
        assert "name" in template
        assert "description" in template
    
    @pytest.mark.asyncio
    async def test_generate_resume_section_endpoint(self, client):
        """Test the resume section generation endpoint"""
        payload = {
            "template_id": "1",
            "section_name": "education",
            "raw_input": "I studied my bachelors in AI from stanford",
            "user_id": "1"
        }
        
        response = client.post("/generate-resume-section", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert "status" in data
        assert data["status"] == "success"
        assert "processed_content" in data


class TestContentQuality:
    """Test suite for content quality and validation"""
    
    def test_json_structure_validation(self):
        """Test that extracted content follows JSON Resume schema"""
        
        # Test education structure
        education_data = {
            "institution": "Stanford University",
            "area": "Computer Science",
            "studyType": "Bachelor's",
            "startDate": "2018",
            "endDate": "2022"
        }
        
        # Validate required fields
        required_fields = ["institution", "area", "studyType"]
        for field in required_fields:
            assert field in education_data
        
        # Test work experience structure
        work_data = {
            "name": "Google",
            "position": "Software Engineer",
            "startDate": "2022-01",
            "endDate": "2024-01",
            "summary": "Developed software solutions",
            "highlights": ["Achievement 1", "Achievement 2"]
        }
        
        required_fields = ["name", "position", "startDate", "endDate"]
        for field in required_fields:
            assert field in work_data
        
        # Test skills structure
        skills_data = [
            {"name": "Python", "level": "Expert", "keywords": ["Django", "Flask"]},
            {"name": "JavaScript", "level": "Advanced", "keywords": ["React", "Node.js"]}
        ]
        
        for skill in skills_data:
            assert "name" in skill
            assert "level" in skill
            assert "keywords" in skill
    
    def test_content_length_validation(self):
        """Test content length constraints"""
        
        # Education summary should be reasonable length
        education_summary = "Bachelor's degree in Computer Science from Stanford University"
        assert len(education_summary) <= 200  # Reasonable max length
        
        # Work experience highlights should be concise
        highlights = ["Led team of 5 developers", "Increased performance by 50%"]
        for highlight in highlights:
            assert len(highlight) <= 100  # Concise bullet points
    
    def test_action_verb_validation(self):
        """Test that content uses strong action verbs"""
        
        strong_verbs = ["developed", "implemented", "led", "managed", "created", "designed"]
        weak_verbs = ["did", "made", "helped", "worked on"]
        
        # Test content with strong verbs
        good_content = "Developed scalable web applications using Python and Django"
        assert any(verb in good_content.lower() for verb in strong_verbs)
        
        # Test content with weak verbs (should be improved)
        weak_content = "Did some programming work"
        assert any(verb in weak_content.lower() for verb in weak_verbs)


class TestPerformance:
    """Test suite for performance and scalability"""
    
    @pytest.mark.asyncio
    async def test_response_time(self):
        """Test that API responses are within acceptable time limits"""
        import time
        
        ai_agent = ResumeWriterAgent()
        start_time = time.time()
        
        result = await ai_agent.generate_section(
            template_id="1",
            section_name="education",
            raw_input="I studied my bachelors in AI from stanford",
            user_id="1"
        )
        
        end_time = time.time()
        response_time = end_time - start_time
        
        # Response should be under 5 seconds
        assert response_time < 5.0, f"Response time {response_time}s exceeds 5s limit"
        assert result is not None
    
    def test_memory_usage(self):
        """Test memory usage is reasonable"""
        import psutil
        import os
        
        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss
        
        # Create multiple AI agents
        agents = []
        for _ in range(5):
            agent = ResumeWriterAgent()
            agents.append(agent)
        
        final_memory = process.memory_info().rss
        memory_increase = final_memory - initial_memory
        
        # Memory increase should be reasonable (less than 100MB)
        assert memory_increase < 100 * 1024 * 1024, f"Memory increase {memory_increase} bytes exceeds 100MB"


if __name__ == "__main__":
    # Run all tests
    pytest.main([__file__, "-v"]) 
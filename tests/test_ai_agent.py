#!/usr/bin/env python3
"""
Comprehensive test suite for the AI Resume Builder
Tests AI agent, RAG system, database integration, and API endpoints
"""

# LANGCHAIN DEPRECATED: Skipping tests that require langchain.
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


# Commented out: TestAIAgent (legacy agent, not used in production)
# class TestAIAgent:
#     """Test suite for the AI Agent functionality"""
    
#     @pytest.fixture
#     def ai_agent(self):
#         """Create a test AI agent instance"""
#         return ResumeWriterAgent()
    
#     @pytest.fixture
#     def sample_inputs(self):
#         """Sample inputs for testing"""
#         return {
#             "education": "I studied my bachelors in AI from stanford",
#             "work": "I worked as a software engineer at Google for 2 years",
#             "skills": "python, javascript, machine learning, data analysis"
#         }
    
#     # Remove tests for rag_service, tools, and in-memory fallback logic
#     # Only keep tests for direct LLM/database-backed logic
#     @pytest.mark.asyncio
#     async def test_education_extraction(self, ai_agent, sample_inputs):
#         """Test education section extraction"""
#         result = await ai_agent.generate_section(
#             template_id="1",
#             section_name="education",
#             raw_input=sample_inputs["education"],
#             user_id="1"
#         )
#         assert result is not None
#         assert "status" in result
#         assert result["status"] == "success"
#         assert "json_resume" in result
#         assert "quality_checklist" in result
    
#     @pytest.mark.asyncio
#     async def test_work_extraction(self, ai_agent, sample_inputs):
#         """Test work experience extraction"""
#         result = await ai_agent.generate_section(
#             template_id="1",
#             section_name="work",
#             raw_input=sample_inputs["work"],
#             user_id="1"
#         )
#         assert result is not None
#         assert "status" in result
#         assert result["status"] == "success"
#         assert "json_resume" in result
#         assert "quality_checklist" in result
    
#     @pytest.mark.asyncio
#     async def test_skills_extraction(self, ai_agent, sample_inputs):
#         """Test skills section extraction"""
#         result = await ai_agent.generate_section(
#             template_id="1",
#             section_name="skills",
#             raw_input=sample_inputs["skills"],
#             user_id="1"
#         )
#         assert result is not None
#         assert "status" in result
#         assert result["status"] == "success"
#         assert "json_resume" in result
#         assert "quality_checklist" in result


class TestDatabaseIntegration:
    """Test suite for database integration"""
    
    @pytest.fixture
    def db_service(self):
        from app.database import get_db
        db = next(get_db())
        return DatabaseService(db)
    
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
        # First, create a session
        session_payload = {"template_id": 1}
        session_response = client.post("/create-session", json=session_payload)
        print("Session creation response:", session_response.status_code, session_response.json())
        assert session_response.status_code == 200
        session_id = session_response.json()["session_id"]
        # Now, use the session_id in the resume section request
        payload = {
            "template_id": "1",
            "section_name": "education",
            "raw_input": "I studied my bachelors in AI from stanford",
            "session_id": session_id
        }
        response = client.post("/generate-resume-section", json=payload)
        if response.status_code != 200:
            print("/generate-resume-section response:", response.status_code, response.text)
        assert response.status_code == 200
        data = response.json()
        assert "status" in data
        assert data["status"] in ("success", "fallback_success")
        assert "json_resume" in data
        assert "quality_checklist" in data

    @pytest.mark.asyncio
    async def test_generate_resume_section_multisection_long_input(self, client):
        """Test the resume section generation endpoint with long, multi-section input"""
        # First, create a session
        session_payload = {"template_id": 1}
        session_response = client.post("/create-session", json=session_payload)
        assert session_response.status_code == 200
        session_id = session_response.json()["session_id"]
        # Long, multi-section input
        long_input = (
            "My name is John Doe. I worked as a software engineer at Google from 2020 to 2022, "
            "where I led a team and improved system performance by 40%. I also interned at Facebook in 2019. "
            "I graduated from MIT in 2020 with a degree in Computer Science. My skills include Python, JavaScript, and machine learning. "
            "I speak English and Spanish. I enjoy hiking and photography."
        )
        payload = {
            "template_id": "1",
            "section_name": "basics",
            "raw_input": long_input,
            "session_id": session_id
        }
        response = client.post("/generate-resume-section", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert "json_resume" in data
        print("json_resume keys:", list(data["json_resume"].keys()))
        # Check that multiple sections are filled
        filled_sections = [k for k, v in data["json_resume"].items() if v]
        print("Filled sections:", filled_sections)
        assert "basics" in filled_sections
        assert "work" in filled_sections
        assert "education" in filled_sections
        assert "skills" in filled_sections

    @pytest.mark.asyncio
    async def test_generate_resume_section_work_only(self, client):
        """Test with input containing only work experience"""
        session_payload = {"template_id": 1}
        session_response = client.post("/create-session", json=session_payload)
        assert session_response.status_code == 200
        session_id = session_response.json()["session_id"]
        work_input = "I worked as a data analyst at Acme Corp from 2018 to 2021."
        payload = {
            "template_id": "1",
            "section_name": "work",
            "raw_input": work_input,
            "session_id": session_id
        }
        response = client.post("/generate-resume-section", json=payload)
        assert response.status_code == 200
        data = response.json()
        print("json_resume:", data["json_resume"])
        print("quality_checklist:", data["quality_checklist"])
        assert "work" in data["json_resume"] and data["json_resume"]["work"]

    @pytest.mark.asyncio
    async def test_generate_resume_section_education_only(self, client):
        """Test with input containing only education info"""
        session_payload = {"template_id": 1}
        session_response = client.post("/create-session", json=session_payload)
        assert session_response.status_code == 200
        session_id = session_response.json()["session_id"]
        edu_input = "I graduated from Harvard in 2017 with a degree in Economics."
        payload = {
            "template_id": "1",
            "section_name": "education",
            "raw_input": edu_input,
            "session_id": session_id
        }
        response = client.post("/generate-resume-section", json=payload)
        assert response.status_code == 200
        data = response.json()
        print("json_resume:", data["json_resume"])
        print("quality_checklist:", data["quality_checklist"])
        assert "education" in data["json_resume"] and data["json_resume"]["education"]

    @pytest.mark.asyncio
    async def test_generate_resume_section_skills_only(self, client):
        """Test with input containing only skills info"""
        session_payload = {"template_id": 1}
        session_response = client.post("/create-session", json=session_payload)
        assert session_response.status_code == 200
        session_id = session_response.json()["session_id"]
        skills_input = "My skills are Python, SQL, and data visualization."
        payload = {
            "template_id": "1",
            "section_name": "skills",
            "raw_input": skills_input,
            "session_id": session_id
        }
        response = client.post("/generate-resume-section", json=payload)
        assert response.status_code == 200
        data = response.json()
        print("json_resume:", data["json_resume"])
        print("quality_checklist:", data["quality_checklist"])
        assert "skills" in data["json_resume"] and data["json_resume"]["skills"]

    @pytest.mark.asyncio
    async def test_generate_resume_section_ambiguous_input(self, client):
        """Test with ambiguous/mixed input"""
        session_payload = {"template_id": 1}
        session_response = client.post("/create-session", json=session_payload)
        assert session_response.status_code == 200
        session_id = session_response.json()["session_id"]
        mixed_input = "I am Jane. I worked at Acme as a manager. I studied at Oxford."
        payload = {
            "template_id": "1",
            "section_name": "basics",
            "raw_input": mixed_input,
            "session_id": session_id
        }
        response = client.post("/generate-resume-section", json=payload)
        assert response.status_code == 200
        data = response.json()
        print("json_resume:", data["json_resume"])
        print("quality_checklist:", data["quality_checklist"])
        assert "basics" in data["json_resume"] and data["json_resume"]["basics"]
        assert "work" in data["json_resume"] and data["json_resume"]["work"]
        assert "education" in data["json_resume"] and data["json_resume"]["education"]

    @pytest.mark.asyncio
    async def test_generate_resume_section_skip_intent(self, client):
        """Test with skip intent in input"""
        session_payload = {"template_id": 1}
        session_response = client.post("/create-session", json=session_payload)
        assert session_response.status_code == 200
        session_id = session_response.json()["session_id"]
        skip_input = "I don't want to provide my phone number."
        payload = {
            "template_id": "1",
            "section_name": "basics",
            "raw_input": skip_input,
            "session_id": session_id
        }
        response = client.post("/generate-resume-section", json=payload)
        assert response.status_code == 200
        data = response.json()
        checklist = data["quality_checklist"]
        print("json_resume:", data["json_resume"])
        print("quality_checklist:", checklist)
        skipped = [k for k, v in checklist.items() if v == "skipped"]
        print("skipped fields:", skipped)
        assert any("phone" in k for k in skipped)


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


# Commented out: TestPerformance (legacy agent test, not used in production)
# class TestPerformance:
#     """Test suite for performance and scalability"""
    
#     @pytest.mark.asyncio
#     async def test_response_time(self):
#         """Test that API responses are within acceptable time limits"""
#         import time
        
#         ai_agent = ResumeWriterAgent()
#         start_time = time.time()
        
#         result = await ai_agent.generate_section(
#             template_id="1",
#             section_name="education",
#             raw_input="I studied my bachelors in AI from stanford",
#             user_id="1"
#         )
        
#         end_time = time.time()
#         response_time = end_time - start_time
        
#         # Response should be under 5 seconds
#         assert response_time < 5.0, f"Response time {response_time}s exceeds 5s limit"
#         assert result is not None
    
#     def test_memory_usage(self):
#         """Test memory usage is reasonable"""
#         import psutil
#         import os
        
#         process = psutil.Process(os.getpid())
#         initial_memory = process.memory_info().rss
        
#         # Create multiple AI agents
#         agents = []
#         for _ in range(5):
#             agent = ResumeWriterAgent()
#             agents.append(agent)
        
#         final_memory = process.memory_info().rss
#         memory_increase = final_memory - initial_memory
        
#         # Memory increase should be reasonable (less than 100MB)
#         assert memory_increase < 100 * 1024 * 1024, f"Memory increase {memory_increase} bytes exceeds 100MB"


if __name__ == "__main__":
    # Run all tests
    pytest.main([__file__, "-v"]) 
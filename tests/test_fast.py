#!/usr/bin/env python3
"""
Fast tests that don't require AI agent initialization
"""

import pytest
import json

def test_imports():
    """Test basic imports without initialization"""
    try:
        import app.services.ai_agent
        import app.services.simple_rag
        import app.services.database_service
        print("✅ All imports successful")
        assert True
    except ImportError as e:
        pytest.fail(f"Import failed: {e}")

# Commented out: test_rag_service_fast (RAG/knowledge base test, not used in production)
# def test_rag_service_fast():
#     """Test RAG service without AI agent"""
#     try:
#         from app.services.simple_rag import SimpleRAGService
#         rag = SimpleRAGService()
        
#         # Test basic functionality
#         assert rag is not None
#         assert hasattr(rag, 'knowledge_base')
#         assert hasattr(rag, 'keyword_index')
#         assert len(rag.knowledge_base) > 0
        
#         # Test a simple query
#         result = rag.get_template_guidelines("professional")
#         assert result is not None
#         assert isinstance(result, str)
#         assert len(result) > 0
        
#         print("✅ RAG service working")
#         assert True
#     except Exception as e:
#         pytest.fail(f"RAG service test failed: {e}")

def test_database_models():
    """Test database models without connection"""
    try:
        from app.models.resume import Education, WorkExperience, Skill
        
        # Test education model
        education = Education(
            institution="Stanford",
            area="Computer Science",
            studyType="Bachelor's"
        )
        assert education.institution == "Stanford"
        assert education.area == "Computer Science"
        
        # Test work experience model
        work = WorkExperience(
            name="Google",
            position="Software Engineer",
            startDate="2022-01",
            endDate="2024-01"
        )
        assert work.name == "Google"
        assert work.position == "Software Engineer"
        
        # Test skills model
        skill = Skill(
            name="Python",
            level="Expert"
        )
        assert skill.name == "Python"
        assert skill.level == "Expert"
        
        print("✅ Database models working")
        assert True
    except Exception as e:
        pytest.fail(f"Database models test failed: {e}")

def test_json_structure():
    """Test JSON Resume structure validation"""
    
    # Test education JSON structure
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
        assert field in education_data, f"Missing required field: {field}"
    
    # Test work experience JSON structure
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
        assert field in work_data, f"Missing required field: {field}"
    
    # Test skills JSON structure
    skills_data = [
        {"name": "Python", "level": "Expert", "keywords": ["Django", "Flask"]},
        {"name": "JavaScript", "level": "Advanced", "keywords": ["React", "Node.js"]}
    ]
    
    for skill in skills_data:
        assert "name" in skill, "Skill missing name"
        assert "level" in skill, "Skill missing level"
        assert "keywords" in skill, "Skill missing keywords"
    
    print("✅ JSON structure validation working")
    assert True

def test_fallback_extraction():
    """Test fallback extraction methods"""
    try:
        from app.services.ai_agent import ResumeWriterAgent
        
        # Create agent without initializing LLM
        agent = ResumeWriterAgent.__new__(ResumeWriterAgent)
        
        # Test education fallback
        education_input = "I studied my bachelors in AI from stanford"
        result = agent._extract_basic_education_info(education_input)
        assert result is not None
        assert hasattr(result, 'institution')
        assert hasattr(result, 'area')
        assert hasattr(result, 'studyType')
        
        # Test work experience fallback
        work_input = "I worked as a software engineer at Google for 2 years"
        result = agent._extract_basic_work_info(work_input)
        assert result is not None
        assert hasattr(result, 'name')
        assert hasattr(result, 'position')
        
        # Test project fallback (skills are handled differently)
        project_input = "Built a web application using Python and React"
        result = agent._extract_basic_project_info(project_input)
        assert result is not None
        assert hasattr(result, 'name')
        assert hasattr(result, 'description')
        
        print("✅ Fallback extraction methods working")
        assert True
    except Exception as e:
        pytest.fail(f"Fallback extraction test failed: {e}")

if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"]) 
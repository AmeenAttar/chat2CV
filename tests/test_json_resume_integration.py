#!/usr/bin/env python3
"""
Tests for JSON Resume Integration
Tests schema validation, theme rendering, and API endpoints
"""

import pytest
import json
from unittest.mock import Mock, patch
from app.services.schema_validator import JSONResumeValidator
from app.services.template_registry import TemplateRegistry, TemplateID
from app.services.resume_renderer import ResumeRenderer
from app.services.theme_preview_generator import ThemePreviewGenerator

class TestJSONResumeValidator:
    """Test JSON Resume schema validation"""
    
    def setup_method(self):
        self.validator = JSONResumeValidator()
    
    def test_valid_resume(self):
        """Test validation of valid resume data"""
        valid_resume = {
            "$schema": "https://raw.githubusercontent.com/jsonresume/resume-schema/v1.0.0/schema.json",
            "basics": {
                "name": "John Doe",
                "email": "john@example.com"
            }
        }
        result = self.validator.validate_resume(valid_resume)
        assert result["is_valid"] == True
        assert len(result["issues"]) == 0
    
    def test_invalid_resume_missing_basics(self):
        """Test validation of resume missing required basics"""
        invalid_resume = {
            "$schema": "https://raw.githubusercontent.com/jsonresume/resume-schema/v1.0.0/schema.json"
            # Missing basics section
        }
        result = self.validator.validate_resume(invalid_resume)
        assert result["is_valid"] == False
        assert len(result["issues"]) > 0
    
    def test_invalid_email_format(self):
        """Test validation of invalid email format"""
        invalid_resume = {
            "$schema": "https://raw.githubusercontent.com/jsonresume/resume-schema/v1.0.0/schema.json",
            "basics": {
                "name": "John Doe",
                "email": "invalid-email"
            }
        }
        result = self.validator.validate_resume(invalid_resume)
        assert result["is_valid"] == False
        assert any("Invalid email format" in issue for issue in result["issues"])
    
    def test_work_validation(self):
        """Test validation of work experience section"""
        resume_with_work = {
            "$schema": "https://raw.githubusercontent.com/jsonresume/resume-schema/v1.0.0/schema.json",
            "basics": {
                "name": "John Doe",
                "email": "john@example.com"
            },
            "work": [
                {
                    "name": "Tech Company",
                    "position": "Developer"
                    # Missing required startDate
                }
            ]
        }
        result = self.validator.validate_resume(resume_with_work)
        assert result["is_valid"] == False
        assert any("Missing required field: work[0].startDate" in issue for issue in result["issues"])
    
    def test_education_validation(self):
        """Test validation of education section"""
        resume_with_education = {
            "$schema": "https://raw.githubusercontent.com/jsonresume/resume-schema/v1.0.0/schema.json",
            "basics": {
                "name": "John Doe",
                "email": "john@example.com"
            },
            "education": [
                {
                    "institution": "University",
                    "area": "Computer Science"
                    # Missing required studyType
                }
            ]
        }
        result = self.validator.validate_resume(resume_with_education)
        assert result["is_valid"] == False
        assert any("Missing required field: education[0].studyType" in issue for issue in result["issues"])

class TestTemplateRegistry:
    """Test template registry with JSON Resume themes"""
    
    def setup_method(self):
        self.registry = TemplateRegistry()
    
    def test_theme_count(self):
        """Test that all 16 JSON Resume themes are registered"""
        themes = self.registry.get_all_themes()
        assert len(themes) == 16
    
    def test_theme_ids(self):
        """Test that theme IDs are correctly assigned"""
        assert self.registry.get_theme(TemplateID.CLASSY).npm_package == "jsonresume-theme-classy"
        assert self.registry.get_theme(TemplateID.ELEGANT).npm_package == "jsonresume-theme-elegant"
        assert self.registry.get_theme(TemplateID.KENDALL).npm_package == "jsonresume-theme-kendall"
    
    def test_theme_requirements(self):
        """Test that all themes use JSON Resume schema requirements"""
        theme = self.registry.get_theme(TemplateID.CLASSY)
        assert "basics" in theme.required_fields
        assert "work" in theme.required_fields
        assert "education" in theme.required_fields
        assert "skills" in theme.required_fields
    
    def test_basics_requirements(self):
        """Test basics section requirements"""
        required_fields = self.registry.get_required_fields(TemplateID.CLASSY, "basics")
        assert "name" in required_fields
        assert "email" in required_fields
    
    def test_work_requirements(self):
        """Test work section requirements"""
        required_fields = self.registry.get_required_fields(TemplateID.CLASSY, "work")
        assert "name" in required_fields
        assert "position" in required_fields
        assert "startDate" in required_fields

class TestResumeRenderer:
    """Test resume rendering with JSON Resume themes"""
    
    def setup_method(self):
        self.renderer = ResumeRenderer()
    
    def test_theme_mapping(self):
        """Test that theme IDs map to correct npm packages"""
        assert self.renderer.themes[1] == "jsonresume-theme-classy"
        assert self.renderer.themes[2] == "jsonresume-theme-elegant"
        assert self.renderer.themes[3] == "jsonresume-theme-kendall"
    
    def test_validate_theme(self):
        """Test theme validation"""
        assert self.renderer.validate_theme(1) == True
        assert self.renderer.validate_theme(16) == True
        assert self.renderer.validate_theme(99) == False
    
    @patch('subprocess.run')
    def test_render_html_success(self, mock_run):
        """Test successful HTML rendering"""
        mock_result = Mock()
        mock_result.returncode = 0
        mock_result.stdout = "<html><body>Test Resume</body></html>"
        mock_run.return_value = mock_result
        
        from app.models.resume import JSONResume, Basics
        resume = JSONResume(basics=Basics(name="Test", email="test@example.com"))
        
        html = self.renderer.render_html(resume, 1)
        assert html == "<html><body>Test Resume</body></html>"
    
    @patch('subprocess.run')
    def test_render_html_failure(self, mock_run):
        """Test fallback HTML when rendering fails"""
        mock_result = Mock()
        mock_result.returncode = 1
        mock_result.stderr = "Theme not found"
        mock_run.return_value = mock_result
        
        from app.models.resume import JSONResume, Basics
        resume = JSONResume(basics=Basics(name="Test", email="test@example.com"))
        
        html = self.renderer.render_html(resume, 1)
        assert html is not None
        assert "<html" in html.lower()
        assert "Test" in html

class TestThemePreviewGenerator:
    """Test theme preview generation"""
    
    def setup_method(self):
        self.generator = ThemePreviewGenerator()
    
    def test_sample_data_structure(self):
        """Test that sample data has correct JSON Resume structure"""
        sample_data = self.generator.get_sample_data()
        assert "basics" in sample_data
        assert "work" in sample_data
        assert "education" in sample_data
        assert "skills" in sample_data
        assert "projects" in sample_data
        
        # Check basics structure
        basics = sample_data["basics"]
        assert "name" in basics
        assert "email" in basics
        assert "label" in basics
    
    def test_sample_data_content(self):
        """Test that sample data has realistic content"""
        sample_data = self.generator.get_sample_data()
        basics = sample_data["basics"]
        
        assert basics["name"] == "John Doe"
        assert basics["label"] == "Software Engineer"
        assert basics["email"] == "john.doe@example.com"
        
        # Check work experience
        work = sample_data["work"]
        assert len(work) == 2
        assert work[0]["name"] == "TechCorp Inc"
        assert work[0]["position"] == "Senior Software Engineer"
    
    @patch('subprocess.run')
    def test_generate_preview_success(self, mock_run):
        """Test successful preview generation"""
        mock_result = Mock()
        mock_result.returncode = 0
        mock_result.stdout = "<html><body>Preview</body></html>"
        mock_run.return_value = mock_result
        
        preview = self.generator.generate_preview("jsonresume-theme-classy")
        assert preview == "<html><body>Preview</body></html>"
    
    @patch('subprocess.run')
    def test_generate_preview_failure(self, mock_run):
        """Test preview generation failure"""
        mock_result = Mock()
        mock_result.returncode = 1
        mock_result.stderr = "Theme not found"
        mock_run.return_value = mock_result
        
        preview = self.generator.generate_preview("invalid-theme")
        assert preview is None

class TestIntegration:
    """Integration tests for JSON Resume features"""
    
    def test_end_to_end_validation_and_rendering(self):
        """Test complete flow from validation to rendering"""
        # Create valid resume data
        resume_data = {
            "$schema": "https://raw.githubusercontent.com/jsonresume/resume-schema/v1.0.0/schema.json",
            "basics": {
                "name": "Jane Smith",
                "email": "jane@example.com",
                "label": "Data Scientist"
            },
            "work": [
                {
                    "name": "Data Corp",
                    "position": "Senior Data Scientist",
                    "startDate": "2020-01",
                    "summary": "Led machine learning projects"
                }
            ],
            "education": [
                {
                    "institution": "Tech University",
                    "area": "Computer Science",
                    "studyType": "Master"
                }
            ],
            "skills": [
                {
                    "name": "Python",
                    "level": "Expert"
                }
            ]
        }
        
        # Validate the data
        validator = JSONResumeValidator()
        validation_result = validator.validate_resume(resume_data)
        assert validation_result["is_valid"] == True
        
        # Test template registry
        registry = TemplateRegistry()
        theme = registry.get_theme(TemplateID.CLASSY)
        assert theme.npm_package == "jsonresume-theme-classy"
        
        # Test that the data meets theme requirements
        work_requirements = registry.get_required_fields(TemplateID.CLASSY, "work")
        for field in work_requirements:
            assert any(field in work for work in resume_data["work"])

if __name__ == "__main__":
    pytest.main([__file__]) 
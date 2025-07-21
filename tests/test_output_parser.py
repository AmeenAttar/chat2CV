#!/usr/bin/env python3
"""
Test suite for the Output Parser and Validation Service
"""

import pytest
import json
from app.services.output_parser import OutputParser, ContentValidator, QualityAssurance

class TestOutputParser:
    """Test suite for the OutputParser class"""
    
    @pytest.fixture
    def parser(self):
        return OutputParser()
    
    def test_clean_json_string(self, parser):
        """Test JSON string cleaning functionality"""
        # Test with malformed JSON
        malformed_json = '{institution: "Stanford", area: "AI", studyType: "Bachelor\'s",}'
        cleaned = parser._clean_json_string(malformed_json)
        
        # Should be valid JSON now
        try:
            data = json.loads(cleaned)
            assert data["institution"] == "Stanford"
            assert data["area"] == "AI"
            assert data["studyType"] == "Bachelor's"
        except json.JSONDecodeError:
            pytest.fail("Cleaned JSON should be valid")
    
    def test_parse_education_output(self, parser):
        """Test education output parsing"""
        # Valid JSON input
        valid_json = '{"institution": "Stanford", "area": "Computer Science", "studyType": "Bachelor\'s"}'
        result = parser.parse_education_output(valid_json)
        
        assert result is not None
        assert result.institution == "Stanford"
        assert result.area == "Computer Science"
        assert result.studyType == "Bachelor's"
    
    def test_parse_work_output(self, parser):
        """Test parsing work experience output"""
        valid_json = '{"name": "Google", "position": "Software Engineer", "startDate": "2022-01", "endDate": "2024-01", "summary": "Developed web applications"}'
        
        result = parser.parse_work_output(valid_json)
        
        assert result is not None
        assert result.name == "Google"
        assert result.position == "Software Engineer"
        assert result.startDate == "2022-01"
        assert result.endDate == "2024-01"
    
    def test_parse_skills_output(self, parser):
        """Test skills output parsing"""
        # Valid JSON input (list format)
        valid_json = '[{"name": "Python", "level": "Expert"}, {"name": "JavaScript", "level": "Advanced"}]'
        result = parser.parse_skills_output(valid_json)
        
        assert len(result) == 2
        assert result[0].name == "Python"
        assert result[0].level == "Expert"
        assert result[1].name == "JavaScript"
        assert result[1].level == "Advanced"
    
    def test_parse_invalid_json(self, parser):
        """Test parsing invalid JSON"""
        invalid_json = "This is not JSON"
        result = parser.parse_education_output(invalid_json)
        assert result is None


class TestContentValidator:
    """Test suite for the ContentValidator class"""
    
    @pytest.fixture
    def validator(self):
        return ContentValidator()
    
    def test_validate_education_content(self, validator):
        """Test education content validation"""
        from app.models.resume import Education
        
        # Valid education
        valid_education = Education(
            institution="Stanford University",
            area="Computer Science",
            studyType="Bachelor's"
        )
        result = validator.validate_education_content(valid_education)
        assert result["is_valid"] == True
        assert len(result["issues"]) == 0
        
        # Invalid education (missing institution)
        invalid_education = Education(
            institution="",
            area="Computer Science",
            studyType="Bachelor's"
        )
        result = validator.validate_education_content(invalid_education)
        assert result["is_valid"] == False
        assert len(result["issues"]) > 0
    
    def test_validate_work_content(self, validator):
        """Test validating work experience content"""
        from app.models.resume import WorkExperience
        
        # Valid work experience
        valid_work = WorkExperience(
            name="Google",
            position="Software Engineer",
            startDate="2022-01",
            endDate="2024-01",
            summary="Developed scalable web applications and improved performance by 40%"
        )
        
        result = validator.validate_work_content(valid_work)
        assert result["is_valid"] == True
        assert len(result["issues"]) == 0
        
        # Work experience with weak verbs
        weak_work = WorkExperience(
            name="Company",
            position="Developer",
            startDate="2022-01",
            endDate="2024-01",
            summary="Did some coding and stuff"
        )
        
        result = validator.validate_work_content(weak_work)
        assert len(result["suggestions"]) > 0  # Should suggest stronger verbs
    
    def test_validate_skills_content(self, validator):
        """Test skills content validation"""
        from app.models.resume import Skill
        
        # Valid skills
        valid_skills = [
            Skill(name="Python", level="Expert"),
            Skill(name="JavaScript", level="Advanced")
        ]
        result = validator.validate_skills_content(valid_skills)
        assert result["is_valid"] == True
        assert len(result["issues"]) == 0
        
        # Empty skills
        empty_skills = []
        result = validator.validate_skills_content(empty_skills)
        assert result["is_valid"] == False
        assert len(result["issues"]) > 0


class TestQualityAssurance:
    """Test suite for the QualityAssurance class"""
    
    @pytest.fixture
    def qa(self):
        return QualityAssurance()
    
    def test_process_education_section(self, qa):
        """Test education section processing"""
        # Valid JSON input
        valid_input = '{"institution": "Stanford", "area": "Computer Science", "studyType": "Bachelor\'s"}'
        result = qa.process_education_section(valid_input)
        
        assert result["status"] == "success"
        assert "parsed_content" in result
        assert "validation" in result
        assert result["validation"]["is_valid"] == True
    
    def test_process_work_section(self, qa):
        """Test processing work experience section"""
        valid_input = '{"name": "Google", "position": "Software Engineer", "startDate": "2022-01", "endDate": "2024-01", "summary": "Developed web applications"}'
        
        result = qa.process_work_section(valid_input)
        
        assert result["status"] == "success"
        assert "parsed_content" in result
        assert "validation" in result
    
    def test_process_skills_section(self, qa):
        """Test skills section processing"""
        # Valid JSON input
        valid_input = '[{"name": "Python", "level": "Expert"}, {"name": "JavaScript", "level": "Advanced"}]'
        result = qa.process_skills_section(valid_input)
        
        assert result["status"] == "success"
        assert "parsed_content" in result
        assert "validation" in result
        assert len(result["parsed_content"]) == 2
    
    def test_process_invalid_input(self, qa):
        """Test processing invalid input"""
        invalid_input = "This is not valid JSON"
        result = qa.process_education_section(invalid_input)
        
        assert result["status"] == "failed"
        assert "error" in result
        assert "raw_output" in result
    
    def test_get_quality_score(self, qa):
        """Test quality score calculation"""
        # Perfect result
        perfect_result = {
            "status": "success",
            "validation": {
                "issues": [],
                "suggestions": []
            }
        }
        score = qa.get_quality_score(perfect_result)
        assert score == 1.0
        
        # Result with issues
        issue_result = {
            "status": "warning",
            "validation": {
                "issues": ["Missing institution name"],
                "suggestions": ["Use stronger verbs"]
            }
        }
        score = qa.get_quality_score(issue_result)
        assert score < 1.0
        assert score > 0.0
        
        # Failed result
        failed_result = {
            "status": "failed"
        }
        score = qa.get_quality_score(failed_result)
        assert score == 0.0


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"]) 
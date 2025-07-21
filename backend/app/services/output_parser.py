#!/usr/bin/env python3
"""
Output Parser and Validation Service for AI Resume Builder
Ensures consistent, high-quality output from the AI agent
"""

import json
import re
from typing import Dict, List, Any, Optional, Union
from pydantic import BaseModel, ValidationError
from app.models.resume import Education, WorkExperience, Skill, Project

class OutputParser:
    """
    Parser for AI agent output to ensure consistent formatting
    """
    
    def __init__(self):
        self.max_lengths = {
            "education_summary": 200,
            "work_summary": 300,
            "work_highlight": 100,
            "skill_description": 50,
            "project_description": 200
        }
    
    def parse_education_output(self, raw_output: str) -> Optional[Education]:
        """Parse education section output"""
        try:
            # Try to parse as JSON first
            if isinstance(raw_output, str):
                # Clean up common JSON formatting issues
                cleaned_output = self._clean_json_string(raw_output)
                data = json.loads(cleaned_output)
            else:
                data = raw_output
            
            # Validate required fields
            required_fields = ["institution", "area", "studyType"]
            for field in required_fields:
                if field not in data:
                    raise ValueError(f"Missing required field: {field}")
            
            # Create Education model
            education = Education(
                institution=data.get("institution", ""),
                area=data.get("area", ""),
                studyType=data.get("studyType", ""),
                startDate=data.get("startDate", ""),
                endDate=data.get("endDate", ""),
                score=data.get("score"),
                courses=data.get("courses")
            )
            
            return education
            
        except (json.JSONDecodeError, ValidationError, ValueError) as e:
            print(f"⚠️  Education parsing failed: {e}")
            return None
    
    def parse_work_output(self, raw_output: str) -> Optional[WorkExperience]:
        """Parse work experience section output"""
        try:
            # Try to parse as JSON first
            if isinstance(raw_output, str):
                cleaned_output = self._clean_json_string(raw_output)
                data = json.loads(cleaned_output)
            else:
                data = raw_output
            
            # Validate required fields
            required_fields = ["name", "position", "startDate", "endDate"]
            for field in required_fields:
                if field not in data:
                    raise ValueError(f"Missing required field: {field}")
            
            # Validate highlights
            highlights = data.get("highlights", [])
            if not isinstance(highlights, list):
                highlights = []
            
            # Create WorkExperience model
            work = WorkExperience(
                name=data.get("name", ""),
                position=data.get("position", ""),
                startDate=data.get("startDate", ""),
                endDate=data.get("endDate", ""),
                summary=data.get("summary", ""),
                highlights=highlights
            )
            
            return work
            
        except (json.JSONDecodeError, ValidationError, ValueError) as e:
            print(f"⚠️  Work experience parsing failed: {e}")
            return None
    
    def parse_skills_output(self, raw_output: str) -> List[Skill]:
        """Parse skills section output"""
        try:
            # Try to parse as JSON first
            if isinstance(raw_output, str):
                cleaned_output = self._clean_json_string(raw_output)
                data = json.loads(cleaned_output)
            else:
                data = raw_output
            
            # Ensure data is a list
            if not isinstance(data, list):
                data = [data]
            
            skills = []
            for skill_data in data:
                if isinstance(skill_data, dict):
                    skill = Skill(
                        name=skill_data.get("name", ""),
                        level=skill_data.get("level", "Proficient"),
                        keywords=skill_data.get("keywords", [])
                    )
                    skills.append(skill)
            
            return skills
            
        except (json.JSONDecodeError, ValidationError, ValueError) as e:
            print(f"⚠️  Skills parsing failed: {e}")
            return []
    
    def parse_project_output(self, raw_output: str) -> Optional[Project]:
        """Parse project section output"""
        try:
            # Try to parse as JSON first
            if isinstance(raw_output, str):
                cleaned_output = self._clean_json_string(raw_output)
                data = json.loads(cleaned_output)
            else:
                data = raw_output
            
            # Validate required fields
            required_fields = ["name", "description"]
            for field in required_fields:
                if field not in data:
                    raise ValueError(f"Missing required field: {field}")
            
            # Create Project model
            project = Project(
                name=data.get("name", ""),
                description=data.get("description", ""),
                highlights=data.get("highlights", []),
                keywords=data.get("keywords", []),
                startDate=data.get("startDate", ""),
                endDate=data.get("endDate", ""),
                url=data.get("url"),
                roles=data.get("roles", []),
                entity=data.get("entity", ""),
                type=data.get("type", "")
            )
            
            return project
            
        except (json.JSONDecodeError, ValidationError, ValueError) as e:
            print(f"⚠️  Project parsing failed: {e}")
            return None
    
    def _clean_json_string(self, json_str: str) -> str:
        """Clean up common JSON formatting issues"""
        # Remove extra whitespace and newlines
        json_str = re.sub(r'\s+', ' ', json_str.strip())
        
        # Fix common JSON issues
        json_str = re.sub(r'([{,])\s*([a-zA-Z_][a-zA-Z0-9_]*)\s*:', r'\1"\2":', json_str)
        
        # Remove trailing commas
        json_str = re.sub(r',\s*}', '}', json_str)
        json_str = re.sub(r',\s*]', ']', json_str)
        
        return json_str


class ContentValidator:
    """
    Validator for content quality and consistency
    """
    
    def __init__(self):
        self.max_lengths = {
            "education_summary": 200,
            "work_summary": 300,
            "work_highlight": 100,
            "skill_description": 50,
            "project_description": 200
        }
        
        self.strong_verbs = [
            "developed", "implemented", "led", "managed", "created", "designed",
            "built", "launched", "optimized", "increased", "improved", "delivered",
            "executed", "coordinated", "facilitated", "established", "generated",
            "maintained", "performed", "produced", "provided", "resolved",
            "streamlined", "transformed", "upgraded", "utilized", "validated"
        ]
        
        self.weak_verbs = [
            "did", "made", "helped", "worked on", "was involved in", "participated in",
            "assisted with", "contributed to", "supported", "was part of"
        ]
    
    def validate_education_content(self, education: Education) -> Dict[str, Any]:
        """Validate education content quality"""
        issues = []
        suggestions = []
        
        # Check institution name
        if not education.institution or len(education.institution.strip()) < 2:
            issues.append("Institution name is missing or too short")
        
        # Check area of study
        if not education.area or len(education.area.strip()) < 2:
            issues.append("Area of study is missing or too short")
        
        # Check degree type
        if not education.studyType:
            issues.append("Degree type is missing")
        
        # Check dates
        if education.startDate and education.endDate:
            if education.startDate > education.endDate:
                issues.append("Start date is after end date")
        
        return {
            "is_valid": len(issues) == 0,
            "issues": issues,
            "suggestions": suggestions
        }
    
    def validate_work_content(self, work: WorkExperience) -> Dict[str, Any]:
        """Validate work experience content quality"""
        issues = []
        suggestions = []
        
        # Check company name
        if not work.name or len(work.name.strip()) < 2:
            issues.append("Company name is missing or too short")
        
        # Check position
        if not work.position or len(work.position.strip()) < 2:
            issues.append("Job position is missing or too short")
        
        # Check summary length
        if work.summary and len(work.summary) > self.max_lengths["work_summary"]:
            issues.append(f"Summary is too long (max {self.max_lengths['work_summary']} characters)")
        
        # Check highlights
        if not work.highlights or len(work.highlights) == 0:
            issues.append("No highlights/achievements provided")
        else:
            for i, highlight in enumerate(work.highlights):
                if len(highlight) > self.max_lengths["work_highlight"]:
                    issues.append(f"Highlight {i+1} is too long (max {self.max_lengths['work_highlight']} characters)")
                
                # Check for weak verbs
                highlight_lower = highlight.lower()
                if any(weak_verb in highlight_lower for weak_verb in self.weak_verbs):
                    suggestions.append(f"Consider using stronger action verbs in highlight {i+1}")
        
        # Check for strong action verbs
        if work.summary:
            summary_lower = work.summary.lower()
            if not any(strong_verb in summary_lower for strong_verb in self.strong_verbs):
                suggestions.append("Consider using stronger action verbs in summary")
        
        return {
            "is_valid": len(issues) == 0,
            "issues": issues,
            "suggestions": suggestions
        }
    
    def validate_skills_content(self, skills: List[Skill]) -> Dict[str, Any]:
        """Validate skills content quality"""
        issues = []
        suggestions = []
        
        if not skills or len(skills) == 0:
            issues.append("No skills provided")
            return {
                "is_valid": False,
                "issues": issues,
                "suggestions": suggestions
            }
        
        # Check each skill
        for i, skill in enumerate(skills):
            if not skill.name or len(skill.name.strip()) < 2:
                issues.append(f"Skill {i+1} name is missing or too short")
            
            if skill.level not in ["Beginner", "Intermediate", "Advanced", "Expert", "Proficient"]:
                suggestions.append(f"Consider using standard skill levels for skill {i+1}")
        
        return {
            "is_valid": len(issues) == 0,
            "issues": issues,
            "suggestions": suggestions
        }
    
    def validate_project_content(self, project: Project) -> Dict[str, Any]:
        """Validate project content quality"""
        issues = []
        suggestions = []
        
        # Check project name
        if not project.name or len(project.name.strip()) < 2:
            issues.append("Project name is missing or too short")
        
        # Check description
        if not project.description or len(project.description.strip()) < 10:
            issues.append("Project description is missing or too short")
        
        if project.description and len(project.description) > self.max_lengths["project_description"]:
            issues.append(f"Project description is too long (max {self.max_lengths['project_description']} characters)")
        
        # Check highlights
        if not project.highlights or len(project.highlights) == 0:
            issues.append("No project highlights provided")
        
        return {
            "is_valid": len(issues) == 0,
            "issues": issues,
            "suggestions": suggestions
        }


class QualityAssurance:
    """
    Quality assurance for AI-generated content
    """
    
    def __init__(self):
        self.parser = OutputParser()
        self.validator = ContentValidator()
    
    def process_education_section(self, raw_output: str) -> Dict[str, Any]:
        """Process and validate education section"""
        # Parse output
        education = self.parser.parse_education_output(raw_output)
        
        if not education:
            return {
                "status": "failed",
                "error": "Failed to parse education output",
                "raw_output": raw_output
            }
        
        # Validate content
        validation = self.validator.validate_education_content(education)
        
        return {
            "status": "success" if validation["is_valid"] else "warning",
            "parsed_content": education,
            "validation": validation,
            "raw_output": raw_output
        }
    
    def process_work_section(self, raw_output: str) -> Dict[str, Any]:
        """Process and validate work experience section"""
        # Parse output
        work = self.parser.parse_work_output(raw_output)
        
        if not work:
            return {
                "status": "failed",
                "error": "Failed to parse work experience output",
                "raw_output": raw_output
            }
        
        # Validate content
        validation = self.validator.validate_work_content(work)
        
        return {
            "status": "success" if validation["is_valid"] else "warning",
            "parsed_content": work,
            "validation": validation,
            "raw_output": raw_output
        }
    
    def process_skills_section(self, raw_output: str) -> Dict[str, Any]:
        """Process and validate skills section"""
        # Parse output
        skills = self.parser.parse_skills_output(raw_output)
        
        if not skills:
            return {
                "status": "failed",
                "error": "Failed to parse skills output",
                "raw_output": raw_output
            }
        
        # Validate content
        validation = self.validator.validate_skills_content(skills)
        
        return {
            "status": "success" if validation["is_valid"] else "warning",
            "parsed_content": skills,
            "validation": validation,
            "raw_output": raw_output
        }
    
    def process_project_section(self, raw_output: str) -> Dict[str, Any]:
        """Process and validate project section"""
        # Parse output
        project = self.parser.parse_project_output(raw_output)
        
        if not project:
            return {
                "status": "failed",
                "error": "Failed to parse project output",
                "raw_output": raw_output
            }
        
        # Validate content
        validation = self.validator.validate_project_content(project)
        
        return {
            "status": "success" if validation["is_valid"] else "warning",
            "parsed_content": project,
            "validation": validation,
            "raw_output": raw_output
        }
    
    def get_quality_score(self, result: Dict[str, Any]) -> float:
        """Calculate quality score for processed content"""
        if result["status"] == "failed":
            return 0.0
        
        validation = result["validation"]
        total_checks = len(validation["issues"]) + len(validation["suggestions"])
        
        if total_checks == 0:
            return 1.0
        
        # Issues are more severe than suggestions
        issue_penalty = len(validation["issues"]) * 0.3
        suggestion_penalty = len(validation["suggestions"]) * 0.1
        
        score = max(0.0, 1.0 - issue_penalty - suggestion_penalty)
        return round(score, 2) 
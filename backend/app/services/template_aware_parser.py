#!/usr/bin/env python3
"""
Template-Aware Output Parser and Validation Service
Adapts parsing and validation rules based on specific JSON Resume templates
"""

import json
import re
from typing import Dict, List, Any, Optional, Union
from pydantic import BaseModel, ValidationError
from app.models.resume import Education, WorkExperience, Skill, Project
from app.services.template_service import TemplateService

class TemplateAwareOutputParser:
    """
    Template-aware parser that adapts to different JSON Resume template requirements
    """
    
    def __init__(self):
        self.template_service = TemplateService()
        
        # Template-specific length constraints
        self.template_lengths = {
            "1": {  # Professional
                "work_summary": 250,
                "work_highlight": 120,
                "education_summary": 150,
                "project_description": 200,
                "skill_description": 50
            },
            "2": {  # Modern
                "work_summary": 300,
                "work_highlight": 150,
                "education_summary": 200,
                "project_description": 250,
                "skill_description": 60
            },
            "3": {  # Creative
                "work_summary": 200,
                "work_highlight": 100,
                "education_summary": 120,
                "project_description": 150,
                "skill_description": 40
            },
            "4": {  # Minimalist
                "work_summary": 150,
                "work_highlight": 80,
                "education_summary": 100,
                "project_description": 120,
                "skill_description": 30
            },
            "5": {  # Executive
                "work_summary": 400,
                "work_highlight": 200,
                "education_summary": 300,
                "project_description": 350,
                "skill_description": 80
            }
        }
    
    def get_template_structure(self, template_id: int, section_name: str) -> Dict[str, Any]:
        """Get template-specific structure requirements"""
        return self.template_service.get_template_json_structure(template_id, section_name)
    
    def get_template_lengths(self, template_id: int) -> Dict[str, int]:
        """Get template-specific length constraints"""
        # Use hardcoded constraints for now since they're more specific
        lengths = {
            1: {  # Professional
                "work_summary": 300,
                "work_highlight": 150,
                "education_summary": 200,
                "project_description": 250,
                "skill_description": 60
            },
            2: {  # Modern
                "work_summary": 300,
                "work_highlight": 150,
                "education_summary": 200,
                "project_description": 250,
                "skill_description": 60
            },
            3: {  # Creative
                "work_summary": 300,
                "work_highlight": 150,
                "education_summary": 200,
                "project_description": 250,
                "skill_description": 60
            },
            4: {  # Minimalist
                "work_summary": 150,
                "work_highlight": 80,
                "education_summary": 100,
                "project_description": 120,
                "skill_description": 30
            },
            5: {  # Executive
                "work_summary": 400,
                "work_highlight": 200,
                "education_summary": 300,
                "project_description": 350,
                "skill_description": 80
            }
        }
        return lengths.get(template_id, lengths[1])
    
    def parse_education_output(self, raw_output: str, template_id: int) -> Optional[Education]:
        """Parse education section output with template-specific requirements"""
        try:
            # Get template structure
            structure = self.get_template_structure(template_id, "education")
            required_fields = structure.get("fields", ["institution", "area", "studyType"])
            
            # Try to parse as JSON first
            if isinstance(raw_output, str):
                cleaned_output = self._clean_json_string(raw_output)
                data = json.loads(cleaned_output)
            else:
                data = raw_output
            
            # Validate required fields for this template
            for field in required_fields:
                if field not in data:
                    raise ValueError(f"Missing required field for template {template_id}: {field}")
            
            # Create Education model with template-specific fields
            education_data = {
                "institution": data.get("institution", ""),
                "area": data.get("area"),
                "studyType": data.get("studyType", ""),
                "startDate": data.get("startDate"),
                "endDate": data.get("endDate"),
                "score": data.get("score") or data.get("gpa"),  # Handle both score and gpa
                "courses": data.get("courses")
            }
            
            # Add template-specific fields
            if template_id == "3":  # Creative template
                education_data["score"] = data.get("gpa")  # Creative uses "gpa"
            elif template_id == "5":  # Executive template
                education_data["score"] = data.get("gpa")
                # Note: "honors" field not in our model, would need extension
            
            # Remove None values
            education_data = {k: v for k, v in education_data.items() if v is not None}
            
            return Education(**education_data)
            
        except (json.JSONDecodeError, ValidationError, ValueError) as e:
            print(f"⚠️  Education parsing failed for template {template_id}: {e}")
            return None
    
    def parse_work_output(self, raw_output: str, template_id: int) -> Optional[WorkExperience]:
        """Parse work experience section output with template awareness"""
        try:
            # Get template structure
            structure = self.get_template_structure(template_id, "work")
            required_fields = structure.get("fields", ["name", "position", "startDate", "endDate"])
            
            # Try to parse as JSON first
            if isinstance(raw_output, str):
                cleaned_output = self._clean_json_string(raw_output)
                data = json.loads(cleaned_output)
            else:
                data = raw_output
            
            # Validate required fields for this template
            for field in required_fields:
                if field not in data:
                    raise ValueError(f"Missing required field for template {template_id}: {field}")
            
            # Create WorkExperience model with template-specific fields
            work_data = {
                "name": data.get("name", ""),
                "position": data.get("position", ""),
                "startDate": data.get("startDate"),
                "endDate": data.get("endDate"),
                "summary": data.get("summary", ""),
                "highlights": data.get("highlights", []),
                "url": data.get("url"),
                "location": data.get("location"),
                "description": data.get("description")
            }
            
            # Add template-specific fields
            if template_id == "3":  # Creative template
                # Note: "technologies" field not in our model, would need extension
                pass
            elif template_id == "5":  # Executive template
                # Note: "achievements", "budget" fields not in our model, would need extension
                pass
            
            # Remove None values
            work_data = {k: v for k, v in work_data.items() if v is not None}
            
            return WorkExperience(**work_data)
            
        except (json.JSONDecodeError, ValidationError, ValueError) as e:
            print(f"⚠️  Work experience parsing failed for template {template_id}: {e}")
            return None
    
    def parse_skills_output(self, raw_output: str, template_id: int) -> List[Skill]:
        """Parse skills section output with template-specific requirements"""
        try:
            # Get template structure
            structure = self.get_template_structure(template_id, "skills")
            required_fields = structure.get("fields", ["name"])
            
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
                    # Validate required fields for this template
                    for field in required_fields:
                        if field not in skill_data:
                            print(f"⚠️  Missing required field {field} for skill in template {template_id}")
                            continue
                    
                    # Create skill with template-specific fields
                    skill_fields = {
                        "name": skill_data.get("name", ""),
                        "level": skill_data.get("level"),
                        "keywords": skill_data.get("keywords", [])
                    }
                    
                    # Add template-specific fields
                    if template_id == "3":  # Creative template
                        skill_fields["level"] = skill_data.get("level")
                        # Note: "category" field not in our model, would need extension
                    elif template_id == "5":  # Executive template
                        skill_fields["level"] = skill_data.get("level")
                        # Note: "years_experience" field not in our model, would need extension
                    
                    # Remove None values
                    skill_fields = {k: v for k, v in skill_fields.items() if v is not None}
                    
                    skill = Skill(**skill_fields)
                    skills.append(skill)
            
            return skills
            
        except (json.JSONDecodeError, ValidationError, ValueError) as e:
            print(f"⚠️  Skills parsing failed for template {template_id}: {e}")
            return []
    
    def parse_project_output(self, raw_output: str, template_id: int) -> Optional[Project]:
        """Parse project section output with template-specific requirements"""
        try:
            # Get template structure (using work structure as base for projects)
            structure = self.get_template_structure(template_id, "work")
            required_fields = ["name", "description"]  # Projects always need these
            
            # Try to parse as JSON first
            if isinstance(raw_output, str):
                cleaned_output = self._clean_json_string(raw_output)
                data = json.loads(cleaned_output)
            else:
                data = raw_output
            
            # Validate required fields
            for field in required_fields:
                if field not in data:
                    raise ValueError(f"Missing required field for project: {field}")
            
            # Create Project model
            project_data = {
                "name": data.get("name", ""),
                "description": data.get("description", ""),
                "highlights": data.get("highlights", []),
                "keywords": data.get("keywords", []),
                "startDate": data.get("startDate"),
                "endDate": data.get("endDate"),
                "url": data.get("url"),
                "roles": data.get("roles", []),
                "entity": data.get("entity"),
                "type": data.get("type")
            }
            
            # Remove None values
            project_data = {k: v for k, v in project_data.items() if v is not None}
            
            return Project(**project_data)
            
        except (json.JSONDecodeError, ValidationError, ValueError) as e:
            print(f"⚠️  Project parsing failed for template {template_id}: {e}")
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


class TemplateAwareContentValidator:
    """
    Template-aware validator that adapts validation rules based on template requirements
    """
    
    def __init__(self):
        self.template_service = TemplateService()
        
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
    
    def validate_education_content(self, education: Education, template_id: int) -> Dict[str, Any]:
        """Validate education content quality with template-specific rules"""
        issues = []
        suggestions = []
        
        # Get template structure
        structure = self.template_service.get_template_json_structure(template_id, "education")
        required_fields = structure.get("fields", ["institution", "area", "studyType"])
        lengths = self._get_template_lengths(template_id)
        
        # Check required fields for this template
        if "institution" in required_fields and (not education.institution or len(education.institution.strip()) < 2):
            issues.append("Institution name is missing or too short")
        
        if "area" in required_fields and (not education.area or len(education.area.strip()) < 2):
            issues.append("Area of study is missing or too short")
        
        if "studyType" in required_fields and not education.studyType:
            issues.append("Degree type is missing")
        
        # Template-specific validations
        if template_id == "4":  # Minimalist - no startDate required
            if education.startDate and education.endDate:
                if education.startDate > education.endDate:
                    issues.append("Start date is after end date")
        else:  # Other templates require startDate
            if "startDate" in required_fields and not education.startDate:
                issues.append("Start date is missing")
        
        # Length validations based on template (Education doesn't have summary field)
        # Note: Education model doesn't have summary field, so skip length validation
        
        return {
            "is_valid": len(issues) == 0,
            "issues": issues,
            "suggestions": suggestions
        }
    
    def validate_work_content(self, work: WorkExperience, template_id: int) -> Dict[str, Any]:
        """Validate work experience content quality with template awareness"""
        issues = []
        suggestions = []
        
        # Get template structure
        structure = self.template_service.get_template_json_structure(template_id, "work")
        required_fields = structure.get("fields", ["name", "position", "startDate", "endDate"])
        lengths = self._get_template_lengths(template_id)
        
        # Check required fields for this template
        if "name" in required_fields and (not work.name or len(work.name.strip()) < 2):
            issues.append("Company name is missing or too short")
        
        if "position" in required_fields and (not work.position or len(work.position.strip()) < 2):
            issues.append("Job position is missing or too short")
        
        # Template-specific validations
        if template_id == "4":  # Minimalist - no startDate required
            if work.startDate and work.endDate:
                if work.startDate > work.endDate:
                    issues.append("Start date is after end date")
        else:  # Other templates require startDate
            if "startDate" in required_fields and not work.startDate:
                issues.append("Start date is missing")
        
        # Length validations based on template
        if work.summary and len(work.summary) > lengths["work_summary"]:
            issues.append(f"Summary is too long for {template_id} template (max {lengths['work_summary']} characters)")
        
        # Check highlights based on template requirements
        if "highlights" in required_fields:
            if not work.highlights or len(work.highlights) == 0:
                issues.append("No highlights/achievements provided")
            else:
                for i, highlight in enumerate(work.highlights):
                    if len(highlight) > lengths["work_highlight"]:
                        issues.append(f"Highlight {i+1} is too long for {template_id} template (max {lengths['work_highlight']} characters)")
                    
                    # Check for weak verbs
                    highlight_lower = highlight.lower()
                    if any(weak_verb in highlight_lower for weak_verb in self.weak_verbs):
                        suggestions.append(f"Consider using stronger action verbs in highlight {i+1}")
        # Note: Minimalist template (4) doesn't require highlights
        
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
    
    def validate_skills_content(self, skills: List[Skill], template_id: int) -> Dict[str, Any]:
        """Validate skills content quality with template-specific rules"""
        issues = []
        suggestions = []
        
        # Get template structure
        structure = self.template_service.get_template_json_structure(template_id, "skills")
        required_fields = structure.get("fields", ["name"])
        
        if not skills or len(skills) == 0:
            issues.append("No skills provided")
            return {
                "is_valid": False,
                "issues": issues,
                "suggestions": suggestions
            }
        
        # Check each skill
        for i, skill in enumerate(skills):
            if "name" in required_fields and (not skill.name or len(skill.name.strip()) < 2):
                issues.append(f"Skill {i+1} name is missing or too short")
            
            # Template-specific validations
            if template_id in ["1", "2", "5"] and "level" in required_fields:
                if not skill.level or skill.level not in ["Beginner", "Intermediate", "Advanced", "Expert", "Proficient"]:
                    suggestions.append(f"Consider using standard skill levels for skill {i+1}")
        
        return {
            "is_valid": len(issues) == 0,
            "issues": issues,
            "suggestions": suggestions
        }
    
    def validate_project_content(self, project: Project, template_id: int) -> Dict[str, Any]:
        """Validate project content quality with template-specific rules"""
        issues = []
        suggestions = []
        
        # Get template structure
        structure = self.template_service.get_template_json_structure(template_id, "work")  # Use work structure as base
        required_fields = ["name", "description"]  # Projects always need these
        lengths = self._get_template_lengths(template_id)
        
        # Check required fields
        if "name" in required_fields and (not project.name or len(project.name.strip()) < 2):
            issues.append("Project name is missing or too short")
        
        if "description" in required_fields and (not project.description or len(project.description.strip()) < 10):
            issues.append("Project description is missing or too short")
        
        # Length validations based on template
        if project.description and len(project.description) > lengths["project_description"]:
            issues.append(f"Project description is too long for {template_id} template (max {lengths['project_description']} characters)")
        
        # Check highlights based on template requirements
        if "highlights" in structure.get("fields", []):
            if not project.highlights or len(project.highlights) == 0:
                issues.append("No project highlights provided")
        
        return {
            "is_valid": len(issues) == 0,
            "issues": issues,
            "suggestions": suggestions
        }
    
    def _get_template_lengths(self, template_id: int) -> Dict[str, int]:
        """Get template-specific length constraints"""
        lengths = {
            1: {  # Professional
                "work_summary": 300,
                "work_highlight": 150,
                "education_summary": 200,
                "project_description": 250,
                "skill_description": 60
            },
            2: {  # Modern
                "work_summary": 300,
                "work_highlight": 150,
                "education_summary": 200,
                "project_description": 250,
                "skill_description": 60
            },
            3: {  # Creative
                "work_summary": 300,
                "work_highlight": 150,
                "education_summary": 200,
                "project_description": 250,
                "skill_description": 60
            },
            4: {  # Minimalist
                "work_summary": 150,
                "work_highlight": 80,
                "education_summary": 100,
                "project_description": 120,
                "skill_description": 30
            },
            5: {  # Executive
                "work_summary": 400,
                "work_highlight": 200,
                "education_summary": 300,
                "project_description": 350,
                "skill_description": 80
            }
        }
        return lengths.get(template_id, lengths[1])


class TemplateAwareQualityAssurance:
    """
    Template-aware quality assurance for AI-generated content
    """
    
    def __init__(self):
        self.parser = TemplateAwareOutputParser()
        self.validator = TemplateAwareContentValidator()
    
    def process_education_section(self, raw_output: str, template_id: int) -> Dict[str, Any]:
        """Process and validate education section with template awareness"""
        # Parse output with template-specific rules
        education = self.parser.parse_education_output(raw_output, template_id)
        
        if not education:
            return {
                "status": "failed",
                "error": f"Failed to parse education output for template {template_id}",
                "raw_output": raw_output
            }
        
        # Validate content with template-specific rules
        validation = self.validator.validate_education_content(education, template_id)
        
        return {
            "status": "success" if validation["is_valid"] else "warning",
            "parsed_content": education,
            "validation": validation,
            "raw_output": raw_output,
            "template_id": template_id
        }
    
    def process_work_section(self, raw_output: str, template_id: int) -> Dict[str, Any]:
        """Process and validate work experience section with template awareness"""
        # Parse output with template-specific rules
        work = self.parser.parse_work_output(raw_output, template_id)
        
        if not work:
            return {
                "status": "failed",
                "error": f"Failed to parse work experience output for template {template_id}",
                "raw_output": raw_output
            }
        
        # Validate content with template-specific rules
        validation = self.validator.validate_work_content(work, template_id)
        
        return {
            "status": "success" if validation["is_valid"] else "warning",
            "parsed_content": work,
            "validation": validation,
            "raw_output": raw_output,
            "template_id": template_id
        }
    
    def process_skills_section(self, raw_output: str, template_id: int) -> Dict[str, Any]:
        """Process and validate skills section with template awareness"""
        # Parse output with template-specific rules
        skills = self.parser.parse_skills_output(raw_output, template_id)
        
        if not skills:
            return {
                "status": "failed",
                "error": f"Failed to parse skills output for template {template_id}",
                "raw_output": raw_output
            }
        
        # Validate content with template-specific rules
        validation = self.validator.validate_skills_content(skills, template_id)
        
        return {
            "status": "success" if validation["is_valid"] else "warning",
            "parsed_content": skills,
            "validation": validation,
            "raw_output": raw_output,
            "template_id": template_id
        }
    
    def process_project_section(self, raw_output: str, template_id: int) -> Dict[str, Any]:
        """Process and validate project section with template awareness"""
        # Parse output with template-specific rules
        project = self.parser.parse_project_output(raw_output, template_id)
        
        if not project:
            return {
                "status": "failed",
                "error": f"Failed to parse project output for template {template_id}",
                "raw_output": raw_output
            }
        
        # Validate content with template-specific rules
        validation = self.validator.validate_project_content(project, template_id)
        
        return {
            "status": "success" if validation["is_valid"] else "warning",
            "parsed_content": project,
            "validation": validation,
            "raw_output": raw_output,
            "template_id": template_id
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
from typing import List, Dict, Any
from app.models.resume import TemplateInfo
from app.services.template_registry import TemplateRegistry, TemplateID

class TemplateService:
    """
    Service for managing resume templates.
    Now uses the scalable template registry with integer IDs.
    """
    
    def __init__(self):
        self.registry = TemplateRegistry()
        # Map theme names to available preview images
        self.preview_mapping = {
            "Macchiato": "macchiato_preview.png",
            "CV": "cv_preview.png",
            "Professional": "professional_preview.png",
            "Jacrys": "jacrys_preview.png"
        }
    
    def get_available_templates(self) -> List[TemplateInfo]:
        """Get list of available resume templates"""
        templates = []
        for theme in self.registry.get_all_themes():
            if theme.name not in self.preview_mapping:
                continue
            preview_file = self.preview_mapping.get(theme.name)
            templates.append(TemplateInfo(
                id=theme.id,
                name=theme.name,
                description=theme.description,
                preview_url=f"/static/templates/{preview_file}",
                theme_package=theme.npm_package,
                npm_package=theme.npm_package,
                version=theme.version,
                author=theme.author,
                category=theme.category
            ))
        return templates
    
    def get_template_by_id(self, template_id: int) -> TemplateInfo:
        """Get a specific template by ID"""
        theme = self.registry.get_theme(template_id)
        if not theme:
            raise ValueError(f"Template with ID '{template_id}' not found")
        
        preview_file = self.preview_mapping.get(theme.name, "professional_preview.png")
        return TemplateInfo(
            id=theme.id,
            name=theme.name,
            description=theme.description,
            preview_url=f"/static/templates/{preview_file}",
            theme_package=theme.npm_package,
            npm_package=theme.npm_package,
            version=theme.version,
            author=theme.author,
            category=theme.category
        )
    
    def get_template_style_guidelines(self, template_id: int) -> Dict[str, Any]:
        """Get style guidelines for a specific template"""
        theme = self.registry.get_theme(template_id)
        if not theme:
            return self._get_default_guidelines()
        
        # Get category-based guidelines
        category_guidelines = self.registry.get_category_guidelines(theme.category)
        
        return {
            "tone": category_guidelines.get("tone", "professional"),
            "font_family": category_guidelines.get("font_family", "Arial, sans-serif"),
            "color_scheme": category_guidelines.get("color_scheme", "black and white"),
            "spacing": category_guidelines.get("spacing", "standard"),
            "emphasis": category_guidelines.get("emphasis", "content over design"),
            "json_structure": "standard_json_resume",
            "theme_package": theme.npm_package,
            "category": theme.category
        }
    
    def get_template_json_structure(self, template_id: int, section_name: str) -> Dict[str, Any]:
        """Get template-specific JSON structure for a section"""
        theme = self.registry.get_theme(template_id)
        if not theme:
            return self._get_default_structure(section_name)
        
        # Get category-based field requirements
        field_requirements = self.registry.get_category_field_requirements(theme.category)
        
        if section_name == "work":
            return {
                "format": "standard",
                "fields": field_requirements.get("work", ["name", "position", "startDate", "endDate", "summary", "highlights"]),
                "example": {
                    "name": "Company Name",
                    "position": "Job Title", 
                    "startDate": "YYYY-MM",
                    "endDate": "YYYY-MM",
                    "summary": "Brief description",
                    "highlights": ["achievement 1", "achievement 2"]
                }
            }
        elif section_name == "education":
            return {
                "format": "standard",
                "fields": field_requirements.get("education", ["institution", "area", "studyType", "startDate", "endDate"]),
                "example": {
                    "institution": "University Name",
                    "area": "Field of Study",
                    "studyType": "Bachelor's",
                    "startDate": "YYYY",
                    "endDate": "YYYY"
                }
            }
        elif section_name == "skills":
            return {
                "format": "array",
                "fields": field_requirements.get("skills", ["name", "level", "keywords"]),
                "example": [{"name": "Skill Name", "level": "Expert/Proficient/Beginner", "keywords": ["related", "terms"]}]
            }
        elif section_name == "projects":
            return {
                "format": "standard",
                "fields": field_requirements.get("projects", ["name", "description", "highlights", "keywords", "startDate", "endDate"]),
                "example": {
                    "name": "Project Name",
                    "description": "Project description",
                    "highlights": ["achievement 1", "achievement 2"],
                    "keywords": ["technology", "framework"],
                    "startDate": "YYYY-MM",
                    "endDate": "YYYY-MM"
                }
            }
        
        return self._get_default_structure(section_name)
    
    def _get_default_guidelines(self) -> Dict[str, Any]:
        """Get default style guidelines"""
        return {
            "tone": "professional",
            "font_family": "Arial, sans-serif",
            "color_scheme": "black and white",
            "spacing": "standard",
            "emphasis": "content over design",
            "json_structure": "standard_json_resume"
        }
    
    def _get_default_structure(self, section_name: str) -> Dict[str, Any]:
        """Get default JSON structure for a section"""
        if section_name == "work":
            return {
                "format": "standard",
                "fields": ["name", "position", "startDate", "endDate", "summary", "highlights"],
                "example": {
                    "name": "Company Name",
                    "position": "Job Title",
                    "startDate": "YYYY-MM",
                    "endDate": "YYYY-MM",
                    "summary": "Brief description",
                    "highlights": ["achievement 1", "achievement 2"]
                }
            }
        elif section_name == "education":
            return {
                "format": "standard",
                "fields": ["institution", "area", "studyType", "startDate", "endDate"],
                "example": {
                    "institution": "University Name",
                    "area": "Field of Study",
                    "studyType": "Bachelor's",
                    "startDate": "YYYY",
                    "endDate": "YYYY"
                }
            }
        elif section_name == "skills":
            return {
                "format": "array",
                "fields": ["name", "level", "keywords"],
                "example": [{"name": "Skill Name", "level": "Expert/Proficient/Beginner", "keywords": ["related", "terms"]}]
            }
        elif section_name == "projects":
            return {
                "format": "standard",
                "fields": ["name", "description", "highlights", "keywords", "startDate", "endDate"],
                "example": {
                    "name": "Project Name",
                    "description": "Project description",
                    "highlights": ["achievement 1", "achievement 2"],
                    "keywords": ["technology", "framework"],
                    "startDate": "YYYY-MM",
                    "endDate": "YYYY-MM"
                }
            }
        
        return {} 
from typing import List, Dict, Any
from app.models.resume import TemplateInfo

class TemplateService:
    """
    Service for managing resume templates.
    For MVP, uses static template data. In production, this would connect to a database.
    """
    
    def __init__(self):
        self.templates = self._initialize_templates()
    
    def _initialize_templates(self) -> List[TemplateInfo]:
        """Initialize available resume templates using JSON Resume themes"""
        return [
            TemplateInfo(
                id="professional",
                name="Professional",
                description="Clean, traditional resume template suitable for corporate environments",
                preview_url="/static/templates/professional_preview.png",
                theme_package="jsonresume-theme-standard",
                category="professional"
            ),
            TemplateInfo(
                id="modern",
                name="Modern",
                description="Contemporary design with clean lines and modern typography",
                preview_url="/static/templates/modern_preview.png",
                theme_package="jsonresume-theme-even",
                category="modern"
            ),
            TemplateInfo(
                id="creative",
                name="Creative",
                description="Bold, creative template for design and creative industries",
                preview_url="/static/templates/creative_preview.png",
                theme_package="jsonresume-theme-kendall",
                category="creative"
            ),
            TemplateInfo(
                id="minimalist",
                name="Minimalist",
                description="Simple, clean template focusing on content over design",
                preview_url="/static/templates/minimalist_preview.png",
                theme_package="jsonresume-theme-tan-responsive",
                category="minimalist"
            ),
            TemplateInfo(
                id="executive",
                name="Executive",
                description="Sophisticated template for senior-level positions",
                preview_url="/static/templates/executive_preview.png",
                theme_package="jsonresume-theme-randytarampi",
                category="executive"
            )
        ]
    
    def get_available_templates(self) -> List[TemplateInfo]:
        """Get list of available resume templates"""
        return self.templates
    
    def get_template_by_id(self, template_id: str) -> TemplateInfo:
        """Get a specific template by ID"""
        for template in self.templates:
            if template.id == template_id:
                return template
        raise ValueError(f"Template with ID '{template_id}' not found")
    
    def get_template_style_guidelines(self, template_id: str) -> Dict[str, Any]:
        """Get style guidelines for a specific template"""
        guidelines = {
            "professional": {
                "tone": "formal",
                "font_family": "Arial, sans-serif",
                "color_scheme": "black and white",
                "spacing": "standard",
                "emphasis": "content over design"
            },
            "modern": {
                "tone": "contemporary",
                "font_family": "Helvetica, sans-serif",
                "color_scheme": "minimal colors",
                "spacing": "generous",
                "emphasis": "clean typography"
            },
            "creative": {
                "tone": "innovative",
                "font_family": "various",
                "color_scheme": "bold colors",
                "spacing": "dynamic",
                "emphasis": "visual impact"
            },
            "minimalist": {
                "tone": "simple",
                "font_family": "simple sans-serif",
                "color_scheme": "monochrome",
                "spacing": "minimal",
                "emphasis": "content only"
            },
            "executive": {
                "tone": "sophisticated",
                "font_family": "serif",
                "color_scheme": "professional",
                "spacing": "elegant",
                "emphasis": "authority and experience"
            }
        }
        
        return guidelines.get(template_id, guidelines["professional"]) 
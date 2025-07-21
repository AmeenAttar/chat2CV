#!/usr/bin/env python3
"""
Scalable Template Registry for JSON Resume Themes
Uses integer IDs and integrates with real JSON Resume themes
"""

import json
import os
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from enum import IntEnum

class TemplateID(IntEnum):
    """Integer-based template IDs for scalability - JSON Resume themes"""
    CLASSY = 1          # jsonresume-theme-classy
    ELEGANT = 2         # jsonresume-theme-elegant  
    KENDALL = 3         # jsonresume-theme-kendall
    CORA = 4            # jsonresume-theme-cora
    EVEN = 5            # jsonresume-theme-even
    LOWMESS = 6         # jsonresume-theme-lowmess
    WATERFALL = 7       # jsonresume-theme-waterfall
    STRAIGHTFORWARD = 8 # jsonresume-theme-straightforward
    SCEPTILE = 9        # jsonresume-theme-sceptile
    BUFFERBLOAT = 10    # jsonresume-theme-bufferbloat
    MODERN = 11         # jsonresume-theme-modern
    MSRESUME = 12       # jsonresume-theme-msresume
    PROJECTS = 13       # jsonresume-theme-projects
    UMENNEL = 14        # jsonresume-theme-umennel
    EVEN_CREWSHIN = 15  # jsonresume-theme-even-crewshin
    STACKOVERFLOW_RU = 16 # jsonresume-theme-stackoverflow-ru

@dataclass
class JSONResumeTheme:
    """Represents a real JSON Resume theme"""
    id: int
    name: str
    npm_package: str
    description: str
    category: str  # UI grouping only
    version: str
    author: str
    github_url: Optional[str] = None
    preview_url: Optional[str] = None
    
    # Template-specific requirements
    required_fields: Dict[str, List[str]] = None
    optional_fields: Dict[str, List[str]] = None
    length_constraints: Dict[str, int] = None
    style_guidelines: Dict[str, Any] = None

class TemplateRegistry:
    """
    Scalable template registry that integrates with real JSON Resume themes
    """
    
    def __init__(self):
        self.themes: Dict[int, JSONResumeTheme] = self._initialize_themes()
        self._load_theme_requirements()
    
    def _initialize_themes(self) -> Dict[int, JSONResumeTheme]:
        """Initialize with actual JSON Resume themes"""
        return {
            TemplateID.CLASSY: JSONResumeTheme(
                id=TemplateID.CLASSY,
                name="Classy",
                npm_package="jsonresume-theme-classy",
                description="An uber-classy JSONResume theme",
                category="professional",  # UI grouping only
                version="1.0.9",
                author="JaredCubilla",
                github_url="https://github.com/JaredCubilla/jsonresume-theme-classy"
            ),
            TemplateID.ELEGANT: JSONResumeTheme(
                id=TemplateID.ELEGANT,
                name="Elegant",
                npm_package="jsonresume-theme-elegant",
                description="Elegant theme for jsonresume",
                category="professional",
                version="1.0.0",
                author="jsonresume",
                github_url="https://github.com/jsonresume/jsonresume-theme-elegant"
            ),
            TemplateID.KENDALL: JSONResumeTheme(
                id=TemplateID.KENDALL,
                name="Kendall",
                npm_package="jsonresume-theme-kendall",
                description="A JSON Resume theme built with bootstrap",
                category="modern",
                version="1.0.0",
                author="jsonresume",
                github_url="https://github.com/jsonresume/jsonresume-theme-kendall"
            ),
            TemplateID.CORA: JSONResumeTheme(
                id=TemplateID.CORA,
                name="Cora",
                npm_package="jsonresume-theme-cora",
                description="An uber-classy JSONResume theme, that is print friendly too!",
                category="professional",
                version="0.1.1",
                author="lechuckcaptain",
                github_url="https://github.com/lechuckcaptain/jsonresume-theme-cora"
            ),
            TemplateID.EVEN: JSONResumeTheme(
                id=TemplateID.EVEN,
                name="Even",
                npm_package="jsonresume-theme-even",
                description="A flat JSON Resume theme, compatible with the latest resume schema",
                category="minimalist",
                version="0.23.0",
                author="jsonresume",
                github_url="https://github.com/jsonresume/jsonresume-theme-even"
            ),
            TemplateID.LOWMESS: JSONResumeTheme(
                id=TemplateID.LOWMESS,
                name="Lowmess",
                npm_package="jsonresume-theme-lowmess",
                description="JSONResume Theme create for Alec Lomas's Resume",
                category="creative",
                version="0.0.11",
                author="alecLomas",
                github_url="https://github.com/alecLomas/jsonresume-theme-lowmess"
            ),
            TemplateID.WATERFALL: JSONResumeTheme(
                id=TemplateID.WATERFALL,
                name="Waterfall",
                npm_package="jsonresume-theme-waterfall",
                description="Minimal jsonresume theme",
                category="minimalist",
                version="1.0.2",
                author="jsonresume",
                github_url="https://github.com/jsonresume/jsonresume-theme-waterfall"
            ),
            TemplateID.STRAIGHTFORWARD: JSONResumeTheme(
                id=TemplateID.STRAIGHTFORWARD,
                name="Straightforward",
                npm_package="jsonresume-theme-straightforward",
                description="a straightforward jsonresume theme",
                category="professional",
                version="0.2.0",
                author="jsonresume",
                github_url="https://github.com/jsonresume/jsonresume-theme-straightforward"
            ),
            TemplateID.SCEPTILE: JSONResumeTheme(
                id=TemplateID.SCEPTILE,
                name="Sceptile",
                npm_package="jsonresume-theme-sceptile",
                description="An uber-sceptile JSONResume theme",
                category="creative",
                version="1.0.5",
                author="jsonresume",
                github_url="https://github.com/jsonresume/jsonresume-theme-sceptile"
            ),
            TemplateID.BUFFERBLOAT: JSONResumeTheme(
                id=TemplateID.BUFFERBLOAT,
                name="Bufferbloat",
                npm_package="jsonresume-theme-bufferbloat",
                description="Buffer Bloat theme for JSON Resume",
                category="modern",
                version="1.0.2",
                author="jsonresume",
                github_url="https://github.com/jsonresume/jsonresume-theme-bufferbloat"
            ),
            TemplateID.MODERN: JSONResumeTheme(
                id=TemplateID.MODERN,
                name="Modern",
                npm_package="jsonresume-theme-modern",
                description="Basic modern theme",
                category="modern",
                version="0.0.18",
                author="jsonresume",
                github_url="https://github.com/jsonresume/jsonresume-theme-modern"
            ),
            TemplateID.MSRESUME: JSONResumeTheme(
                id=TemplateID.MSRESUME,
                name="MS Resume",
                npm_package="jsonresume-theme-msresume",
                description="JSONResume Theme based on Metalsmith Resume",
                category="professional",
                version="0.1.0",
                author="jsonresume",
                github_url="https://github.com/jsonresume/jsonresume-theme-msresume"
            ),
            TemplateID.PROJECTS: JSONResumeTheme(
                id=TemplateID.PROJECTS,
                name="Projects",
                npm_package="jsonresume-theme-projects",
                description="A flat JSON Resume theme based on jsonresume-theme-projects",
                category="modern",
                version="0.30.0",
                author="jsonresume",
                github_url="https://github.com/jsonresume/jsonresume-theme-projects"
            ),
            TemplateID.UMENNEL: JSONResumeTheme(
                id=TemplateID.UMENNEL,
                name="Umennel",
                npm_package="jsonresume-theme-umennel",
                description="Uche Mennel's jsonresume theme",
                category="creative",
                version="0.1.1",
                author="umennel",
                github_url="https://github.com/umennel/jsonresume-theme-umennel"
            ),
            TemplateID.EVEN_CREWSHIN: JSONResumeTheme(
                id=TemplateID.EVEN_CREWSHIN,
                name="Even Crewshin",
                npm_package="jsonresume-theme-even-crewshin",
                description="A flat JSON Resume theme based on jsonresume-theme-projects",
                category="minimalist",
                version="0.41.0",
                author="crewshin",
                github_url="https://github.com/crewshin/jsonresume-theme-even-crewshin"
            ),
            TemplateID.STACKOVERFLOW_RU: JSONResumeTheme(
                id=TemplateID.STACKOVERFLOW_RU,
                name="Stack Overflow RU",
                npm_package="jsonresume-theme-stackoverflow-ru",
                description="Translation of jsonresume-theme-stackoverflow into Russian",
                category="professional",
                version="3.4.1",
                author="jsonresume",
                github_url="https://github.com/jsonresume/jsonresume-theme-stackoverflow-ru"
            )
        }
    
    def _load_theme_requirements(self):
        """Load JSON Resume schema requirements for all themes"""
        # JSON Resume schema requirements - same for all themes
        json_resume_requirements = {
            "basics": {
                "required": ["name", "email"],
                "optional": ["label", "phone", "url", "summary", "location", "profiles"],
                "length_constraints": {
                    "name": 100,
                    "label": 100,
                    "email": 100,
                    "phone": 20,
                    "url": 200,
                    "summary": 500
                }
            },
            "work": {
                "required": ["name", "position", "startDate"],
                "optional": ["endDate", "summary", "highlights", "url", "location", "description"],
                "length_constraints": {
                    "name": 100,
                    "position": 100,
                    "summary": 500,
                    "highlights": 200,
                    "highlight_item": 150
                }
            },
            "education": {
                "required": ["institution", "area", "studyType"],
                "optional": ["startDate", "endDate", "score", "courses", "url"],
                "length_constraints": {
                    "institution": 100,
                    "area": 100,
                    "studyType": 50,
                    "score": 20
                }
            },
            "skills": {
                "required": ["name"],
                "optional": ["level", "keywords"],
                "length_constraints": {
                    "name": 50,
                    "level": 30,
                    "keywords": 10
                }
            },
            "projects": {
                "required": ["name", "description"],
                "optional": ["highlights", "keywords", "startDate", "endDate", "url", "roles", "entity", "type"],
                "length_constraints": {
                    "name": 100,
                    "description": 500,
                    "highlights": 200,
                    "highlight_item": 150
                }
            },
            "volunteer": {
                "required": ["organization", "position", "startDate"],
                "optional": ["endDate", "summary", "url", "highlights"],
                "length_constraints": {
                    "organization": 100,
                    "position": 100,
                    "summary": 500,
                    "highlights": 200
                }
            },
            "awards": {
                "required": ["title", "date", "awarder"],
                "optional": ["summary"],
                "length_constraints": {
                    "title": 100,
                    "awarder": 100,
                    "summary": 300
                }
            },
            "certificates": {
                "required": ["name", "date", "issuer"],
                "optional": ["url"],
                "length_constraints": {
                    "name": 100,
                    "issuer": 100
                }
            },
            "publications": {
                "required": ["name", "publisher", "releaseDate"],
                "optional": ["url", "summary"],
                "length_constraints": {
                    "name": 150,
                    "publisher": 100,
                    "summary": 500
                }
            },
            "languages": {
                "required": ["language", "fluency"],
                "optional": [],
                "length_constraints": {
                    "language": 50,
                    "fluency": 30
                }
            },
            "interests": {
                "required": ["name"],
                "optional": ["keywords"],
                "length_constraints": {
                    "name": 100,
                    "keywords": 10
                }
            },
            "references": {
                "required": ["name", "reference"],
                "optional": [],
                "length_constraints": {
                    "name": 100,
                    "reference": 500
                }
            }
        }
        
        # Apply JSON Resume requirements to all themes
        for theme in self.themes.values():
            theme.required_fields = json_resume_requirements
            theme.optional_fields = json_resume_requirements
            theme.length_constraints = json_resume_requirements
    
    def get_theme(self, theme_id: int) -> Optional[JSONResumeTheme]:
        """Get theme by integer ID"""
        return self.themes.get(theme_id)
    
    def get_all_themes(self) -> List[JSONResumeTheme]:
        """Get all available themes"""
        return list(self.themes.values())
    
    def get_themes_by_category(self, category: str) -> List[JSONResumeTheme]:
        """Get themes by category"""
        return [theme for theme in self.themes.values() if theme.category == category]
    
    def get_theme_requirements(self, theme_id: int, section: str) -> Dict[str, Any]:
        """Get theme-specific requirements for a section"""
        theme = self.get_theme(theme_id)
        if not theme or not theme.required_fields:
            return {}
        
        return theme.required_fields.get(section, {})
    
    def get_required_fields(self, theme_id: int, section: str) -> List[str]:
        """Get required fields for a theme and section"""
        requirements = self.get_theme_requirements(theme_id, section)
        return requirements.get("required", [])
    
    def get_optional_fields(self, theme_id: int, section: str) -> List[str]:
        """Get optional fields for a theme and section"""
        requirements = self.get_theme_requirements(theme_id, section)
        return requirements.get("optional", [])
    
    def get_length_constraints(self, theme_id: int, section: str) -> Dict[str, int]:
        """Get length constraints for a theme and section"""
        requirements = self.get_theme_requirements(theme_id, section)
        return requirements.get("length_constraints", {})
    
    def validate_field_requirements(self, theme_id: int, section: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate that data meets theme requirements"""
        required_fields = self.get_required_fields(theme_id, section)
        optional_fields = self.get_optional_fields(theme_id, section)
        length_constraints = self.get_length_constraints(theme_id, section)
        
        issues = []
        warnings = []
        
        # Check required fields
        for field in required_fields:
            if field not in data or not data[field]:
                issues.append(f"Missing required field: {field}")
        
        # Check length constraints
        for field, max_length in length_constraints.items():
            if field in data and data[field]:
                if isinstance(data[field], str) and len(data[field]) > max_length:
                    warnings.append(f"Field '{field}' exceeds maximum length ({max_length} characters)")
                elif isinstance(data[field], list):
                    for i, item in enumerate(data[field]):
                        if isinstance(item, str) and len(item) > max_length:
                            warnings.append(f"Item {i+1} in '{field}' exceeds maximum length ({max_length} characters)")
        
        return {
            "is_valid": len(issues) == 0,
            "issues": issues,
            "warnings": warnings,
            "required_fields": required_fields,
            "optional_fields": optional_fields,
            "length_constraints": length_constraints
        }
    
    def add_theme(self, theme: JSONResumeTheme) -> bool:
        """Add a new theme to the registry"""
        if theme.id in self.themes:
            return False
        
        self.themes[theme.id] = theme
        return True
    
    def remove_theme(self, theme_id: int) -> bool:
        """Remove a theme from the registry"""
        if theme_id not in self.themes:
            return False
        
        del self.themes[theme_id]
        return True
    
    def update_theme(self, theme: JSONResumeTheme) -> bool:
        """Update an existing theme"""
        if theme.id not in self.themes:
            return False
        
        self.themes[theme.id] = theme
        return True
    
    def get_theme_statistics(self) -> Dict[str, Any]:
        """Get statistics about available themes"""
        total_themes = len(self.themes)
        categories = {}
        
        for theme in self.themes.values():
            if theme.category not in categories:
                categories[theme.category] = 0
            categories[theme.category] += 1
        
        return {
            "total_themes": total_themes,
            "categories": categories,
            "categories_count": len(categories)
        }
    
    def get_category_guidelines(self, category: str) -> Dict[str, Any]:
        """Get style guidelines for a category"""
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
        
        return guidelines.get(category, guidelines["professional"])
    
    def get_category_field_requirements(self, category: str) -> Dict[str, List[str]]:
        """Get field requirements for a category"""
        requirements = {
            "professional": {
                "work": ["name", "position", "startDate", "endDate", "summary", "highlights"],
                "education": ["institution", "area", "studyType", "startDate", "endDate"],
                "skills": ["name", "level", "keywords"],
                "projects": ["name", "description", "highlights", "keywords", "startDate", "endDate"]
            },
            "modern": {
                "work": ["name", "position", "startDate", "endDate", "summary", "highlights"],
                "education": ["institution", "area", "studyType", "startDate", "endDate"],
                "skills": ["name", "level", "keywords"],
                "projects": ["name", "description", "highlights", "keywords", "startDate", "endDate"]
            },
            "creative": {
                "work": ["name", "position", "startDate", "endDate", "summary", "highlights"],
                "education": ["institution", "area", "studyType", "startDate", "endDate"],
                "skills": ["name", "level", "keywords"],
                "projects": ["name", "description", "highlights", "keywords", "startDate", "endDate"]
            },
            "minimalist": {
                "work": ["name", "position", "startDate", "endDate", "summary"],
                "education": ["institution", "area", "studyType", "endDate"],
                "skills": ["name"],
                "projects": ["name", "description"]
            },
            "executive": {
                "work": ["name", "position", "startDate", "endDate", "summary", "highlights", "achievements"],
                "education": ["institution", "area", "studyType", "startDate", "endDate", "gpa"],
                "skills": ["name", "level", "years_experience", "keywords"],
                "projects": ["name", "description", "highlights", "keywords", "startDate", "endDate", "budget"]
            }
        }
        
        return requirements.get(category, requirements["professional"]) 
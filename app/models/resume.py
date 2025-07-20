from pydantic import BaseModel, Field
from typing import Dict, List, Optional, Any
from enum import Enum

class SectionStatus(str, Enum):
    NOT_STARTED = "not_started"
    INCOMPLETE = "incomplete"
    PARTIAL = "partial"
    COMPLETE = "complete"

class ResumeSection(BaseModel):
    """Represents a section of a resume"""
    name: str
    content: List[str] = Field(default_factory=list)
    status: SectionStatus = SectionStatus.NOT_STARTED
    last_updated: Optional[str] = None

class ResumeCompletenessSummary(BaseModel):
    """Summary of resume completion status"""
    personal_details: SectionStatus = SectionStatus.NOT_STARTED
    work_experience: SectionStatus = SectionStatus.NOT_STARTED
    education: SectionStatus = SectionStatus.NOT_STARTED
    skills: SectionStatus = SectionStatus.NOT_STARTED
    projects: SectionStatus = SectionStatus.NOT_STARTED
    certifications: SectionStatus = SectionStatus.NOT_STARTED
    languages: SectionStatus = SectionStatus.NOT_STARTED
    interests: SectionStatus = SectionStatus.NOT_STARTED

class ResumeData(BaseModel):
    """Complete resume data structure"""
    user_id: str
    template_id: str
    sections: Dict[str, ResumeSection] = Field(default_factory=dict)
    completeness_summary: ResumeCompletenessSummary = Field(default_factory=ResumeCompletenessSummary)
    created_at: Optional[str] = None
    updated_at: Optional[str] = None

class TemplateStyle(BaseModel):
    """Template style guidelines"""
    template_id: str
    name: str
    tone: str  # e.g., "professional", "modern", "creative"
    formatting_rules: Dict[str, Any]
    action_verbs: List[str]
    keywords: List[str]
    examples: List[str]

class TemplateInfo(BaseModel):
    """Template information for the catalog"""
    id: str
    name: str
    description: str
    preview_url: Optional[str] = None

class GenerateResumeSectionResult(BaseModel):
    """Result from AI agent generating resume section"""
    status: str
    updated_section: str
    rephrased_content: str
    resume_completeness_summary: ResumeCompletenessSummary 
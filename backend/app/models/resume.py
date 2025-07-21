from pydantic import BaseModel, Field
from typing import Dict, List, Optional, Any
from enum import Enum

class SectionStatus(str, Enum):
    NOT_STARTED = "not_started"
    INCOMPLETE = "incomplete"
    PARTIAL = "partial"
    COMPLETE = "complete"

# JSON Resume Schema Models
class Location(BaseModel):
    address: Optional[str] = None
    postalCode: Optional[str] = None
    city: Optional[str] = None
    countryCode: Optional[str] = None
    region: Optional[str] = None

class Profile(BaseModel):
    network: str
    username: str
    url: Optional[str] = None

class Basics(BaseModel):
    name: Optional[str] = None
    label: Optional[str] = None
    image: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    url: Optional[str] = None
    summary: Optional[str] = None
    location: Optional[Location] = None
    profiles: Optional[List[Profile]] = None

class WorkExperience(BaseModel):
    name: str
    position: str
    url: Optional[str] = None
    startDate: Optional[str] = None
    endDate: Optional[str] = None
    summary: Optional[str] = None
    highlights: Optional[List[str]] = None
    location: Optional[str] = None
    description: Optional[str] = None

class Education(BaseModel):
    institution: str
    url: Optional[str] = None
    area: Optional[str] = None
    studyType: Optional[str] = None
    startDate: Optional[str] = None
    endDate: Optional[str] = None
    score: Optional[str] = None
    courses: Optional[List[str]] = None

class Skill(BaseModel):
    name: str
    level: Optional[str] = None
    keywords: Optional[List[str]] = None

class Language(BaseModel):
    language: str
    fluency: Optional[str] = None

class Interest(BaseModel):
    name: str
    keywords: Optional[List[str]] = None

class Project(BaseModel):
    name: str
    description: Optional[str] = None
    highlights: Optional[List[str]] = None
    keywords: Optional[List[str]] = None
    startDate: Optional[str] = None
    endDate: Optional[str] = None
    url: Optional[str] = None
    roles: Optional[List[str]] = None
    entity: Optional[str] = None
    type: Optional[str] = None

class Award(BaseModel):
    title: str
    date: Optional[str] = None
    awarder: Optional[str] = None
    summary: Optional[str] = None

class Publication(BaseModel):
    name: str
    publisher: Optional[str] = None
    releaseDate: Optional[str] = None
    url: Optional[str] = None
    summary: Optional[str] = None

class Volunteer(BaseModel):
    organization: str
    position: str
    url: Optional[str] = None
    startDate: Optional[str] = None
    endDate: Optional[str] = None
    summary: Optional[str] = None
    highlights: Optional[List[str]] = None

class Reference(BaseModel):
    name: str
    reference: str

class Meta(BaseModel):
    canonical: Optional[str] = None
    version: Optional[str] = None
    lastModified: Optional[str] = None

class JSONResume(BaseModel):
    """JSON Resume format - the standard for resume data"""
    schema: Optional[str] = "https://raw.githubusercontent.com/jsonresume/resume-schema/v1.0.0/schema.json"
    basics: Optional[Basics] = None
    work: Optional[List[WorkExperience]] = None
    volunteer: Optional[List[Volunteer]] = None
    education: Optional[List[Education]] = None
    awards: Optional[List[Award]] = None
    publications: Optional[List[Publication]] = None
    skills: Optional[List[Skill]] = None
    languages: Optional[List[Language]] = None
    interests: Optional[List[Interest]] = None
    references: Optional[List[Reference]] = None
    projects: Optional[List[Project]] = None
    meta: Optional[Meta] = None

class ResumeSection(BaseModel):
    """Represents a section of a resume"""
    name: str
    content: List[str] = Field(default_factory=list)
    status: SectionStatus = SectionStatus.NOT_STARTED
    last_updated: Optional[str] = None

class ResumeCompletenessSummary(BaseModel):
    """Smart completeness summary for Voiceflow conversational guidance"""
    # Section completion status - using JSON Resume standard names
    basics: SectionStatus = SectionStatus.NOT_STARTED
    work: SectionStatus = SectionStatus.NOT_STARTED
    education: SectionStatus = SectionStatus.NOT_STARTED
    skills: SectionStatus = SectionStatus.NOT_STARTED
    projects: SectionStatus = SectionStatus.NOT_STARTED
    awards: SectionStatus = SectionStatus.NOT_STARTED
    languages: SectionStatus = SectionStatus.NOT_STARTED
    interests: SectionStatus = SectionStatus.NOT_STARTED
    volunteer: SectionStatus = SectionStatus.NOT_STARTED
    publications: SectionStatus = SectionStatus.NOT_STARTED
    references: SectionStatus = SectionStatus.NOT_STARTED
    
    # Smart conversational guidance for Voiceflow
    conversation_context: Dict[str, Any] = Field(default_factory=dict)
    suggested_topics: List[str] = Field(default_factory=list)
    missing_critical_info: List[str] = Field(default_factory=list)
    conversation_flow_hints: List[str] = Field(default_factory=list)
    user_progress_insights: Dict[str, Any] = Field(default_factory=dict)

class ResumeData(BaseModel):
    """Complete resume data structure"""
    user_id: str
    template_id: int
    json_resume: JSONResume = Field(default_factory=JSONResume)
    sections: Dict[str, ResumeSection] = Field(default_factory=dict)
    completeness_summary: ResumeCompletenessSummary = Field(default_factory=ResumeCompletenessSummary)
    created_at: Optional[str] = None
    updated_at: Optional[str] = None

class TemplateInfo(BaseModel):
    """Template information for the catalog"""
    id: int
    name: str
    description: str
    preview_url: Optional[str] = None
    theme_package: Optional[str] = None  # npm package name for the theme
    npm_package: Optional[str] = None  # npm package name for the theme
    version: Optional[str] = None
    author: Optional[str] = None
    category: Optional[str] = None  # professional, creative, modern, etc.

class TemplateStyle(BaseModel):
    """Template style guidelines"""
    template_id: int
    name: str
    tone: str  # e.g., "professional", "modern", "creative"
    formatting_rules: Dict[str, Any]
    action_verbs: List[str]
    keywords: List[str]
    examples: List[str]

class GenerateResumeSectionResult(BaseModel):
    """Result from AI agent generating resume section"""
    status: str
    updated_section: str
    rephrased_content: str
    resume_completeness_summary: ResumeCompletenessSummary
    resume_data: Optional[ResumeData] = None 
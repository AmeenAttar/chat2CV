from sqlalchemy import Column, Integer, String, Text, DateTime, JSON, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base
from datetime import datetime
from typing import Optional, Dict, Any

class User(Base):
    """User model for authentication and user management"""
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    name = Column(String(255), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    resumes = relationship("Resume", back_populates="user", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<User(id={self.id}, email='{self.email}', name='{self.name}')>"

class Resume(Base):
    """Resume model for storing complete resume data"""
    __tablename__ = "resumes"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    template_id = Column(Integer, nullable=False)  # JSON Resume theme ID
    title = Column(String(255), nullable=True)  # User-defined resume title
    json_resume_data = Column(JSON, nullable=False)  # Complete JSON Resume structure
    schema_version = Column(String(50), default="v1.0.0")  # Track schema version
    is_complete = Column(Boolean, default=False)
    is_paid = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    user = relationship("User", back_populates="resumes")
    sections = relationship("ResumeSection", back_populates="resume", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Resume(id={self.id}, user_id={self.user_id}, template_id='{self.template_id}', title='{self.title}')>"

class ResumeSection(Base):
    """Individual resume section model for tracking section-level data"""
    __tablename__ = "resume_sections"
    
    id = Column(Integer, primary_key=True, index=True)
    resume_id = Column(Integer, ForeignKey("resumes.id"), nullable=False)
    section_name = Column(String(100), nullable=False)  # e.g., "work_experience", "education", "skills"
    original_input = Column(Text, nullable=True)  # Raw user input from Voiceflow
    processed_content = Column(JSON, nullable=True)  # AI-processed content
    status = Column(String(50), default="pending")  # pending, processing, completed, failed
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    resume = relationship("Resume", back_populates="sections")
    
    def __repr__(self):
        return f"<ResumeSection(id={self.id}, resume_id={self.resume_id}, section_name='{self.section_name}', status='{self.status}')>"

class Template(Base):
    """Template model for storing template metadata"""
    __tablename__ = "templates"
    
    id = Column(Integer, primary_key=True, index=True)
    template_id = Column(Integer, unique=True, nullable=False)  # e.g., 1, 2, 3, 4, 5
    name = Column(String(255), nullable=False)  # Display name
    description = Column(Text, nullable=True)
    category = Column(String(100), nullable=True)  # e.g., "professional", "creative", "minimalist"
    preview_url = Column(String(500), nullable=True)  # URL to preview image
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    def __repr__(self):
        return f"<Template(id={self.id}, template_id='{self.template_id}', name='{self.name}')>"

class UserSession(Base):
    """User session model for tracking active sessions"""
    __tablename__ = "user_sessions"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    resume_id = Column(Integer, ForeignKey("resumes.id"), nullable=False)  # Added resume_id
    session_token = Column(String(255), unique=True, nullable=False)
    expires_at = Column(DateTime(timezone=True), nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    def __repr__(self):
        return f"<UserSession(id={self.id}, user_id={self.user_id}, resume_id={self.resume_id}, expires_at='{self.expires_at}')>"

# Pydantic models for API requests/responses
from pydantic import BaseModel, EmailStr
from typing import Optional, List, Dict, Any
from datetime import datetime

class UserCreate(BaseModel):
    email: EmailStr
    name: Optional[str] = None

class UserResponse(BaseModel):
    id: int
    email: str
    name: Optional[str] = None
    is_active: bool
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

class ResumeCreate(BaseModel):
    template_id: str
    title: Optional[str] = None

class ResumeUpdate(BaseModel):
    title: Optional[str] = None
    json_resume_data: Optional[Dict[str, Any]] = None
    is_complete: Optional[bool] = None

class ResumeResponse(BaseModel):
    id: int
    user_id: int
    template_id: str
    title: Optional[str] = None
    json_resume_data: Dict[str, Any]
    schema_version: str = "v1.0.0"
    is_complete: bool
    is_paid: bool
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

class ResumeSectionCreate(BaseModel):
    section_name: str
    original_input: Optional[str] = None

class ResumeSectionUpdate(BaseModel):
    original_input: Optional[str] = None
    processed_content: Optional[Dict[str, Any]] = None
    status: Optional[str] = None

class ResumeSectionResponse(BaseModel):
    id: int
    resume_id: int
    section_name: str
    original_input: Optional[str] = None
    processed_content: Optional[Dict[str, Any]] = None
    status: str
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

class TemplateResponse(BaseModel):
    id: int
    template_id: str
    name: str
    description: Optional[str] = None
    category: Optional[str] = None
    preview_url: Optional[str] = None
    is_active: bool
    
    class Config:
        from_attributes = True 
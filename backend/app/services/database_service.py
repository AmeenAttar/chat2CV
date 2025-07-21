from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta, timezone
import uuid

from app.models.database_models import (
    User, Resume, ResumeSection, Template, UserSession,
    UserCreate, ResumeCreate, ResumeUpdate, ResumeSectionCreate, ResumeSectionUpdate
)
from app.models.resume import ResumeData, JSONResume

class DatabaseService:
    """Service class for handling all database operations"""
    
    def __init__(self, db: Session):
        self.db = db
    
    # User operations
    def create_user(self, user_data: UserCreate = None, email: str = None, name: str = None) -> User:
        """Create a new user"""
        if user_data:
            db_user = User(
                email=user_data.email,
                name=user_data.name
            )
        else:
            db_user = User(
                email=email,
                name=name
            )
        self.db.add(db_user)
        self.db.commit()
        self.db.refresh(db_user)
        return db_user
    
    def get_user_by_id(self, user_id: int) -> Optional[User]:
        """Get user by ID"""
        return self.db.query(User).filter(User.id == user_id).first()
    
    def get_user_by_email(self, email: str) -> Optional[User]:
        """Get user by email"""
        return self.db.query(User).filter(User.email == email).first()
    
    def update_user(self, user_id: int, **kwargs) -> Optional[User]:
        """Update user information"""
        user = self.get_user_by_id(user_id)
        if user:
            for key, value in kwargs.items():
                if hasattr(user, key):
                    setattr(user, key, value)
            user.updated_at = datetime.utcnow()
            self.db.commit()
            self.db.refresh(user)
        return user
    
    # Resume operations
    def create_resume(self, user_id: int, template_id: int, title: Optional[str] = None) -> Resume:
        """Create a new resume for a user"""
        # Initialize empty JSON Resume structure
        json_resume_data = {
            "basics": {
                "name": "",
                "label": "",
                "image": "",
                "email": "",
                "phone": "",
                "url": "",
                "summary": "",
                "location": {
                    "address": "",
                    "postalCode": "",
                    "city": "",
                    "countryCode": "",
                    "region": ""
                },
                "profiles": []
            },
            "work": [],
            "volunteer": [],
            "education": [],
            "awards": [],
            "certificates": [],
            "publications": [],
            "skills": [],
            "languages": [],
            "interests": [],
            "references": [],
            "projects": [],
            "meta": {
                "theme": template_id
            }
        }
        
        # Create default completeness summary
        completeness_summary = {
            "basics": "not_started",
            "work": "not_started",
            "education": "not_started",
            "skills": "not_started",
            "projects": "not_started",
            "awards": "not_started",
            "languages": "not_started",
            "interests": "not_started",
            "volunteer": "not_started",
            "publications": "not_started",
            "references": "not_started"
        }
        
        db_resume = Resume(
            user_id=user_id,
            template_id=template_id,
            title=title or f"Resume - Template {template_id}",
            json_resume_data=json_resume_data,
            schema_version="v1.0.0",
            completeness_summary=completeness_summary
        )
        
        self.db.add(db_resume)
        self.db.commit()
        self.db.refresh(db_resume)
        return db_resume
    
    def get_resume_by_id(self, resume_id: int) -> Optional[Resume]:
        """Get resume by ID"""
        return self.db.query(Resume).filter(Resume.id == resume_id).first()
    
    def get_user_resumes(self, user_id: int) -> List[Resume]:
        """Get all resumes for a user"""
        return self.db.query(Resume).filter(Resume.user_id == user_id).all()
    
    def update_resume(self, resume_id: int, **kwargs) -> Optional[Resume]:
        """Update resume information"""
        resume = self.get_resume_by_id(resume_id)
        if resume:
            for key, value in kwargs.items():
                if hasattr(resume, key):
                    setattr(resume, key, value)
            resume.updated_at = datetime.utcnow()
            self.db.commit()
            self.db.refresh(resume)
        return resume
    
    def delete_resume(self, resume_id: int) -> bool:
        """Delete a resume"""
        resume = self.get_resume_by_id(resume_id)
        if resume:
            self.db.delete(resume)
            self.db.commit()
            return True
        return False
    
    # Resume section operations
    def create_resume_section(self, resume_id: int, section_name: str, original_input: Optional[str] = None) -> ResumeSection:
        """Create a new resume section"""
        db_section = ResumeSection(
            resume_id=resume_id,
            section_name=section_name,
            original_input=original_input,
            status="pending"
        )
        self.db.add(db_section)
        self.db.commit()
        self.db.refresh(db_section)
        return db_section
    
    def get_resume_section(self, section_id: int) -> Optional[ResumeSection]:
        """Get resume section by ID"""
        return self.db.query(ResumeSection).filter(ResumeSection.id == section_id).first()
    
    def get_resume_sections(self, resume_id: int) -> List[ResumeSection]:
        """Get all sections for a resume"""
        return self.db.query(ResumeSection).filter(ResumeSection.resume_id == resume_id).all()
    
    def get_resume_section_by_name(self, resume_id: int, section_name: str) -> Optional[ResumeSection]:
        """Get resume section by name"""
        return self.db.query(ResumeSection).filter(
            and_(ResumeSection.resume_id == resume_id, ResumeSection.section_name == section_name)
        ).first()
    
    def update_resume_section(self, section_id: int, **kwargs) -> Optional[ResumeSection]:
        """Update resume section"""
        section = self.get_resume_section(section_id)
        if section:
            for key, value in kwargs.items():
                if hasattr(section, key):
                    setattr(section, key, value)
            section.updated_at = datetime.utcnow()
            self.db.commit()
            self.db.refresh(section)
        return section
    
    def update_resume_section_by_name(self, resume_id: int, section_name: str, **kwargs) -> Optional[ResumeSection]:
        """Update resume section by name"""
        section = self.get_resume_section_by_name(resume_id, section_name)
        if section:
            return self.update_resume_section(section.id, **kwargs)
        return None
    
    def save_resume_section(self, resume_id: int, section_name: str, original_input: str, processed_content: Dict[str, Any]) -> ResumeSection:
        """Save or update a resume section"""
        # Check if section already exists
        existing_section = self.get_resume_section_by_name(resume_id, section_name)
        
        if existing_section:
            # Update existing section
            return self.update_resume_section(
                existing_section.id,
                original_input=original_input,
                processed_content=processed_content,
                status="completed"
            )
        else:
            # Create new section
            return self.create_resume_section(
                resume_id=resume_id,
                section_name=section_name,
                original_input=original_input
            )
    
    def update_resume_data(self, resume_id: int, json_resume_data: Dict[str, Any], completeness_summary: Dict[str, Any]) -> bool:
        """Update resume data and completeness summary"""
        resume = self.get_resume_by_id(resume_id)
        if resume:
            resume.json_resume_data = json_resume_data
            resume.completeness_summary = completeness_summary
            resume.updated_at = datetime.utcnow()
            self.db.commit()
            return True
        return False
    
    # Template operations
    def create_template(self, template_id: int, name: str, description: Optional[str] = None, 
                       category: Optional[str] = None, preview_url: Optional[str] = None) -> Template:
        """Create a new template"""
        db_template = Template(
            template_id=template_id,
            name=name,
            description=description,
            category=category,
            preview_url=preview_url
        )
        self.db.add(db_template)
        self.db.commit()
        self.db.refresh(db_template)
        return db_template
    
    def get_template_by_id(self, template_id: int) -> Optional[Template]:
        """Get template by ID"""
        return self.db.query(Template).filter(Template.template_id == template_id).first()
    
    def get_all_templates(self) -> List[Template]:
        """Get all active templates"""
        return self.db.query(Template).filter(Template.is_active == True).all()
    
    # Session operations
    def create_user_session(self, user_id: int, resume_id: int, expires_in_hours: int = 24) -> UserSession:
        """Create a new user session"""
        session_token = str(uuid.uuid4())
        expires_at = datetime.utcnow().replace(tzinfo=timezone.utc) + timedelta(hours=expires_in_hours)
        
        session = UserSession(
            user_id=user_id,
            resume_id=resume_id,
            session_token=session_token,
            expires_at=expires_at
        )
        self.db.add(session)
        self.db.commit()
        self.db.refresh(session)
        return session

    def create_user_session_with_id(self, user_id: int, resume_id: int, session_id: str, expires_at: datetime) -> UserSession:
        """Create a new user session with a specific session ID"""
        # Ensure expires_at is timezone-aware
        if expires_at.tzinfo is None:
            expires_at = expires_at.replace(tzinfo=timezone.utc)
        
        session = UserSession(
            user_id=user_id,
            resume_id=resume_id,
            session_token=session_id,
            expires_at=expires_at
        )
        self.db.add(session)
        self.db.commit()
        self.db.refresh(session)
        return session

    def get_session_by_id(self, session_id: str) -> Optional[UserSession]:
        """Get session by session ID"""
        return self.db.query(UserSession).filter(UserSession.session_token == session_id).first()

    def get_session_by_token(self, session_token: str) -> Optional[UserSession]:
        """Get session by token"""
        return self.db.query(UserSession).filter(UserSession.session_token == session_token).first()

    def deactivate_session(self, session_token: str) -> bool:
        """Deactivate a session"""
        session = self.get_session_by_token(session_token)
        if session:
            session.is_active = False
            session.updated_at = datetime.utcnow()
            self.db.commit()
            return True
        return False
    
    # Resume data conversion
    def resume_to_resume_data(self, resume: Resume) -> ResumeData:
        """Convert database Resume to ResumeData model"""
        return ResumeData(
            user_id=str(resume.user_id),
            template_id=resume.template_id,
            json_resume=JSONResume(**resume.json_resume_data),
            completeness_summary=resume.completeness_summary or {}
        )
    
    def resume_data_to_resume(self, resume_data: ResumeData, user_id: int) -> Resume:
        """Convert ResumeData to database Resume model"""
        return Resume(
            user_id=user_id,
            template_id=resume_data.template_id,
            json_resume_data=resume_data.json_resume.dict(),
            completeness_summary=resume_data.completeness_summary
        )
    
    # Utility methods
    def update_resume_completeness(self, resume_id: int, section_name: str, status: str) -> bool:
        """Update the completeness summary for a resume section"""
        resume = self.get_resume_by_id(resume_id)
        if resume and resume.completeness_summary:
            resume.completeness_summary[section_name] = status
            resume.updated_at = datetime.utcnow()
            self.db.commit()
            return True
        return False
    
    def get_resume_with_sections(self, resume_id: int) -> Optional[Resume]:
        """Get resume with all its sections"""
        return self.db.query(Resume).filter(Resume.id == resume_id).first()
    
    def cleanup_expired_sessions(self) -> int:
        """Clean up expired sessions"""
        expired_sessions = self.db.query(UserSession).filter(
            UserSession.expires_at < datetime.utcnow()
        ).all()
        
        count = len(expired_sessions)
        for session in expired_sessions:
            self.db.delete(session)
        
        self.db.commit()
        return count 
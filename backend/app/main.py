from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect, Depends, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, validator
from typing import Dict, List, Optional, Any
import json
import os
import time
from dotenv import load_dotenv
load_dotenv()
from datetime import datetime, timedelta, timezone
import uuid
import re
import traceback
import logging
logging.basicConfig(level=logging.DEBUG, force=True)

from app.services.simple_ai_agent import SimpleResumeAgent
from app.services.template_service import TemplateService
from app.services.resume_renderer import ResumeRenderer
from app.services.database_service import DatabaseService
from app.services.schema_validator import JSONResumeValidator
from app.services.completeness_analyzer import CompletenessAnalyzer, QualityChecklistGenerator
from app.services.section_classifier import llm_infer_section_from_input
from app.models.resume import ResumeSection, ResumeData, GenerateResumeResponse
from app.database import get_db, init_db
from sqlalchemy.ext.asyncio import AsyncSession
from app.services.error_handler import error_handler

# Load environment variables
# load_dotenv('../.env') # This line is now redundant as load_dotenv() is called at the top

# Recursively promote top-level JSON Resume fields from nested dicts to the top level

def promote_sections_to_top_level(data, top_fields=None):
    """Recursively promote top-level JSON Resume fields from nested dicts to the top level."""
    if top_fields is None:
        top_fields = [
            "work", "education", "skills", "projects", "awards", "languages", "interests", "volunteer", "publications", "references"
        ]
    def _promote(d, root):
        if not isinstance(d, dict):
            return
        for field in top_fields:
            if field in d and d[field]:
                if (field not in root) or (not root[field]):
                    root[field] = d[field]
        for v in d.values():
            if isinstance(v, dict):
                _promote(v, root)
    _promote(data, data)
    return data

def clean_null_values(data: Any) -> Any:
    """Remove null values from data to comply with JSON Resume schema"""
    if isinstance(data, dict):
        cleaned = {}
        for key, value in data.items():
            if value is not None:
                cleaned[key] = clean_null_values(value)
        return cleaned
    elif isinstance(data, list):
        return [clean_null_values(item) for item in data if item is not None]
    else:
        return data

def infer_section_from_input(raw_input: str, current_resume_data: Optional[dict] = None) -> str:
    """Infer the most likely section from user input using simple heuristics. Extend with LLM if needed."""
    text = raw_input.lower()
    # Simple keyword-based heuristics
    if any(word in text for word in ["work", "job", "company", "position", "employer", "manager", "engineer", "developer", "analyst", "designer", "consultant", "intern", "experience", "role"]):
        return "work"
    if any(word in text for word in ["study", "university", "college", "school", "degree", "bachelor", "master", "phd", "gpa", "education", "course", "graduated"]):
        return "education"
    if any(word in text for word in ["skill", "proficient", "expertise", "languages", "tools", "framework", "technology", "competency"]):
        return "skills"
    if any(word in text for word in ["project", "built", "created", "developed", "launched", "side project", "portfolio"]):
        return "projects"
    if any(word in text for word in ["award", "honor", "prize", "recognition", "achievement"]):
        return "awards"
    if any(word in text for word in ["language", "fluent", "bilingual", "multilingual", "native speaker"]):
        return "languages"
    if any(word in text for word in ["interest", "hobby", "passion", "enjoy", "like to"]):
        return "interests"
    if any(word in text for word in ["volunteer", "volunteering", "nonprofit", "charity", "community service"]):
        return "volunteer"
    if any(word in text for word in ["publication", "published", "paper", "article", "journal"]):
        return "publications"
    if any(word in text for word in ["reference", "referee", "recommendation"]):
        return "references"
    # Default to basics if nothing else matches
    return "basics"

app = FastAPI(
    title="Chat-to-CV Backend",
    description="Backend service for Chat-to-CV iOS application with Resume Writer AI Agent",
    version="1.0.0"
)

# Security middleware
security = HTTPBearer(auto_error=False)

# Rate limiting (simple in-memory implementation)
rate_limit_store = {}
RATE_LIMIT_REQUESTS = 10  # requests per minute
RATE_LIMIT_WINDOW = 60  # seconds

def check_rate_limit(user_id: str) -> bool:
    """Simple rate limiting implementation"""
    current_time = time.time()
    if user_id not in rate_limit_store:
        rate_limit_store[user_id] = []
    
    # Remove old requests outside the window
    rate_limit_store[user_id] = [
        req_time for req_time in rate_limit_store[user_id] 
        if current_time - req_time < RATE_LIMIT_WINDOW
    ]
    
    # Check if user has exceeded limit
    if len(rate_limit_store[user_id]) >= RATE_LIMIT_REQUESTS:
        return False
    
    # Add current request
    rate_limit_store[user_id].append(current_time)
    return True

# Input validation models
class GenerateResumeSectionRequest(BaseModel):
    template_id: int
    section_name: Optional[str] = None  # Now optional
    raw_input: str
    session_id: str  # Changed from user_id to session_id

    @validator('template_id')
    def validate_template_id(cls, v):
        if v not in [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16]:
            raise ValueError('Invalid template ID')
        return v

    @validator('section_name', pre=True, always=True)
    def validate_section_name(cls, v):
        # Allow None or 'auto' for section inference
        valid_sections = [
            'basics', 'work', 'education', 'skills', 'projects', 
            'awards', 'languages', 'interests', 'volunteer', 
            'publications', 'references'
        ]
        if v is None or v == 'auto':
            return v
        if v not in valid_sections:
            raise ValueError(f'Invalid section name. Must be one of: {valid_sections}, or None/"auto" for inference')
        return v

    @validator('raw_input')
    def validate_raw_input(cls, v):
        if not v or not v.strip():
            raise ValueError('Raw input cannot be empty')
        if len(v) > 2000:
            raise ValueError('Raw input too long (max 2000 characters)')
        return v.strip()

    @validator('session_id')
    def validate_session_id(cls, v):
        if not v or not v.strip():
            raise ValueError('Session ID cannot be empty')
        return v.strip()

class CreateResumeRequest(BaseModel):
    template_id: int
    title: Optional[str] = None
    user_email: str

class GenerateResumeResponse(BaseModel):
    status: str
    json_resume: dict
    quality_checklist: dict

class TemplateInfo(BaseModel):
    id: str
    name: str
    description: str
    preview_url: Optional[str] = None
    npm_package: Optional[str] = None
    version: Optional[str] = None
    author: Optional[str] = None

class CreateSessionRequest(BaseModel):
    template_id: int

class CreateSessionResponse(BaseModel):
    session_id: str
    resume_id: int
    template_id: int
    status: str

# CORS middleware for iOS app
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "https://your-ios-app.com"],  # Configure for production
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)

# Initialize services (lazy initialization)
ai_agent = None
template_service = TemplateService()
resume_renderer = ResumeRenderer()

# Mount static files for template previews
static_dir = os.path.join(os.path.dirname(__file__), "static")
app.mount("/static", StaticFiles(directory=static_dir), name="static")

@app.on_event("startup")
async def startup_event():
    """Initialize database on startup"""
    init_db()

def get_ai_agent():
    global ai_agent
    if ai_agent is None:
        ai_agent = SimpleResumeAgent()
    return ai_agent

# WebSocket connection manager
class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}
        self.connection_timestamps: Dict[str, float] = {}
        self.message_queue: Dict[str, List[str]] = {}

    async def connect(self, websocket: WebSocket, user_id: str):
        await websocket.accept()
        self.active_connections[user_id] = websocket
        self.connection_timestamps[user_id] = time.time()
        self.message_queue[user_id] = []
        
        # Send welcome message
        await websocket.send_text(json.dumps({
            "type": "connection_established",
            "user_id": user_id,
            "timestamp": datetime.utcnow().isoformat()
        }))
        
        # Send any queued messages
        if user_id in self.message_queue:
            for message in self.message_queue[user_id]:
                await websocket.send_text(message)
            self.message_queue[user_id] = []

    def disconnect(self, user_id: str):
        if user_id in self.active_connections:
            del self.active_connections[user_id]
        if user_id in self.connection_timestamps:
            del self.connection_timestamps[user_id]
        if user_id in self.message_queue:
            del self.message_queue[user_id]

    async def send_personal_message(self, message: str, user_id: str):
        if user_id in self.active_connections:
            try:
                await self.active_connections[user_id].send_text(message)
            except Exception as e:
                error_handler.log_error(e, {
                    'operation': 'websocket_send',
                    'user_id': user_id,
                    'message': message[:100]  # Log first 100 chars
                })
                # Remove failed connection
                self.disconnect(user_id)
        else:
            # Queue message for when user reconnects
            if user_id not in self.message_queue:
                self.message_queue[user_id] = []
            self.message_queue[user_id].append(message)

    def get_connection_stats(self) -> Dict[str, Any]:
        """Get WebSocket connection statistics"""
        current_time = time.time()
        return {
            "active_connections": len(self.active_connections),
            "queued_messages": sum(len(queue) for queue in self.message_queue.values()),
            "connection_durations": {
                user_id: current_time - timestamp 
                for user_id, timestamp in self.connection_timestamps.items()
            }
        }

manager = ConnectionManager()

# API Endpoints
@app.get("/")
async def root():
    return {"message": "Chat-to-CV Backend API", "version": "1.0.0"}

@app.get("/health")
async def health_check():
    """Comprehensive health check endpoint"""
    health_status = {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "version": "1.0.0",
        "services": {}
    }
    
    # Check database health
    try:
        from sqlalchemy import text
        db = next(get_db())
        db.execute(text("SELECT 1"))
        health_status["services"]["database"] = "healthy"
    except Exception as e:
        health_status["services"]["database"] = f"unhealthy: {str(e)}"
        health_status["status"] = "degraded"
    
    # Check AI agent health
    try:
        agent = get_ai_agent()
        agent_health = agent.get_health_status()
        health_status["services"]["ai_agent"] = agent_health
    except Exception as e:
        health_status["services"]["ai_agent"] = f"unhealthy: {str(e)}"
        health_status["status"] = "degraded"
    
    # Check template service health
    try:
        templates = template_service.get_available_templates()
        health_status["services"]["template_service"] = {
            "status": "healthy",
            "template_count": len(templates)
        }
    except Exception as e:
        health_status["services"]["template_service"] = f"unhealthy: {str(e)}"
        health_status["status"] = "degraded"
    
    # Add error handler status
    health_status["services"]["error_handler"] = error_handler.get_health_status()
    
    return health_status

@app.get("/metrics")
async def get_metrics():
    """Get system metrics for monitoring"""
    return {
        "error_summary": error_handler.get_error_summary(),
        "performance_metrics": error_handler.performance_metrics,
        "rate_limits": {
            "active_users": len(rate_limit_store),
            "total_requests": sum(len(requests) for requests in rate_limit_store.values())
        }
    }

@app.get("/logs")
async def get_recent_logs(limit: int = 100):
    """Get recent application logs (for debugging)"""
    try:
        with open('app.log', 'r') as f:
            lines = f.readlines()
            return {
                "logs": lines[-limit:] if len(lines) > limit else lines,
                "total_lines": len(lines)
            }
    except FileNotFoundError:
        return {"logs": [], "total_lines": 0}

@app.post("/generate-resume-section", response_model=GenerateResumeResponse)
async def generate_resume_section(
    request: GenerateResumeSectionRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Core endpoint for the Resume Writer AI Agent.
    Takes user input and generates rephrased resume content.
    """
    # Rate limiting check
    if not check_rate_limit(request.session_id):
        raise HTTPException(
            status_code=429, 
            detail="Rate limit exceeded. Please try again later."
        )
    
    try:
        db_service = DatabaseService(db)
        
        # Get session and associated user/resume
        session = db_service.get_session_by_id(request.session_id)
        if not session or session.expires_at < datetime.utcnow().replace(tzinfo=timezone.utc):
            raise HTTPException(status_code=404, detail="Session not found or expired")
        
        user = db_service.get_user_by_id(session.user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Get resume for this session
        resume = db_service.get_resume_by_id(session.resume_id)
        if not resume:
            raise HTTPException(status_code=404, detail="Resume not found")
        
        # Get current resume data from database for context
        current_resume_data = db_service.resume_to_resume_data(resume)
        
        # Infer section if needed
        section_name = request.section_name
        if section_name is None or section_name == "auto":
            section_name = llm_infer_section_from_input(request.raw_input, current_resume_data.json_resume.dict() if current_resume_data and current_resume_data.json_resume else None)
        
        # Generate resume content using AI agent with current context
        agent = get_ai_agent()
        result = await agent.generate_section(
            template_id=request.template_id,
            section_name=section_name,
            raw_input=request.raw_input,
            current_resume_data=current_resume_data
        )
        
        # Only process 100% known data - don't assume missing information
        # The AI agent should only extract what's explicitly provided
        updated_json_resume = current_resume_data.json_resume.dict()
        
        # Merge all top-level fields from the LLM output
        if "updated_section" in result and result["updated_section"]:
            try:
                section_data = json.loads(result["updated_section"])
                # If the LLM output is just a dict with basics fields, treat as basics
                if isinstance(section_data, dict):
                    # If it looks like a single section (e.g., only 'work', 'education', 'skills')
                    if set(section_data.keys()).issubset({"work", "education", "skills", "projects", "awards", "languages", "interests", "volunteer", "publications", "references"}):
                        for key, value in section_data.items():
                            if value and value != "Unknown" and value != "N/A":
                                updated_json_resume[key] = value
                    else:
                        # Merge all top-level fields
                        for key, value in section_data.items():
                            if value and value != "Unknown" and value != "N/A":
                                updated_json_resume[key] = value
                        # Recursively promote sections from nested dicts (e.g., basics)
                        updated_json_resume = promote_sections_to_top_level(updated_json_resume)
                elif isinstance(section_data, list):
                    # If the LLM output is a list, assign to the section_name
                    updated_json_resume[request.section_name] = section_data
                else:
                    # Fallback: merge all top-level fields
                    for key, value in section_data.items():
                        if value and value != "Unknown" and value != "N/A":
                            updated_json_resume[key] = value
                    updated_json_resume = promote_sections_to_top_level(updated_json_resume)
            except json.JSONDecodeError:
                pass
        
        # Clean up null values from the entire resume data
        updated_json_resume = clean_null_values(updated_json_resume)
        checklist_generator = QualityChecklistGenerator()
        # For skip-intent, ensure skip detection is applied to all possible field paths
        skipped_fields = checklist_generator.detect_skipped_fields(request.raw_input)
        def expand_skipped_fields(json_resume, skipped_fields):
            expanded = set()
            def walk(obj, path=""):
                if isinstance(obj, dict):
                    for k, v in obj.items():
                        full_path = f"{path}.{k}" if path else k
                        if k in skipped_fields or full_path in skipped_fields:
                            expanded.add(full_path)
                        walk(v, full_path)
                elif isinstance(obj, list):
                    for idx, item in enumerate(obj):
                        full_path = f"{path}[{idx}]"
                        walk(item, full_path)
            walk(json_resume)
            return expanded
        skipped_fields = expand_skipped_fields(updated_json_resume, skipped_fields)
        quality_checklist = checklist_generator.generate(updated_json_resume, skipped_fields=skipped_fields)
        
        # Validate the updated resume data against JSON Resume schema
        validator = JSONResumeValidator()
        validation_result = validator.validate_resume(updated_json_resume)
        
        # Save the processed section to database
        db_service.save_resume_section(
            resume_id=resume.id,
            section_name=section_name,
            original_input=request.raw_input,
            processed_content={
                "rephrased_content": result["rephrased_content"],
                "updated_section": result["updated_section"]
            }
        )
        
        # Update resume data in database
        db_service.update_resume_data(
            resume_id=session.resume_id,
            json_resume_data=updated_json_resume
        )
        
        # Send real-time update via WebSocket
        await manager.send_personal_message(
            json.dumps({
                "type": "resume_update",
                "resume_id": resume.id,
                "section": section_name,
                "content": result["rephrased_content"],
                "completeness": None, # No longer used
                "validation_issues": validation_result["issues"] if not validation_result["is_valid"] else []
            }),
            request.session_id
        )
        
        return GenerateResumeResponse(
            status=result["status"],
            json_resume=updated_json_resume,
            quality_checklist=quality_checklist
        )
        
    except ValueError as e:
        print("ValueError in generate_resume_section:", e)
        traceback.print_exc()
        raise HTTPException(status_code=400, detail=str(e))
    except HTTPException as e:
        print("HTTPException in generate_resume_section:", e)
        traceback.print_exc()
        raise  # Let FastAPI handle it and return the correct status code/message
    except Exception as e:
        print("Exception in generate_resume_section:", e)
        traceback.print_exc()
        raise HTTPException(status_code=500, detail="Internal server error")

@app.post("/resumes")
async def create_resume(request: CreateResumeRequest, db: AsyncSession = Depends(get_db)):
    """Create a new resume for a user"""
    try:
        db_service = DatabaseService(db)
        
        # Get or create user
        user = db_service.get_user_by_email(request.user_email)
        if not user:
            user = db_service.create_user(email=request.user_email)
        
        # Create resume
        resume = db_service.create_resume(user.id, request.template_id, request.title)
        
        return {
            "resume_id": resume.id,
            "template_id": resume.template_id,
            "title": resume.title,
            "user_id": user.id
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating resume: {str(e)}")

@app.get("/resumes/{user_email}")
async def get_user_resumes(user_email: str, db: AsyncSession = Depends(get_db)):
    """Get all resumes for a user"""
    try:
        db_service = DatabaseService(db)
        
        # Get user
        user = db_service.get_user_by_email(user_email)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Get resumes
        resumes = db_service.get_user_resumes(user.id)
        
        return [
            {
                "id": resume.id,
                "title": resume.title,
                "template_id": resume.template_id,
                "created_at": resume.created_at,
                "updated_at": resume.updated_at,
                "completeness_summary": resume.completeness_summary
            }
            for resume in resumes
        ]
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting resumes: {str(e)}")

@app.get("/resumes/{resume_id}/data")
async def get_resume_data(resume_id: int, db: AsyncSession = Depends(get_db)):
    """Get specific resume data"""
    try:
        db_service = DatabaseService(db)
        resume = db_service.get_resume_by_id(resume_id)
        
        if not resume:
            raise HTTPException(status_code=404, detail="Resume not found")
        
        return {
            "id": resume.id,
            "title": resume.title,
            "template_id": resume.template_id,
            "json_resume_data": resume.json_resume_data,
            "completeness_summary": resume.completeness_summary,
            "sections": [
                {
                    "section_name": section.section_name,
                    "original_input": section.original_input,
                    "processed_content": section.processed_content,
                    "created_at": section.created_at,
                    "updated_at": section.updated_at
                }
                for section in resume.sections
            ]
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting resume data: {str(e)}")

@app.get("/resumes/{resume_id}/voiceflow-guidance")
async def get_voiceflow_guidance(resume_id: int, db: AsyncSession = Depends(get_db)):
    """
    Get conversational guidance for Voiceflow based on current resume state.
    This endpoint analyzes the current resume data and suggests what to ask next.
    """
    try:
        db_service = DatabaseService(db)
        resume = db_service.get_resume_by_id(resume_id)
        
        if not resume:
            raise HTTPException(status_code=404, detail="Resume not found")
        
        # Convert database resume to JSON Resume format
        resume_data = db_service.resume_to_resume_data(resume)
        
        # Generate smart completeness guidance based on current state
        completeness_analyzer = CompletenessAnalyzer()
        smart_completeness = completeness_analyzer.analyze_completeness(
            resume_data.json_resume, 
            resume.template_id
        )
        
        # Analyze what's missing and what to ask next
        missing_info = smart_completeness.missing_critical_info
        suggested_topics = smart_completeness.suggested_topics
        
        # Determine conversation priority based on what's missing
        conversation_priority = "basics"  # Default
        if "name" in missing_info or "email" in missing_info:
            conversation_priority = "basics"
        elif "work" in missing_info:
            conversation_priority = "work"
        elif "education" in missing_info:
            conversation_priority = "education"
        elif "skills" in missing_info:
            conversation_priority = "skills"
        elif "projects" in missing_info:
            conversation_priority = "projects"
        
        # Generate specific next questions based on priority
        next_questions = []
        if conversation_priority == "basics":
            if "name" in missing_info:
                next_questions.append("What's your full name?")
            elif "email" in missing_info:
                next_questions.append("What's your email address?")
            elif "phone" in missing_info:
                next_questions.append("What's your phone number?")
            elif "summary" in missing_info:
                next_questions.append("Tell me about yourself - what's your professional summary?")
        elif conversation_priority == "work":
            if "work" in missing_info:
                next_questions.append("Tell me about your work experience")
            else:
                # Check for missing details in existing work experience
                for item in missing_info:
                    if item.startswith("work_") and "start_date" in item:
                        next_questions.append("When did you start your current job?")
                        break
                    elif item.startswith("work_") and "end_date" in item:
                        next_questions.append("When did you leave your previous job?")
                        break
                    elif item.startswith("work_") and "achievements" in item:
                        next_questions.append("What were your key achievements in your current role?")
                        break
        elif conversation_priority == "education":
            if "education" in missing_info:
                next_questions.append("Tell me about your education")
            else:
                # Check for missing details in existing education
                for item in missing_info:
                    if item.startswith("education_") and "field_of_study" in item:
                        next_questions.append("What did you study?")
                        break
        elif conversation_priority == "skills":
            next_questions.append("What technical skills do you have?")
        elif conversation_priority == "projects":
            next_questions.append("Tell me about any projects you've worked on")
        
        # If no specific questions, provide general guidance
        if not next_questions:
            next_questions = ["What would you like to add to your resume?"]
        
        return {
            "resume_id": resume.id,
            "template_id": resume.template_id,
            "completeness_summary": smart_completeness.dict(),
            "voiceflow_context": {
                "conversation_context": smart_completeness.conversation_context,
                "suggested_topics": suggested_topics,
                "missing_critical_info": missing_info,
                "conversation_flow_hints": smart_completeness.conversation_flow_hints,
                "user_progress_insights": smart_completeness.user_progress_insights,
                "conversation_priority": conversation_priority,
                "next_questions": next_questions[:3],  # Top 3 questions to ask
                "resume_stage": smart_completeness.conversation_context.get("resume_stage", "initial_setup"),
                "completion_percentage": smart_completeness.user_progress_insights.get("completion_percentage", 0.0)
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting Voiceflow guidance: {str(e)}")

@app.get("/templates", response_model=List[TemplateInfo])
async def get_templates(request: Request):
    """Get available JSON Resume themes"""
    templates = template_service.get_available_templates()
    base_url = str(request.base_url).rstrip("/")
    return [
        TemplateInfo(
            id=str(template.id),
            name=template.name,
            description=template.description,
            preview_url=(
                template.preview_url if (template.preview_url and template.preview_url.startswith("http"))
                else f"{base_url}{template.preview_url}" if template.preview_url else None
            ),
            npm_package=template.npm_package,
            version=template.version,
            author=template.author
        )
        for template in templates
    ]

@app.post("/validate-resume")
async def validate_resume(resume_data: Dict[str, Any]):
    """Validate resume data against JSON Resume schema"""
    validator = JSONResumeValidator()
    result = validator.validate_resume(resume_data)
    return result

@app.get("/resume/{user_id}")
async def get_resume(user_id: str):
    """Get current resume state for a user"""
    try:
        agent = get_ai_agent()
        resume_data = await agent.get_resume_data(user_id)
        return resume_data
    except Exception as e:
        raise HTTPException(status_code=404, detail=f"Resume not found: {str(e)}")

@app.get("/resume/{user_id}/json")
async def get_resume_json(user_id: str):
    """Get resume data in JSON Resume format"""
    try:
        agent = get_ai_agent()
        resume_data = await agent.get_resume_data(user_id)
        return resume_data.json_resume
    except Exception as e:
        raise HTTPException(status_code=404, detail=f"Resume not found: {str(e)}")

@app.get("/resume/{user_id}/html")
async def get_resume_html(user_id: str, theme: str = "professional"):
    """Get resume rendered as HTML using JSON Resume theme"""
    try:
        agent = get_ai_agent()
        resume_data = await agent.get_resume_data(user_id)
        
        # Render the resume using the specified theme
        html_content = resume_renderer.render_html(resume_data.json_resume, theme)
        
        if html_content:
            return {"html": html_content, "theme": theme}
        else:
            raise HTTPException(status_code=500, detail="Failed to render resume")
            
    except Exception as e:
        raise HTTPException(status_code=404, detail=f"Resume not found: {str(e)}")

@app.post("/create-session", response_model=CreateSessionResponse)
async def create_session(
    request: CreateSessionRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Create a new user session and resume without requiring email.
    Returns session_id that Voiceflow should use for subsequent calls.
    """
    try:
        db_service = DatabaseService(db)
        
        # Generate unique session ID
        session_id = str(uuid.uuid4())
        
        # Create anonymous user for this session
        user = db_service.create_user(email=f"session_{session_id}@temp.com")
        
        # Create resume with selected template
        resume = db_service.create_resume(user.id, request.template_id)
        
        # Create session record
        session = db_service.create_user_session_with_id(
            user_id=user.id,
            resume_id=resume.id,
            session_id=session_id,
            expires_at=datetime.utcnow().replace(tzinfo=timezone.utc) + timedelta(hours=24)
        )
        
        return CreateSessionResponse(
            session_id=session_id,
            resume_id=resume.id,
            template_id=request.template_id,
            status="created"
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create session: {str(e)}")

@app.get("/session/{session_id}/resume")
async def get_session_resume(
    session_id: str,
    db: AsyncSession = Depends(get_db)
):
    """
    Get resume data for a session
    """
    try:
        db_service = DatabaseService(db)
        session = db_service.get_session_by_id(session_id)
        
        if not session or session.expires_at < datetime.utcnow().replace(tzinfo=timezone.utc):
            raise HTTPException(status_code=404, detail="Session not found or expired")
        
        resume = db_service.get_resume_by_id(session.resume_id)
        if not resume:
            raise HTTPException(status_code=404, detail="Resume not found")
        
        return {
            "resume_id": resume.id,
            "template_id": resume.template_id,
            "completeness_summary": resume.completeness_summary
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get session resume: {str(e)}")

@app.websocket("/ws/{user_id}")
async def websocket_endpoint(websocket: WebSocket, user_id: str):
    """WebSocket endpoint for real-time resume updates"""
    await manager.connect(websocket, user_id)
    try:
        while True:
            # Keep connection alive and handle incoming messages
            data = await websocket.receive_text()
            
            # Parse incoming message
            try:
                message_data = json.loads(data)
                message_type = message_data.get("type", "unknown")
                
                # Handle different message types
                if message_type == "ping":
                    await websocket.send_text(json.dumps({
                        "type": "pong",
                        "timestamp": datetime.utcnow().isoformat()
                    }))
                elif message_type == "resume_request":
                    # Handle resume data requests
                    resume_id = message_data.get("resume_id")
                    if resume_id:
                        # Get resume data and send update
                        pass
                else:
                    # Echo back for testing
                    await websocket.send_text(json.dumps({
                        "type": "echo",
                        "message": data,
                        "timestamp": datetime.utcnow().isoformat()
                    }))
                    
            except json.JSONDecodeError:
                # Send error response for invalid JSON
                await websocket.send_text(json.dumps({
                    "type": "error",
                    "message": "Invalid JSON format",
                    "timestamp": datetime.utcnow().isoformat()
                }))
                
    except WebSocketDisconnect:
        manager.disconnect(user_id)
    except Exception as e:
        error_handler.log_error(e, {
            'operation': 'websocket_handler',
            'user_id': user_id
        })
        manager.disconnect(user_id)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 
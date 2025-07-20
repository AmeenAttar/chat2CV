from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, List, Optional
import json
import os
from dotenv import load_dotenv

from app.services.ai_agent import ResumeWriterAgent
from app.services.template_service import TemplateService
from app.services.resume_renderer import ResumeRenderer
from app.models.resume import ResumeSection, ResumeData, ResumeCompletenessSummary

# Load environment variables
load_dotenv()

app = FastAPI(
    title="Chat-to-CV Backend",
    description="Backend service for Chat-to-CV iOS application with Resume Writer AI Agent",
    version="1.0.0"
)

# CORS middleware for iOS app
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize services (lazy initialization)
ai_agent = None
template_service = TemplateService()
resume_renderer = ResumeRenderer()

def get_ai_agent():
    global ai_agent
    if ai_agent is None:
        ai_agent = ResumeWriterAgent()
    return ai_agent

# WebSocket connection manager
class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}

    async def connect(self, websocket: WebSocket, user_id: str):
        await websocket.accept()
        self.active_connections[user_id] = websocket

    def disconnect(self, user_id: str):
        if user_id in self.active_connections:
            del self.active_connections[user_id]

    async def send_personal_message(self, message: str, user_id: str):
        if user_id in self.active_connections:
            await self.active_connections[user_id].send_text(message)

manager = ConnectionManager()

# Request/Response Models
class GenerateResumeSectionRequest(BaseModel):
    template_id: str
    section_name: str
    raw_input: str
    user_id: str

class GenerateResumeSectionResponse(BaseModel):
    status: str
    updated_section: str
    rephrased_content: str
    resume_completeness_summary: ResumeCompletenessSummary

class TemplateInfo(BaseModel):
    id: str
    name: str
    description: str
    preview_url: Optional[str] = None

# API Endpoints
@app.get("/")
async def root():
    return {"message": "Chat-to-CV Backend API", "version": "1.0.0"}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "ai_agent": "ready"}

@app.post("/generate-resume-section", response_model=GenerateResumeSectionResponse)
async def generate_resume_section(request: GenerateResumeSectionRequest):
    """
    Core endpoint for the Resume Writer AI Agent.
    Takes user input and generates rephrased resume content.
    """
    try:
        # Generate resume content using AI agent
        agent = get_ai_agent()
        result = await agent.generate_section(
            template_id=request.template_id,
            section_name=request.section_name,
            raw_input=request.raw_input,
            user_id=request.user_id
        )
        
        # Send real-time update via WebSocket
        await manager.send_personal_message(
            json.dumps({
                "type": "resume_update",
                "section": request.section_name,
                "content": result.rephrased_content,
                "completeness": result.resume_completeness_summary.dict()
            }),
            request.user_id
        )
        
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating resume section: {str(e)}")

@app.get("/templates", response_model=List[TemplateInfo])
async def get_templates():
    """Get available resume templates"""
    return template_service.get_available_templates()

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

@app.websocket("/ws/{user_id}")
async def websocket_endpoint(websocket: WebSocket, user_id: str):
    """WebSocket endpoint for real-time resume updates"""
    await manager.connect(websocket, user_id)
    try:
        while True:
            # Keep connection alive
            data = await websocket.receive_text()
            # Echo back for testing
            await websocket.send_text(f"Message received: {data}")
    except WebSocketDisconnect:
        manager.disconnect(user_id)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 
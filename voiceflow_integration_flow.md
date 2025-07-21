# Voiceflow Integration Flow with JSON Resume Sections

## **Complete Workflow**

### **1. Template Selection & Initialization**
- User picks a template (1-16 JSON Resume themes)
- Voiceflow starts casual conversation
- Backend creates empty resume structure in database with selected template

### **2. Natural Conversation Flow**
- Voiceflow chats naturally with user
- Collects information through casual conversation
- **Does NOT wait for backend responses** - continues conversation flow
- Uses template structure from database to know what sections are empty

### **3. Data Collection & Processing**
- Voiceflow sends collected info to backend via API **after each conversation exchange**
- **Real-time processing**: Voiceflow continuously sends raw data to backend as conversation progresses
- **API Input**: template_id, section_name, raw_input, user_id, resume_id
- **Section Names** (JSON Resume compliant):
  - `basics` - Personal details (name, email, phone, summary)
  - `work` - Work experience
  - `education` - Educational background
  - `skills` - Technical and soft skills
  - `projects` - Personal/professional projects
  - `volunteer` - Volunteer experience
  - `awards` - Awards and certifications
  - `publications` - Publications
  - `languages` - Language skills
  - `interests` - Personal interests
  - `references` - Professional references

### **4. Backend Processing Chain**
```
Voiceflow Input → Resume Restructuring AI → Resume Building Function → Database Update
```
- **Resume Restructuring AI**: Converts casual input to professional JSON Resume format
- **Resume Building Function**: Adds structured data to JSON Resume template in backend (live processing)
- **Real-time updates**: Each time backend receives data, it immediately processes and updates the resume
- **Database**: Stores complete resume with template context
- **All services know the selected template** for consistent styling

### **5. Backend Response to Voiceflow**
- **Progress status**: What sections are complete/incomplete
- **Validation results**: Any data quality issues
- **Template-specific guidance**: What to ask next based on template requirements
- **NO restructured content** - that goes to resume builder service
- **JSON Resume sections status**: Which sections are filled/empty

### **6. Conversation Continuation**
- Voiceflow continues conversation based on empty template structure
- Gets live database template for full context
- Only checks recent backend response when confused or needs guidance
- **Template-specific conversation**: Different approaches for professional vs creative templates

### **7. Completion & Finalization**
- Backend determines when resume is complete (all critical sections filled)
- Backend tells Voiceflow: "Resume is complete"
- Only then can user finalize and download resume
- Voiceflow guides user through final review process

## **Key Points**
- **Template awareness**: Every service knows which template user selected
- **JSON Resume compliance**: All sections follow JSON Resume schema
- **Non-blocking**: Voiceflow doesn't wait for backend responses
- **Context-aware**: Uses live database template for conversation guidance
- **Template-specific**: Different conversation styles for different templates

## **API Endpoints**

### **POST /generate-resume-section**
**Purpose**: Send user chat input, get professional resume content back

**Voiceflow → Backend:**
```json
{
  "template_id": 1,
  "section_name": "work_experience", 
  "raw_input": "I work at Google as a software engineer for 2 years, I built web apps and improved performance by 40%",
  "user_id": "john@email.com",
  "resume_id": 123
}
```

**Backend → Voiceflow:**
```json
{
  "status": "success",
  "updated_section": "{\"work\": [{\"name\": \"Google\", \"position\": \"Software Engineer\", \"startDate\": \"2022-01\", \"endDate\": \"Present\", \"summary\": \"Developed scalable web applications and optimized system performance\", \"highlights\": [\"Improved application performance by 40% through optimization\", \"Built and maintained multiple web applications\"]}]}",
  "rephrased_content": "Software Engineer at Google (2022-Present): Developed scalable web applications and improved system performance by 40%",
  "resume_completeness_summary": {
    "work_experience": "complete",
    "education": "not_started", 
    "skills": "not_started",
    "personal_details": "complete",
    "conversation_context": {
      "resume_stage": "building_experience",
      "user_experience_level": "mid_level"
    },
    "suggested_topics": [
      "Tell me about your educational background",
      "What technical skills would you like to highlight?"
    ],
    "missing_critical_info": ["education", "skills"],
    "conversation_flow_hints": ["user_is_engaged", "build_momentum"]
  },
  "validation_issues": null
}
```

### **GET /resumes/{resume_id}/voiceflow-guidance**
**Purpose**: Get conversation guidance without sending new data

**Voiceflow → Backend:**
```
GET /resumes/123/voiceflow-guidance
```

**Backend → Voiceflow:**
```json
{
  "resume_id": 123,
  "template_id": 1,
  "completeness_summary": {
    "personal_details": "complete",
    "work_experience": "complete", 
    "education": "not_started",
    "skills": "not_started",
    "projects": "not_started"
  },
  "voiceflow_context": {
    "conversation_context": {
      "resume_stage": "building_experience",
      "user_experience_level": "mid_level",
      "industry_focus": "technology",
      "template_requirements": "professional_tone",
      "conversation_tone": "encouraging",
      "user_engagement_level": "engaged"
    },
    "suggested_topics": [
      "What's your educational background?",
      "Tell me about your technical skills",
      "Do you have any notable projects?"
    ],
    "missing_critical_info": [
      "education",
      "skills"
    ],
    "conversation_flow_hints": [
      "user_is_engaged",
      "build_momentum",
      "has_experience"
    ],
    "user_progress_insights": {
      "completion_percentage": 40.0,
      "estimated_time_remaining": 8,
      "quality_score": 85.0,
      "next_priority": "education",
      "user_pattern": "detail_oriented"
    }
  }
}
```

### **Template System (JSON Resume Compliant)**

**Available Templates (1-16):**
- **1-4**: Professional (Classy, Elegant, Kendall, Cora)
- **5-8**: Modern/Minimalist (Even, Lowmess, Waterfall, Straightforward)  
- **9-12**: Creative (Sceptile, Bufferbloat, Modern, MSResume)
- **13-16**: Specialized (Projects, Umennel, Even-Crewshin, StackOverflow-RU)

**Template Info API:**
```json
GET /templates
Response:
[
  {
    "id": "1",
    "name": "Classy", 
    "description": "An uber-classy JSONResume theme",
    "preview_url": "/static/templates/classy_preview.png",
    "npm_package": "jsonresume-theme-classy",
    "version": "1.0.9",
    "author": "JaredCubilla"
  }
]
```

## **Usage Flow:**

1. **Voiceflow starts conversation** → User picks template
2. **Voiceflow chats naturally** → Collects user info
3. **Voiceflow sends to API 1** → Gets professional content + guidance
4. **Voiceflow continues chatting** → Uses guidance to ask about missing sections
5. **Voiceflow checks API 2** → Gets updated guidance when needed
6. **Repeat until complete** → Resume is fully built

The two APIs work together: API 1 for active processing, API 2 for passive guidance checking.

This creates a seamless flow where Voiceflow handles conversation, backend handles resume building, and everything stays synchronized with the selected template. 
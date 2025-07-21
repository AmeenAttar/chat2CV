import os
import json
from datetime import datetime
from typing import Dict, List, Optional
import asyncio

from langchain.agents import AgentExecutor, initialize_agent, AgentType
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.tools import tool

# Import our services
from app.services.llama_index_rag import LlamaIndexRAGService
from app.services.database_service import DatabaseService
from app.services.template_aware_parser import TemplateAwareQualityAssurance

from app.models.resume import (
    ResumeData, 
    ResumeSection, 
    ResumeCompletenessSummary, 
    SectionStatus,
    GenerateResumeSectionResult,
    WorkExperience,
    Education,
    Skill,
    Project
)

class ResumeWriterAgent:
    """
    Core AI Agent for resume generation using LangChain + Simple RAG.
    Implements the hybrid methodology as specified in the project details.
    """
    
    def __init__(self, db_service: Optional[DatabaseService] = None):
        # Lazy initialization for LLM and agent
        self.llm = None
        self.agent = None
        
        # Database service for persistent storage
        self.db_service = db_service
        
        # Initialize RAG service
        self.rag_service = LlamaIndexRAGService()
        
        # Initialize template-aware quality assurance
        self.qa_service = TemplateAwareQualityAssurance()
        
        print("✅ ResumeWriterAgent initialized with LlamaIndex RAG Service")
        print("✅ Quality Assurance service integrated")
        if db_service:
            print("✅ Database service integrated for persistent storage")
        else:
            print("⚠️  Using in-memory storage (no database service provided)")
    
    def _get_llm(self):
        """Get LLM instance (lazy initialization)"""
        if self.llm is None:
            try:
                self.llm = ChatOpenAI(
                    model="gpt-3.5-turbo",  # Free tier model
                    temperature=0.7,
                    api_key=os.getenv("OPENAI_API_KEY")
                )
                print("✅ LLM initialized successfully")
            except Exception as e:
                print(f"Warning: Could not initialize LLM: {e}")
                return None
        return self.llm
    
    def _get_agent(self):
        """Get agent instance (lazy initialization)"""
        if self.agent is None:
            self.agent = self._create_agent()
        return self.agent
    
    def _create_agent(self):
        """Create LangChain agent with resume writing tools"""
        
        # Define tools for the agent using our RAG service (single parameter for older LangChain)
        @tool
        def get_template_guidelines(template_id: int) -> str:
            """Retrieve template-specific guidelines for resume templates. Input should be the template name like 'professional', 'modern', 'creative'."""
            return self.rag_service.get_template_guidelines(template_id)
        
        @tool
        def get_action_verbs(industry: str) -> str:
            """Get relevant action verbs for resume writing. Input should be the industry like 'tech', 'finance', 'marketing', or 'general'."""
            return self.rag_service.get_action_verbs(industry)
        
        @tool
        def get_resume_best_practices(section: str) -> str:
            """Get best practices for a specific resume section using RAG. Input should be the section name like 'work', 'education', 'skills'."""
            return self.rag_service.get_best_practices(section)
        
        @tool
        def get_industry_guidelines(industry: str) -> str:
            """Get industry-specific resume guidelines and keywords. Input should be the industry like 'tech', 'finance', 'marketing'."""
            return self.rag_service.get_industry_guidelines(industry)
        
        # Create the agent with tools
        tools = [
            get_template_guidelines,
            get_action_verbs,
            get_resume_best_practices,
            get_industry_guidelines
        ]
        
        # Create the agent using the older LangChain API
        agent = initialize_agent(
            tools=tools,
            llm=self._get_llm(),
            agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
            verbose=True
        )
        
        return agent
    
    async def generate_section(
        self, 
        template_id: int, 
        section_name: str, 
        raw_input: str, 
        user_id: str,
        resume_id: Optional[int] = None
    ) -> GenerateResumeSectionResult:
        """
        Generate resume section content using AI agent with RAG
        """
        try:
            # Get or create resume data from database
            if self.db_service:
                # Use database service for persistent storage
                if not resume_id:
                    # Create new resume if not provided
                    user = self.db_service.get_user_by_id(int(user_id))
                    if not user:
                        raise Exception(f"User {user_id} not found")
                    
                    resume = self.db_service.create_resume(
                        user_id=int(user_id),
                        template_id=template_id
                    )
                    resume_id = resume.id
                else:
                    resume = self.db_service.get_resume_by_id(resume_id)
                    if not resume:
                        raise Exception(f"Resume {resume_id} not found")
                
                # Convert to ResumeData for processing
                resume_data = self.db_service.resume_to_resume_data(resume)
            else:
                # Fallback to in-memory storage
                if user_id not in self.resume_data:
                    self.resume_data[user_id] = ResumeData(user_id=user_id, template_id=template_id)
                resume_data = self.resume_data[user_id]
            
            # Get template-specific JSON structure
            from app.services.template_service import TemplateService
            template_service = TemplateService()
            json_structure = template_service.get_template_json_structure(template_id, section_name)
            
            # Create template-specific JSON format instructions
            json_format_instructions = ""
            if json_structure:
                format_type = json_structure.get("format", "standard")
                fields = json_structure.get("fields", [])
                example = json_structure.get("example", {})
                
                json_format_instructions = f"""
TEMPLATE-SPECIFIC JSON FORMAT ({format_type.upper()}):
Required fields: {', '.join(fields)}
Example format: {example}
"""
            
            # Create a comprehensive prompt for the agent
            agent_prompt = f"""You are an expert resume writer AI assistant. Extract structured data from this resume content for the {section_name} section using the {template_id} template style.

Raw input: "{raw_input}"

CRITICAL INSTRUCTION: You must return ONLY valid JSON data, no explanations, no descriptions, no thinking out loud. Just the JSON.

Available tools:
- get_template_guidelines: Get style guidelines for specific resume templates (input: template name like '1', '2', '3', '4', '5')
- get_action_verbs: Get relevant action verbs for different industries (input: industry like 'tech', 'finance', 'marketing', 'general')
- get_resume_best_practices: Get best practices for specific resume sections (input: section name like 'work', 'education', 'skills')
- get_industry_guidelines: Get industry-specific guidelines and keywords (input: industry like 'tech', 'finance', 'marketing')

{json_format_instructions}

IMPORTANT: The JSON structure varies based on the template. Follow the template-specific format above.

Steps:
1. Use get_template_guidelines with "{template_id}" to understand the template style and any specific JSON requirements
2. Use get_resume_best_practices with "{section_name}" to get section guidelines
3. Use get_action_verbs with "general" to get strong action verbs
4. Extract structured data from the input
5. Format the data according to the template-specific JSON structure shown above
6. Apply professional language and strong action verbs

FINAL OUTPUT: Return ONLY the structured JSON data, starting with {{ or [. No other text."""
            
            # Get agent and generate content
            agent = self._get_agent()
            if agent and self._get_llm():
                try:
                    # Use the agent to generate content (older LangChain API)
                    result = agent.run(agent_prompt)
                    rephrased_content = result if result else ""
                    
                    # If agent fails, fall back to simple rephrasing
                    if not rephrased_content or len(rephrased_content) < 10:
                        rephrased_content = self._fallback_rephrase(raw_input, section_name, template_id)
                except Exception as e:
                    print(f"Agent execution failed, using fallback: {e}")
                    rephrased_content = self._fallback_rephrase(raw_input, section_name, template_id)
            else:
                # Fall back to simple rephrasing if LLM is not available
                rephrased_content = self._fallback_rephrase(raw_input, section_name, template_id)
            
            # Parse structured data from AI output and update resume data
            try:
                # Try to parse the AI output as JSON
                if rephrased_content.strip().startswith('{') or rephrased_content.strip().startswith('['):
                    parsed_data = json.loads(rephrased_content)
                else:
                    # If not JSON, treat as fallback text
                    parsed_data = None
                
                if parsed_data:
                    # Update resume data using extracted structured data
                    if section_name == "work":
                        if not resume_data.json_resume.work:
                            resume_data.json_resume.work = []
                        work_exp = WorkExperience(
                            name=parsed_data.get("name", "Company Name"),
                            position=parsed_data.get("position", "Job Title"),
                            startDate=parsed_data.get("startDate", "2023-01"),
                            endDate=parsed_data.get("endDate", "Present"),
                            summary=parsed_data.get("summary", ""),
                            highlights=parsed_data.get("highlights", [])
                        )
                        resume_data.json_resume.work.append(work_exp)
                        
                    elif section_name == "education":
                        if not resume_data.json_resume.education:
                            resume_data.json_resume.education = []
                        education = Education(
                            institution=parsed_data.get("institution", "University Name"),
                            studyType=parsed_data.get("studyType", "Bachelor's"),
                            area=parsed_data.get("area", "Field of Study"),
                            startDate=parsed_data.get("startDate", "2020-09"),
                            endDate=parsed_data.get("endDate", "2024-05")
                        )
                        resume_data.json_resume.education.append(education)
                        
                    elif section_name == "skills":
                        if not resume_data.json_resume.skills:
                            resume_data.json_resume.skills = []
                        if isinstance(parsed_data, list):
                            for skill_data in parsed_data:
                                skill = Skill(
                                    name=skill_data.get("name", "Skill"),
                                    level=skill_data.get("level", "Proficient"),
                                    keywords=skill_data.get("keywords", [])
                                )
                                resume_data.json_resume.skills.append(skill)
                        else:
                            # Single skill object
                            skill = Skill(
                                name=parsed_data.get("name", "Skill"),
                                level=parsed_data.get("level", "Proficient"),
                                keywords=parsed_data.get("keywords", [])
                            )
                            resume_data.json_resume.skills.append(skill)
                            
                    elif section_name == "projects":
                        if not resume_data.json_resume.projects:
                            resume_data.json_resume.projects = []
                        project = Project(
                            name=parsed_data.get("name", "Project Name"),
                            description=parsed_data.get("description", ""),
                            url=parsed_data.get("url", ""),
                            startDate=parsed_data.get("startDate", "2023-01"),
                            endDate=parsed_data.get("endDate", "2023-06"),
                            highlights=parsed_data.get("highlights", [])
                        )
                        resume_data.json_resume.projects.append(project)
                else:
                    # Fallback: try to extract basic information from the input
                    print(f"⚠️  AI output not in JSON format, attempting basic extraction from: {raw_input}")
                    
                    if section_name == "work":
                        if not resume_data.json_resume.work:
                            resume_data.json_resume.work = []
                        # Try to extract basic info from input
                        work_exp = self._extract_basic_work_info(raw_input)
                        resume_data.json_resume.work.append(work_exp)
                        
                    elif section_name == "education":
                        if not resume_data.json_resume.education:
                            resume_data.json_resume.education = []
                        # Try to extract basic info from input
                        education = self._extract_basic_education_info(raw_input)
                        resume_data.json_resume.education.append(education)
                        
                    elif section_name == "skills":
                        if not resume_data.json_resume.skills:
                            resume_data.json_resume.skills = []
                        # Extract skills from comma-separated input
                        skills = [skill.strip() for skill in raw_input.split(',')]
                        for skill_name in skills:
                            if skill_name:  # Only add non-empty skills
                                resume_data.json_resume.skills.append(Skill(name=skill_name))
                                
                    elif section_name == "projects":
                        if not resume_data.json_resume.projects:
                            resume_data.json_resume.projects = []
                        # Try to extract basic project info
                        project = self._extract_basic_project_info(raw_input)
                        resume_data.json_resume.projects.append(project)
                        
            except json.JSONDecodeError as e:
                print(f"Failed to parse AI output as JSON: {e}")
                # Use fallback approach with basic extraction
                print(f"⚠️  Using basic extraction fallback for: {raw_input}")
                
                if section_name == "work":
                    if not resume_data.json_resume.work:
                        resume_data.json_resume.work = []
                    work_exp = self._extract_basic_work_info(raw_input)
                    resume_data.json_resume.work.append(work_exp)
                    
                elif section_name == "education":
                    if not resume_data.json_resume.education:
                        resume_data.json_resume.education = []
                    education = self._extract_basic_education_info(raw_input)
                    resume_data.json_resume.education.append(education)
                    
                elif section_name == "skills":
                    if not resume_data.json_resume.skills:
                        resume_data.json_resume.skills = []
                    skills = [skill.strip() for skill in raw_input.split(',')]
                    for skill_name in skills:
                        if skill_name:  # Only add non-empty skills
                            resume_data.json_resume.skills.append(Skill(name=skill_name))
                            
                elif section_name == "projects":
                    if not resume_data.json_resume.projects:
                        resume_data.json_resume.projects = []
                    project = self._extract_basic_project_info(raw_input)
                    resume_data.json_resume.projects.append(project)
            
            # Apply template-aware quality assurance to the generated content
            qa_result = None
            if rephrased_content:
                try:
                    if section_name == "education":
                        qa_result = self.qa_service.process_education_section(rephrased_content, template_id)
                    elif section_name == "work":
                        qa_result = self.qa_service.process_work_section(rephrased_content, template_id)
                    elif section_name == "skills":
                        qa_result = self.qa_service.process_skills_section(rephrased_content, template_id)
                    elif section_name == "projects":
                        qa_result = self.qa_service.process_project_section(rephrased_content, template_id)
                    
                    if qa_result and qa_result["status"] == "success":
                        # Use the parsed content from QA if available
                        if "parsed_content" in qa_result:
                            print(f"✅ Template-aware quality assurance passed for {section_name} (template {template_id})")
                        else:
                            print(f"⚠️  Template-aware quality assurance warning for {section_name} (template {template_id})")
                    elif qa_result and qa_result["status"] == "warning":
                        print(f"⚠️  Template-aware quality assurance warnings for {section_name} (template {template_id}): {qa_result['validation']['issues']}")
                    elif qa_result and qa_result["status"] == "failed":
                        print(f"❌ Template-aware quality assurance failed for {section_name} (template {template_id}): {qa_result.get('error', 'Unknown error')}")
                        
                except Exception as e:
                    print(f"⚠️  Template-aware quality assurance failed: {e}")
            
            # Update completeness summary
            completeness_summary = self._update_completeness_summary(resume_data)
            
            # Save to database if using database service
            if self.db_service and resume_id:
                try:
                    # Update resume data in database
                    self.db_service.update_resume(
                        resume_id=resume_id,
                        json_resume_data=resume_data.json_resume.dict(),
                        completeness_summary=completeness_summary.dict()
                    )
                    
                    # Create or update resume section with structured data
                    section = self.db_service.get_resume_section_by_name(resume_id, section_name)
                    
                    # Prepare structured data for storage
                    structured_data = {
                        "content": rephrased_content,
                        "structured_data": self._get_section_structured_data(resume_data, section_name)
                    }
                    
                    if section:
                        self.db_service.update_resume_section(
                            section.id,
                            original_input=raw_input,
                            processed_content=structured_data,
                            status="completed"
                        )
                    else:
                        self.db_service.create_resume_section(
                            resume_id=resume_id,
                            section_name=section_name,
                            original_input=raw_input
                        )
                        self.db_service.update_resume_section_by_name(
                            resume_id=resume_id,
                            section_name=section_name,
                            processed_content=structured_data,
                            status="completed"
                        )
                    
                    print(f"✅ Saved resume section to database: {section_name}")
                except Exception as e:
                    print(f"⚠️  Failed to save to database: {e}")
            
            return GenerateResumeSectionResult(
                status="success",
                updated_section=section_name,
                rephrased_content=rephrased_content,
                resume_completeness_summary=completeness_summary,
                resume_data=resume_data
            )
            
        except Exception as e:
            print(f"Error generating resume section: {e}")
            # Fall back to simple rephrasing
            rephrased_content = self._fallback_rephrase(raw_input, section_name, template_id)
            
            return GenerateResumeSectionResult(
                status="success",
                updated_section=section_name,
                rephrased_content=rephrased_content,
                resume_completeness_summary=self._update_completeness_summary(
                    self.resume_data.get(user_id, ResumeData(user_id=user_id, template_id=template_id))
                ),
                resume_data=self.resume_data.get(user_id, ResumeData(user_id=user_id, template_id=template_id))
            )
    
    def _fallback_rephrase(self, raw_input: str, section_name: str, template_id: int = 1, industry: str = "general") -> str:
        """
        Fallback rephrasing method when LLM is not available
        Uses RAG service to get relevant guidelines and applies basic improvements
        """
        try:
            # Get relevant guidelines from RAG service
            action_verbs = self.rag_service.get_action_verbs(industry)
            
            # Simple rephrasing logic
            rephrased = raw_input
            
            # Apply basic improvements
            if section_name == "work":
                # Replace weak verbs with strong action verbs
                weak_verbs = ["did", "made", "worked on", "helped with", "was responsible for"]
                rephrased = raw_input
                
                for weak_verb in weak_verbs:
                    if weak_verb in rephrased.lower():
                        # Find a suitable action verb
                        verbs = [v.strip() for v in action_verbs.split(", ")]
                        if verbs:
                            rephrased = rephrased.lower().replace(weak_verb, verbs[0].lower())
                        break
                
                # Add quantification if numbers are mentioned
                if any(char.isdigit() for char in raw_input):
                    if "increased" not in raw_input.lower() and "improved" not in raw_input.lower():
                        rephrased = f"Improved {rephrased}"
                
                # Ensure it starts with a strong action verb
                if not rephrased[0].isupper():
                    rephrased = rephrased.capitalize()
            
            elif section_name == "skills":
                # Format skills properly
                skills = [skill.strip() for skill in raw_input.split(',')]
                rephrased = ", ".join(skills)
            
            elif section_name == "education":
                # Ensure proper formatting
                rephrased = raw_input
            
            elif section_name == "projects":
                # Add impact if not present
                if "impact" not in raw_input.lower() and "result" not in raw_input.lower():
                    rephrased = f"{raw_input}, delivering measurable results"
            
            return rephrased
            
        except Exception as e:
            print(f"Fallback rephrasing failed: {e}")
            return raw_input
    
    def _update_completeness_summary(self, resume_data: ResumeData) -> ResumeCompletenessSummary:
        """Update the completeness summary for the resume"""
        return ResumeCompletenessSummary(
            basics=SectionStatus.COMPLETE if resume_data.json_resume.basics else SectionStatus.NOT_STARTED,
            work=SectionStatus.COMPLETE if resume_data.json_resume.work and len(resume_data.json_resume.work) >= 1 else SectionStatus.INCOMPLETE,
            education=SectionStatus.COMPLETE if resume_data.json_resume.education and len(resume_data.json_resume.education) >= 1 else SectionStatus.INCOMPLETE,
            skills=SectionStatus.COMPLETE if resume_data.json_resume.skills and len(resume_data.json_resume.skills) >= 3 else SectionStatus.INCOMPLETE,
            projects=SectionStatus.COMPLETE if resume_data.json_resume.projects and len(resume_data.json_resume.projects) >= 1 else SectionStatus.NOT_STARTED
        )
    
    async def get_resume_data(self, user_id: str) -> ResumeData:
        """Get resume data for a user"""
        if user_id not in self.resume_data:
            # Use a default template if none is specified
            self.resume_data[user_id] = ResumeData(user_id=user_id, template_id="professional")
        return self.resume_data[user_id]
    
    def get_rag_health(self) -> Dict:
        """Get health status of the RAG system"""
        return self.rag_service.health_check()
    
    def _extract_basic_work_info(self, raw_input: str) -> WorkExperience:
        """Extract basic work information from raw input"""
        input_lower = raw_input.lower()
        
        # Try to extract company name (common patterns)
        company = "Company Name"
        if "at " in input_lower:
            company_part = input_lower.split("at ")[-1].split(" ")[0]
            if company_part and len(company_part) > 2:
                company = company_part.title()
        
        # Try to extract position
        position = "Job Title"
        if "as " in input_lower:
            position_part = input_lower.split("as ")[-1].split(" ")[:2]
            if position_part:
                position = " ".join(position_part).title()
        
        # Try to extract duration
        duration = ""
        if "for " in input_lower and any(char.isdigit() for char in input_lower):
            duration_part = input_lower.split("for ")[-1].split(" ")[0]
            if duration_part.isdigit():
                duration = f"{duration_part} years"
        
        return WorkExperience(
            name=company,
            position=position,
            startDate="2023-01",
            endDate="Present",
            summary=raw_input,
            highlights=[f"Worked {duration}" if duration else "Completed assigned tasks"]
        )
    
    def _extract_basic_education_info(self, raw_input: str) -> Education:
        """Extract basic education information from raw input"""
        input_lower = raw_input.lower()
        
        # Try to extract institution
        institution = "University Name"
        if "from " in input_lower:
            institution_part = input_lower.split("from ")[-1].split(" ")[0]
            if institution_part and len(institution_part) > 2:
                institution = institution_part.title()
        
        # Try to extract degree type
        study_type = "Bachelor's"
        if "bachelor" in input_lower:
            study_type = "Bachelor's"
        elif "master" in input_lower:
            study_type = "Master's"
        elif "phd" in input_lower or "doctorate" in input_lower:
            study_type = "PhD"
        
        # Try to extract field of study
        area = "Field of Study"
        if "in " in input_lower:
            area_part = input_lower.split("in ")[-1].split(" ")[0]
            if area_part and len(area_part) > 1:
                area = area_part.upper()
        
        return Education(
            institution=institution,
            studyType=study_type,
            area=area,
            startDate="2020-09",
            endDate="2024-05"
        )
    
    def _extract_basic_project_info(self, raw_input: str) -> Project:
        """Extract basic project information from raw input"""
        return Project(
            name="Project Name",
            description=raw_input,
            url="",
            startDate="2023-01",
            endDate="2023-06",
            highlights=["Completed project successfully"]
        )
    
    def _get_section_structured_data(self, resume_data: ResumeData, section_name: str) -> dict:
        """Extract structured data for a specific section from resume_data"""
        if section_name == "work" and resume_data.json_resume.work:
            latest_work = resume_data.json_resume.work[-1]  # Get most recent
            return {
                "name": latest_work.name,
                "position": latest_work.position,
                "startDate": latest_work.startDate,
                "endDate": latest_work.endDate,
                "summary": latest_work.summary,
                "highlights": latest_work.highlights or []
            }
        elif section_name == "education" and resume_data.json_resume.education:
            latest_education = resume_data.json_resume.education[-1]  # Get most recent
            return {
                "institution": latest_education.institution,
                "studyType": latest_education.studyType,
                "area": latest_education.area,
                "startDate": latest_education.startDate,
                "endDate": latest_education.endDate
            }
        elif section_name == "skills" and resume_data.json_resume.skills:
            return [{"name": skill.name, "level": skill.level, "keywords": skill.keywords or []} 
                   for skill in resume_data.json_resume.skills]
        elif section_name == "projects" and resume_data.json_resume.projects:
            latest_project = resume_data.json_resume.projects[-1]  # Get most recent
            return {
                "name": latest_project.name,
                "description": latest_project.description,
                "url": latest_project.url,
                "startDate": latest_project.startDate,
                "endDate": latest_project.endDate,
                "highlights": latest_project.highlights or []
            }
        else:
            return {} 
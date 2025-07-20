import os
import json
from datetime import datetime
from typing import Dict, List, Optional
import asyncio

from langchain.agents import AgentExecutor, create_openai_functions_agent
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.tools import tool
from langchain_core.output_parsers import StrOutputParser

# Temporarily disable LlamaIndex for MVP - will implement RAG in next iteration
# from llama_index.core import VectorStoreIndex, SimpleDirectoryReader
# from llama_index.vector_stores.chroma import ChromaVectorStore
# from llama_index.embeddings.openai import OpenAIEmbedding
# import chromadb

from app.models.resume import (
    ResumeData, 
    ResumeSection, 
    ResumeCompletenessSummary, 
    SectionStatus,
    GenerateResumeSectionResult
)

class ResumeWriterAgent:
    """
    Core AI Agent for resume generation using LangChain + LlamaIndex.
    Implements the hybrid methodology as specified in the project details.
    """
    
    def __init__(self):
        self.llm = ChatOpenAI(
            model="gpt-4",
            temperature=0.7,
            api_key=os.getenv("OPENAI_API_KEY")
        )
        
        # Initialize LangChain agent (simplified for MVP)
        self.agent = self._create_agent()
        
        # In-memory storage for resume data (replace with database in production)
        self.resume_data: Dict[str, ResumeData] = {}
        
        # Initialize knowledge base (simplified for MVP)
        self._initialize_knowledge_base()
    
    def _initialize_vector_store(self):
        """Initialize ChromaDB vector store (disabled for MVP)"""
        # TODO: Implement vector store for RAG in next iteration
        pass
    
    def _create_query_engine(self):
        """Create LlamaIndex query engine for knowledge retrieval (disabled for MVP)"""
        # TODO: Implement query engine for RAG in next iteration
        pass
    
    def _create_agent(self):
        """Create LangChain agent with resume writing tools"""
        
        # Define tools for the agent (simplified for MVP)
        @tool
        def get_template_guidelines(template_id: str, section: str) -> str:
            """Retrieve template-specific guidelines for a resume section"""
            # Simplified for MVP - return hardcoded guidelines
            guidelines = {
                "professional": "Use formal tone, clear structure, focus on achievements",
                "modern": "Use contemporary language, clean formatting, emphasize results",
                "creative": "Use innovative language, bold statements, highlight creativity",
                "minimalist": "Use simple language, focus on content, avoid unnecessary words",
                "executive": "Use sophisticated language, emphasize leadership and strategy"
            }
            return guidelines.get(template_id, "Use professional tone and clear structure")
        
        @tool
        def get_action_verbs(industry: str = "general") -> str:
            """Get relevant action verbs for resume writing"""
            # Simplified for MVP - return common action verbs
            verbs = "Managed, Led, Developed, Implemented, Created, Designed, Analyzed, Optimized, Increased, Improved, Established, Coordinated, Facilitated, Generated, Delivered"
            return f"Common action verbs for {industry}: {verbs}"
        
        @tool
        def get_resume_best_practices(section: str) -> str:
            """Get best practices for a specific resume section"""
            # Simplified for MVP - return basic best practices
            practices = {
                "work_experience": "Use strong action verbs, quantify achievements, focus on results",
                "education": "Include degree, institution, graduation date, relevant coursework",
                "skills": "Group by category, include proficiency levels, focus on relevant skills",
                "projects": "Describe impact, use metrics, highlight technical skills"
            }
            return practices.get(section, "Use clear, professional language and focus on achievements")
        
        # Create prompt template
        prompt = ChatPromptTemplate.from_messages([
            ("system", """You are an expert resume writer AI agent. Your job is to take user input and rephrase it to match the selected resume template style.

Key responsibilities:
1. Analyze the user's raw input
2. Retrieve relevant template guidelines and best practices
3. Rephrase the content to match the template style
4. Use appropriate action verbs and keywords
5. Ensure professional, clear, and impactful language
6. Quantify achievements where possible

Always maintain the user's original meaning while improving the presentation and impact."""),
            MessagesPlaceholder(variable_name="chat_history"),
            ("human", "{input}"),
            MessagesPlaceholder(variable_name="agent_scratchpad"),
        ])
        
        # Create agent
        agent = create_openai_functions_agent(
            llm=self.llm,
            tools=[get_template_guidelines, get_action_verbs, get_resume_best_practices],
            prompt=prompt
        )
        
        return AgentExecutor(agent=agent, tools=[get_template_guidelines, get_action_verbs, get_resume_best_practices])
    
    def _initialize_knowledge_base(self):
        """Initialize the knowledge base with resume writing guidelines (simplified for MVP)"""
        # Create knowledge base directory if it doesn't exist
        os.makedirs("app/knowledge_base", exist_ok=True)
        
        # Create sample knowledge base files (simplified for MVP)
        self._create_sample_knowledge_files()
        
        # TODO: Implement vector store integration in next iteration
        print("Knowledge base initialized (simplified for MVP)")
    
    def _create_sample_knowledge_files(self):
        """Create sample knowledge base files for development"""
        
        # Template guidelines
        template_guidelines = """
# Professional Template Guidelines

## Overall Style
- Clean, minimalist design
- Professional tone
- Clear hierarchy with headings
- Consistent formatting

## Action Verbs
- Managed, Led, Developed, Implemented, Created, Designed, Analyzed, Optimized, Increased, Improved

## Best Practices
- Use bullet points for achievements
- Quantify results with numbers
- Start with strong action verbs
- Keep descriptions concise and impactful
- Focus on achievements, not just responsibilities
        """
        
        with open("app/knowledge_base/template_guidelines.md", "w") as f:
            f.write(template_guidelines)
        
        # Resume best practices
        best_practices = """
# Resume Best Practices

## Work Experience Section
- Use strong action verbs
- Quantify achievements with numbers
- Focus on results and impact
- Use present tense for current roles, past tense for previous roles
- Include relevant keywords for ATS

## Skills Section
- Group skills by category (Technical, Soft Skills, Languages)
- Include proficiency levels where appropriate
- Focus on skills relevant to the target position

## Education Section
- Include degree, institution, graduation date
- Add relevant coursework if recent graduate
- Include GPA if 3.5+ (optional)

## General Tips
- Keep it to 1-2 pages
- Use consistent formatting
- Proofread carefully
- Tailor content to the job description
        """
        
        with open("app/knowledge_base/best_practices.md", "w") as f:
            f.write(best_practices)
    
    async def generate_section(
        self, 
        template_id: str, 
        section_name: str, 
        raw_input: str, 
        user_id: str
    ) -> GenerateResumeSectionResult:
        """
        Generate rephrased resume content for a specific section.
        This is the core method that implements the hybrid LangChain + LlamaIndex approach.
        """
        
        # Get or create resume data for user
        if user_id not in self.resume_data:
            self.resume_data[user_id] = ResumeData(
                user_id=user_id,
                template_id=template_id,
                created_at=datetime.now().isoformat()
            )
        
        resume_data = self.resume_data[user_id]
        
        # Create agent input with context
        agent_input = f"""
        Template ID: {template_id}
        Section: {section_name}
        User Input: {raw_input}
        
        Please rephrase this input to match the template style and best practices.
        """
        
        try:
            # Run the agent to generate rephrased content
            result = await asyncio.to_thread(
                self.agent.invoke,
                {"input": agent_input}
            )
            
            rephrased_content = result.get("output", raw_input)
            
            # Update resume data
            if section_name not in resume_data.sections:
                resume_data.sections[section_name] = ResumeSection(name=section_name)
            
            section = resume_data.sections[section_name]
            section.content.append(rephrased_content)
            section.status = SectionStatus.PARTIAL
            section.last_updated = datetime.now().isoformat()
            
            # Update completeness summary
            completeness_summary = self._update_completeness_summary(resume_data)
            resume_data.completeness_summary = completeness_summary
            resume_data.updated_at = datetime.now().isoformat()
            
            return GenerateResumeSectionResult(
                status="success",
                updated_section=section_name,
                rephrased_content=rephrased_content,
                resume_completeness_summary=completeness_summary
            )
            
        except Exception as e:
            # Fallback to simple rephrasing if agent fails
            fallback_content = self._fallback_rephrase(raw_input, section_name)
            
            # Update resume data with fallback
            if section_name not in resume_data.sections:
                resume_data.sections[section_name] = ResumeSection(name=section_name)
            
            section = resume_data.sections[section_name]
            section.content.append(fallback_content)
            section.status = SectionStatus.PARTIAL
            section.last_updated = datetime.now().isoformat()
            
            completeness_summary = self._update_completeness_summary(resume_data)
            resume_data.completeness_summary = completeness_summary
            resume_data.updated_at = datetime.now().isoformat()
            
            return GenerateResumeSectionResult(
                status="success (fallback)",
                updated_section=section_name,
                rephrased_content=fallback_content,
                resume_completeness_summary=completeness_summary
            )
    
    def _fallback_rephrase(self, raw_input: str, section_name: str) -> str:
        """Simple fallback rephrasing when AI agent fails"""
        # Basic rephrasing logic for development
        if "managed" in raw_input.lower():
            raw_input = raw_input.replace("managed", "Led")
        if "did" in raw_input.lower():
            raw_input = raw_input.replace("did", "Accomplished")
        
        return f"• {raw_input}"
    
    def _update_completeness_summary(self, resume_data: ResumeData) -> ResumeCompletenessSummary:
        """Update the completeness summary based on current sections"""
        summary = ResumeCompletenessSummary()
        
        for section_name, section in resume_data.sections.items():
            if section.content:
                if len(section.content) >= 3:
                    status = SectionStatus.COMPLETE
                elif len(section.content) >= 1:
                    status = SectionStatus.PARTIAL
                else:
                    status = SectionStatus.INCOMPLETE
                
                # Map section names to summary fields
                if section_name == "personal_details":
                    summary.personal_details = status
                elif section_name == "work_experience":
                    summary.work_experience = status
                elif section_name == "education":
                    summary.education = status
                elif section_name == "skills":
                    summary.skills = status
                elif section_name == "projects":
                    summary.projects = status
                elif section_name == "certifications":
                    summary.certifications = status
                elif section_name == "languages":
                    summary.languages = status
                elif section_name == "interests":
                    summary.interests = status
        
        return summary
    
    async def get_resume_data(self, user_id: str) -> ResumeData:
        """Get current resume data for a user"""
        if user_id not in self.resume_data:
            raise ValueError(f"No resume data found for user {user_id}")
        return self.resume_data[user_id] 
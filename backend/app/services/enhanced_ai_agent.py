#!/usr/bin/env python3
"""
Enhanced AI Agent for Resume Generation
Fixes LangChain execution issues, improves prompt engineering, and adds robust error recovery
"""

import os
import json
import asyncio
from typing import Dict, Any, Optional, List
from datetime import datetime
import logging

# Try multiple LLM providers for better reliability
try:
    import google.generativeai as genai
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False

try:
    from openai import OpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False

# Import our services
from app.services.llama_index_rag import LlamaIndexRAGService
from app.services.database_service import DatabaseService
from app.services.template_aware_parser import TemplateAwareQualityAssurance
from app.services.output_parser import OutputParser

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

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class EnhancedResumeAgent:
    """
    Enhanced AI Agent with multiple LLM providers, improved prompts, and robust error recovery
    """
    
    def __init__(self, db_service: Optional[DatabaseService] = None, use_rag: bool = True):
        self.db_service = db_service
        self.use_rag = use_rag
        
        # Initialize RAG service only if requested
        if use_rag:
            try:
                self.rag_service = LlamaIndexRAGService()
                print("✅ LlamaIndex RAG service initialized")
            except Exception as e:
                print(f"⚠️  RAG service initialization failed: {e}")
                self.rag_service = None
                self.use_rag = False
        else:
            self.rag_service = None
            print("⚠️  RAG service disabled for testing")
        
        # Initialize other services
        try:
            self.qa_service = TemplateAwareQualityAssurance()
            self.output_parser = OutputParser()
        except Exception as e:
            print(f"⚠️  Some services failed to initialize: {e}")
            self.qa_service = None
            self.output_parser = None
        
        # Initialize multiple LLM providers for fallback
        self.llm_providers = self._initialize_llm_providers()
        
        # Track provider performance for intelligent fallback
        self.provider_stats = {
            'gemini': {'success': 0, 'failure': 0, 'avg_response_time': 0},
            'openai': {'success': 0, 'failure': 0, 'avg_response_time': 0},
            'fallback': {'success': 0, 'failure': 0, 'avg_response_time': 0}
        }
        
        logger.info("✅ EnhancedResumeAgent initialized with multiple LLM providers")
    
    def _initialize_llm_providers(self) -> Dict[str, Any]:
        """Initialize multiple LLM providers for redundancy"""
        providers = {}
        
        # Initialize Gemini
        if GEMINI_AVAILABLE:
            gemini_key = os.getenv("GEMINI_API_KEY")
            if gemini_key:
                try:
                    genai.configure(api_key=gemini_key)
                    providers['gemini'] = genai.GenerativeModel('gemini-1.5-flash')
                    logger.info("✅ Gemini LLM provider initialized")
                except Exception as e:
                    logger.warning(f"⚠️  Failed to initialize Gemini: {e}")
        
        # Initialize OpenAI
        if OPENAI_AVAILABLE:
            openai_key = os.getenv("OPENAI_API_KEY")
            if openai_key:
                try:
                    providers['openai'] = OpenAI(api_key=openai_key)
                    logger.info("✅ OpenAI LLM provider initialized")
                except Exception as e:
                    logger.warning(f"⚠️  Failed to initialize OpenAI: {e}")
        
        if not providers:
            logger.warning("⚠️  No LLM providers available, using fallback only")
        
        return providers
    
    def _create_enhanced_prompt(self, section_name: str, raw_input: str, template_id: int, 
                               current_resume_data: Optional[ResumeData] = None) -> str:
        """Create context-aware, template-specific prompts with RAG integration"""
        
        # Get RAG context if available
        if self.rag_service and self.use_rag:
            try:
                template_guidelines = self.rag_service.get_template_guidelines(template_id)
                best_practices = self.rag_service.get_best_practices(section_name)
                action_verbs = self.rag_service.get_action_verbs("general")
            except Exception as e:
                logger.warning(f"RAG service failed: {e}")
                template_guidelines = "Use professional tone and clear structure"
                best_practices = "Focus on achievements and use strong action verbs"
                action_verbs = "Managed, Led, Developed, Implemented, Created, Designed, Analyzed, Optimized"
        else:
            # Fallback content when RAG is not available
            template_guidelines = "Use professional tone and clear structure"
            best_practices = "Focus on achievements and use strong action verbs"
            action_verbs = "Managed, Led, Developed, Implemented, Created, Designed, Analyzed, Optimized"
        
        # Get current resume context
        current_context = {}
        if current_resume_data and current_resume_data.json_resume:
            current_context = current_resume_data.json_resume.dict()
        
        # Create section-specific instructions
        section_instructions = self._get_section_specific_instructions(section_name, template_id)
        
        # Create template-specific formatting
        json_format = self._get_json_format_for_section(section_name, template_id)
        
        prompt = f"""
You are an expert resume writer specializing in JSON Resume format. Your task is to convert user input into professional, structured resume content.

CONTEXT:
- Section: {section_name}
- Template ID: {template_id}
- User Input: "{raw_input}"

TEMPLATE GUIDELINES:
{template_guidelines}

SECTION BEST PRACTICES:
{best_practices}

ACTION VERBS:
{action_verbs}

CURRENT RESUME CONTEXT:
{json.dumps(current_context, indent=2)}

SECTION-SPECIFIC INSTRUCTIONS:
{section_instructions}

JSON FORMAT REQUIREMENTS:
{json_format}

CRITICAL INSTRUCTIONS:
1. Convert the user input into professional resume content
2. Follow the template guidelines and maintain consistency with existing content
3. Use strong action verbs and quantify achievements where possible
4. Return ONLY a valid JSON object - no explanations, no markdown, no additional text
5. Ensure all dates are in YYYY-MM format (or YYYY for education)
6. OMIT any fields that are empty or not provided - do not include null values
7. Maintain the exact JSON structure specified above

Generate the content now. Return ONLY the JSON object:
"""
        return prompt
    
    def _get_section_specific_instructions(self, section_name: str, template_id: int) -> str:
        """Get section-specific instructions based on template and section"""
        
        instructions = {
            "work": {
                "focus": "achievements, impact, and measurable results",
                "structure": "company, position, dates, summary, highlights",
                "tone": "professional and achievement-oriented"
            },
            "education": {
                "focus": "degree, institution, relevant coursework, achievements",
                "structure": "institution, studyType, area, startDate, endDate",
                "tone": "academic and professional"
            },
            "skills": {
                "focus": "technical skills, proficiency levels, and relevance",
                "structure": "name, level, keywords",
                "tone": "clear and specific"
            },
            "projects": {
                "focus": "technical details, impact, and technologies used",
                "structure": "name, description, highlights, keywords, startDate, endDate",
                "tone": "technical and achievement-focused"
            },
            "personal_details": {
                "focus": "contact information, summary, and professional branding",
                "structure": "name, email, phone, location, summary",
                "tone": "professional and concise"
            }
        }
        
        section_info = instructions.get(section_name, {
            "focus": "relevant information and achievements",
            "structure": "standard JSON Resume format",
            "tone": "professional"
        })
        
        return f"""
Focus: {section_info['focus']}
Structure: {section_info['structure']}
Tone: {section_info['tone']}
"""
    
    def _get_json_format_for_section(self, section_name: str, template_id: int) -> str:
        """Get JSON format requirements for specific section and template"""
        
        formats = {
            "work": {
                "structure": {
                    "name": "string (company name)",
                    "position": "string (job title)",
                    "startDate": "string (YYYY-MM)",
                    "endDate": "string (YYYY-MM or 'Present')",
                    "summary": "string (brief description)",
                    "highlights": ["string (achievement 1)", "string (achievement 2)"]
                },
                "example": {
                    "name": "Tech Company Inc.",
                    "position": "Senior Software Engineer",
                    "startDate": "2022-01",
                    "endDate": "Present",
                    "summary": "Led development of scalable web applications",
                    "highlights": [
                        "Reduced API response time by 40% through optimization",
                        "Led team of 5 developers to deliver MVP in 3 months"
                    ]
                }
            },
            "education": {
                "structure": {
                    "institution": "string (university name)",
                    "studyType": "string (Bachelor's, Master's, etc.)",
                    "area": "string (field of study)",
                    "startDate": "string (YYYY)",
                    "endDate": "string (YYYY)",
                    "score": "string (GPA if 3.5+)"
                },
                "example": {
                    "institution": "Stanford University",
                    "studyType": "Bachelor's",
                    "area": "Computer Science",
                    "startDate": "2018",
                    "endDate": "2022",
                    "score": "3.8"
                }
            },
            "skills": {
                "structure": {
                    "name": "string (skill name)",
                    "level": "string (Beginner, Intermediate, Advanced, Expert)",
                    "keywords": ["string (related terms)"]
                },
                "example": {
                    "name": "Python",
                    "level": "Expert",
                    "keywords": ["Django", "Flask", "Data Analysis", "Machine Learning"]
                }
            }
        }
        
        section_format = formats.get(section_name, {
            "structure": "Follow JSON Resume schema",
            "example": "Use standard format"
        })
        
        return f"""
Required Structure:
{json.dumps(section_format['structure'], indent=2)}

Example:
{json.dumps(section_format['example'], indent=2)}
"""
    
    async def generate_section(self, template_id: int, section_name: str, raw_input: str, 
                              current_resume_data: Optional[ResumeData] = None) -> Dict[str, Any]:
        """Generate resume section with multiple fallback strategies"""
        
        start_time = datetime.now()
        
        try:
            # Create enhanced prompt
            prompt = self._create_enhanced_prompt(section_name, raw_input, template_id, current_resume_data)
            
            # Try multiple LLM providers with intelligent fallback
            result = await self._try_multiple_providers(prompt, section_name)
            
            # Process and validate result
            processed_result = self._process_and_validate_result(result, section_name, raw_input)
            
            # Update provider statistics
            self._update_provider_stats('success', start_time)
            
            return processed_result
            
        except Exception as e:
            logger.error(f"❌ All AI providers failed: {e}")
            self._update_provider_stats('failure', start_time)
            
            # Final fallback to rule-based processing
            return self._rule_based_fallback(section_name, raw_input, template_id)
    
    async def _try_multiple_providers(self, prompt: str, section_name: str) -> str:
        """Try multiple LLM providers with intelligent fallback"""
        
        # Sort providers by success rate for optimal order
        sorted_providers = self._get_sorted_providers()
        
        for provider_name in sorted_providers:
            if provider_name not in self.llm_providers:
                continue
                
            try:
                logger.info(f"🔄 Trying {provider_name} provider...")
                result = await self._call_llm_provider(provider_name, prompt)
                
                if result and self._validate_llm_response(result, section_name):
                    logger.info(f"✅ {provider_name} provider succeeded")
                    return result
                    
            except Exception as e:
                logger.warning(f"⚠️  {provider_name} provider failed: {e}")
                self.provider_stats[provider_name]['failure'] += 1
        
        # If all providers fail, use rule-based fallback
        logger.warning("⚠️  All LLM providers failed, using rule-based fallback")
        return ""
    
    def _get_sorted_providers(self) -> List[str]:
        """Get providers sorted by success rate"""
        if not self.provider_stats:
            return list(self.llm_providers.keys())
        
        # Calculate success rates
        success_rates = {}
        for provider, stats in self.provider_stats.items():
            total = stats['success'] + stats['failure']
            if total > 0:
                success_rates[provider] = stats['success'] / total
            else:
                success_rates[provider] = 0.5  # Default to 50% for new providers
        
        # Sort by success rate (highest first)
        return sorted(success_rates.keys(), key=lambda x: success_rates[x], reverse=True)
    
    async def _call_llm_provider(self, provider_name: str, prompt: str) -> str:
        """Call specific LLM provider"""
        
        if provider_name == 'gemini':
            response = self.llm_providers['gemini'].generate_content(prompt)
            return response.text
        
        elif provider_name == 'openai':
            response = self.llm_providers['openai'].chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.7,
                max_tokens=1000
            )
            return response.choices[0].message.content
        
        else:
            raise ValueError(f"Unknown provider: {provider_name}")
    
    def _validate_llm_response(self, response: str, section_name: str) -> bool:
        """Validate LLM response quality"""
        
        if not response or len(response.strip()) < 10:
            return False
        
        # Check if response looks like JSON
        response_clean = response.strip()
        if not (response_clean.startswith('{') or response_clean.startswith('[')):
            return False
        
        # Try to parse as JSON
        try:
            json.loads(response_clean)
            return True
        except json.JSONDecodeError:
            return False
    
    def _process_and_validate_result(self, result: str, section_name: str, raw_input: str) -> Dict[str, Any]:
        """Process and validate the AI result"""
        
        if not result:
            return self._rule_based_fallback(section_name, raw_input)
        
        try:
            # Parse JSON response
            parsed_data = json.loads(result.strip())
            
            # Use output parser for quality assurance
            qa_result = self.qa_service.process_section(section_name, parsed_data)
            
            if qa_result['status'] == 'success':
                return {
                    'status': 'success',
                    'updated_section': json.dumps(parsed_data),
                    'rephrased_content': self._extract_text_content(parsed_data, section_name),
                    'quality_score': qa_result.get('quality_score', 0.8)
                }
            else:
                logger.warning(f"⚠️  Quality check failed: {qa_result.get('issues', [])}")
                return self._rule_based_fallback(section_name, raw_input)
                
        except json.JSONDecodeError as e:
            logger.warning(f"⚠️  JSON parsing failed: {e}")
            return self._rule_based_fallback(section_name, raw_input)
    
    def _rule_based_fallback(self, section_name: str, raw_input: str, template_id: int = 1) -> Dict[str, Any]:
        """Rule-based fallback when AI providers fail"""
        
        logger.info(f"🔄 Using rule-based fallback for {section_name}")
        
        try:
            if section_name == "work":
                result = self._extract_work(raw_input)
            elif section_name == "education":
                result = self._extract_education(raw_input)
            elif section_name == "skills":
                result = self._extract_skills(raw_input)
            elif section_name == "projects":
                result = self._extract_projects(raw_input)
            else:
                result = self._extract_generic_section(raw_input, section_name)
            
            return {
                'status': 'fallback_success',
                'updated_section': json.dumps(result),
                'rephrased_content': self._extract_text_content(result, section_name),
                'quality_score': 0.6  # Lower quality for fallback
            }
            
        except Exception as e:
            logger.error(f"❌ Rule-based fallback failed: {e}")
            return {
                'status': 'error',
                'updated_section': '{}',
                'rephrased_content': raw_input,
                'quality_score': 0.0
            }
    
    def _extract_work(self, raw_input: str) -> Dict[str, Any]:
        """Extract work experience using rule-based approach"""
        
        # Simple extraction logic
        lines = raw_input.split('.')
        
        # Try to extract company and position
        company = "Company Name"
        position = "Job Title"
        
        for line in lines:
            line = line.strip().lower()
            if 'at' in line:
                parts = line.split('at')
                if len(parts) >= 2:
                    position = parts[0].strip().title()
                    company = parts[1].strip().title()
                    break
        
        return {
            "name": company,
            "position": position,
            "startDate": "2023-01",
            "endDate": "Present",
            "summary": raw_input,
            "highlights": [raw_input]
        }
    
    def _extract_education(self, raw_input: str) -> Dict[str, Any]:
        """Extract education using rule-based approach"""
        
        institution = "University Name"
        study_type = "Bachelor's"
        area = "Field of Study"
        
        # Simple extraction
        if 'bachelor' in raw_input.lower():
            study_type = "Bachelor's"
        elif 'master' in raw_input.lower():
            study_type = "Master's"
        elif 'phd' in raw_input.lower() or 'doctorate' in raw_input.lower():
            study_type = "PhD"
        
        return {
            "institution": institution,
            "studyType": study_type,
            "area": area,
            "startDate": "2020",
            "endDate": "2024"
        }
    
    def _extract_skills(self, raw_input: str) -> Dict[str, Any]:
        """Extract skills using rule-based approach"""
        
        skills = raw_input.split(',')
        return {
            "name": skills[0].strip() if skills else "Skill",
            "level": "Intermediate",
            "keywords": [skill.strip() for skill in skills[1:] if skill.strip()]
        }
    
    def _extract_projects(self, raw_input: str) -> Dict[str, Any]:
        """Extract projects using rule-based approach"""
        
        return {
            "name": "Project Name",
            "description": raw_input,
            "highlights": [raw_input],
            "keywords": [],
            "startDate": "2023-01",
            "endDate": "2023-12"
        }
    
    def _extract_generic_section(self, raw_input: str, section_name: str) -> Dict[str, Any]:
        """Extract generic section data"""
        
        return {
            "name": section_name.replace('_', ' ').title(),
            "description": raw_input,
            "content": raw_input
        }
    
    def _extract_text_content(self, data: Dict[str, Any], section_name: str) -> str:
        """Extract human-readable text from structured data"""
        
        if section_name == "work":
            return f"{data.get('position', '')} at {data.get('name', '')}"
        elif section_name == "education":
            return f"{data.get('studyType', '')} in {data.get('area', '')} from {data.get('institution', '')}"
        elif section_name == "skills":
            return f"{data.get('name', '')} ({data.get('level', '')})"
        else:
            return data.get('description', str(data))
    
    def _update_provider_stats(self, result: str, start_time: datetime):
        """Update provider performance statistics"""
        
        response_time = (datetime.now() - start_time).total_seconds()
        
        # Update the last used provider's stats
        for provider in self.llm_providers.keys():
            if result == 'success':
                self.provider_stats[provider]['success'] += 1
            else:
                self.provider_stats[provider]['failure'] += 1
            
            # Update average response time
            current_avg = self.provider_stats[provider]['avg_response_time']
            total_requests = self.provider_stats[provider]['success'] + self.provider_stats[provider]['failure']
            
            if total_requests > 0:
                self.provider_stats[provider]['avg_response_time'] = (
                    (current_avg * (total_requests - 1) + response_time) / total_requests
                )
    
    def get_health_status(self) -> Dict[str, Any]:
        """Get health status of the AI agent"""
        
        return {
            'status': 'healthy' if self.llm_providers else 'degraded',
            'providers_available': len(self.llm_providers),
            'provider_stats': self.provider_stats,
            'rag_service': self.rag_service.health_check() if self.rag_service else 'N/A',
            'qa_service': 'available' if self.qa_service else 'N/A'
        } 
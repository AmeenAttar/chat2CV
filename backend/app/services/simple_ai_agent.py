#!/usr/bin/env python3
"""
Simple AI Agent for Resume Generation
Direct LLM calls with Gemini, no complex dependencies
"""

import os
import json
import asyncio
from typing import Dict, Any, Optional, List
from datetime import datetime
import logging

# Try multiple LLM providers for redundancy
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
from app.services.database_service import DatabaseService
from app.models.resume import (
    ResumeData, 
    ResumeCompletenessSummary, 
    SectionStatus,
    WorkExperience,
    Education,
    Skill,
    Project
)

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SimpleResumeAgent:
    """
    Simple, reliable AI agent for resume generation
    Uses direct LLM calls with multiple fallback strategies
    """
    
    def __init__(self, db_service: Optional[DatabaseService] = None):
        self.db_service = db_service
        
        # Initialize LLM providers
        self.llm_providers = self._initialize_llm_providers()
        
        # Load knowledge base content (simple file reads)
        self.knowledge_base = {
            'template_guidelines': {
                1: "Use professional tone and clear structure",
                2: "Focus on achievements and quantifiable results",
                3: "Emphasize leadership and strategic thinking",
                4: "Highlight technical expertise and innovation"
            },
            'section_best_practices': {
                'basics': "Include name, email, phone, location. Add LinkedIn if professional. Keep summary concise (2-3 sentences).",
                'work': "Focus on achievements, use action verbs, quantify results. Include company, position, dates, and key accomplishments.",
                'education': "Include institution, degree, field of study, graduation date. Add GPA if 3.5+.",
                'skills': "Group by category (Technical, Soft Skills, Languages). Include proficiency levels where relevant.",
                'projects': "Describe the project, your role, technologies used, and outcomes. Quantify impact where possible.",
                'awards': "Include award name, issuing organization, date, and brief description of achievement.",
                'languages': "List language and proficiency level (Native, Fluent, Intermediate, Basic).",
                'interests': "Include professional interests and hobbies that show personality and cultural fit.",
                'volunteer': "Include organization, role, dates, and impact. Focus on leadership and community involvement.",
                'publications': "Include title, publication venue, date, and brief description of research/work.",
                'references': "Include name, title, company, and contact information. Get permission before including."
            },
            'action_verbs': {
                'general': "Developed, Built, Improved, Led, Created, Implemented, Managed, Designed, Optimized, Delivered",
                'technical': "Architected, Coded, Debugged, Deployed, Integrated, Migrated, Refactored, Scaled, Secured, Tested",
                'leadership': "Directed, Guided, Mentored, Orchestrated, Oversaw, Supervised, Trained, Coordinated, Facilitated, Empowered"
            }
        }
        
        # Track performance
        self.stats = {
            'total_requests': 0,
            'successful_requests': 0,
            'fallback_used': 0,
            'errors': 0
        }
        
        logger.info(f"✅ SimpleResumeAgent initialized with {len(self.llm_providers)} LLM providers")
    
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
    
    def _load_knowledge_base(self) -> Dict[str, str]:
        """Load knowledge base content from files"""
        knowledge_base = {}
        
        # Simple knowledge base content (no complex RAG)
        knowledge_base['template_guidelines'] = {
            1: "Professional template: Clean, conservative design. Use formal tone, focus on achievements, quantify results.",
            2: "Modern template: Contemporary, innovative design. Use forward-thinking language, emphasize innovation.",
            3: "Creative template: Bold, artistic design. Use creative language, emphasize artistic skills.",
            4: "Minimalist template: Simple, clean design. Use concise language, focus on essential information.",
            5: "Executive template: Sophisticated, professional design. Use strategic language, emphasize leadership."
        }
        
        knowledge_base['section_best_practices'] = {
            'work_experience': "Focus on achievements and measurable results. Use strong action verbs. Quantify impact with numbers and percentages.",
            'education': "Include degree, institution, graduation date. Add GPA if 3.5+. Include relevant coursework for recent graduates.",
            'skills': "Group by category (Technical, Soft Skills, Languages). Include proficiency levels. Focus on relevant skills.",
            'projects': "Describe impact and technologies used. Use metrics to show results. Highlight technical skills.",
            'basics': "Include name, email, phone, location. Add LinkedIn if professional. Keep summary concise (2-3 sentences)."
        }
        
        knowledge_base['action_verbs'] = {
            'general': "Managed, Led, Developed, Implemented, Created, Designed, Analyzed, Optimized, Increased, Improved, Coordinated, Established, Generated, Streamlined, Enhanced",
            'tech': "Developed, Engineered, Implemented, Architected, Deployed, Optimized, Scaled, Debugged, Refactored, Automated, Built, Created, Designed, Integrated, Maintained",
            'finance': "Analyzed, Managed, Prepared, Audited, Forecasted, Optimized, Streamlined, Implemented, Monitored, Evaluated, Budgeted, Controlled, Reported, Advised, Structured",
            'marketing': "Increased, Generated, Developed, Executed, Managed, Coordinated, Launched, Optimized, Analyzed, Drove, Created, Designed, Implemented, Measured, Improved"
        }
        
        return knowledge_base
    
    def _create_prompt(self, section_name: str, raw_input: str, template_id: int, 
                      current_resume_data: Optional[ResumeData] = None) -> str:
        """Create a comprehensive, context-aware prompt"""
        
        # Get template guidelines
        template_guidelines = self.knowledge_base['template_guidelines'].get(template_id, "Use professional tone and clear structure")
        
        # Get section best practices
        best_practices = self.knowledge_base['section_best_practices'].get(section_name, "Focus on achievements and use strong action verbs")
        
        # Get action verbs
        action_verbs = self.knowledge_base['action_verbs']['general']
        
        # Get current resume context
        current_context = {}
        if current_resume_data and current_resume_data.json_resume:
            current_context = current_resume_data.json_resume.dict()
        
        # Create section-specific JSON format
        json_format = self._get_json_format_for_section(section_name)
        
        prompt = f"""
You are an expert resume writer specializing in JSON Resume format. Convert the user input into professional, structured resume content.

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
    
    def _get_json_format_for_section(self, section_name: str) -> str:
        """Get JSON format requirements for specific section"""
        
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
                    "keywords": ["string (related skills)"]
                },
                "example": {
                    "name": "Python",
                    "level": "Advanced",
                    "keywords": ["Django", "Flask", "Pandas", "NumPy"]
                }
            },
            "projects": {
                "structure": {
                    "name": "string (project name)",
                    "description": "string (project description)",
                    "highlights": ["string (key feature 1)", "string (key feature 2)"],
                    "keywords": ["string (technology 1)", "string (technology 2)"],
                    "startDate": "string (YYYY-MM)",
                    "endDate": "string (YYYY-MM or 'Present')",
                    "url": "string (project URL if available)"
                },
                "example": {
                    "name": "E-commerce Platform",
                    "description": "Full-stack web application for online retail",
                    "highlights": [
                        "Implemented secure payment processing with Stripe",
                        "Built responsive UI using React and Material-UI"
                    ],
                    "keywords": ["React", "Node.js", "MongoDB", "Stripe"],
                    "startDate": "2023-01",
                    "endDate": "2023-06",
                    "url": "https://github.com/user/ecommerce-platform"
                }
            },
            "basics": {
                "structure": {
                    "name": "string (full name)",
                    "email": "string (email address)",
                    "phone": "string (phone number)",
                    "summary": "string (professional summary)",
                    "location": {
                        "address": "string (street address)",
                        "city": "string (city)",
                        "region": "string (state/province)",
                        "postalCode": "string (zip code)",
                        "countryCode": "string (country code)"
                    }
                },
                "example": {
                    "name": "John Doe",
                    "email": "john.doe@email.com",
                    "phone": "+1-555-123-4567",
                    "summary": "Experienced software engineer with 5+ years developing scalable web applications",
                    "location": {
                        "address": "123 Main St",
                        "city": "San Francisco",
                        "region": "CA",
                        "postalCode": "94105",
                        "countryCode": "US"
                    }
                }
            }
        }
        
        if section_name in formats:
            format_info = formats[section_name]
            return f"""
STRUCTURE:
{json.dumps(format_info['structure'], indent=2)}

EXAMPLE:
{json.dumps(format_info['example'], indent=2)}
"""
        else:
            return f"Return a JSON object for {section_name} section with appropriate fields."
    
    async def generate_section(self, template_id: int, section_name: str, raw_input: str, 
                              current_resume_data: Optional[ResumeData] = None) -> Dict[str, Any]:
        """Generate resume section with multiple fallback strategies"""
        
        self.stats['total_requests'] += 1
        start_time = datetime.now()
        
        try:
            # Create prompt
            prompt = self._create_prompt(section_name, raw_input, template_id, current_resume_data)
            
            # Try LLM providers
            result = await self._try_llm_providers(prompt, section_name)
            
            if result:
                # Process and validate result
                processed_result = self._process_and_validate_result(result, section_name, raw_input)
                self.stats['successful_requests'] += 1
                return processed_result
            else:
                # Use rule-based fallback
                logger.warning("⚠️  All LLM providers failed, using rule-based fallback")
                self.stats['fallback_used'] += 1
                return self._rule_based_fallback(section_name, raw_input, template_id)
                
        except Exception as e:
            logger.error(f"❌ Generation failed: {e}")
            self.stats['errors'] += 1
            
            # Final fallback
            return self._rule_based_fallback(section_name, raw_input, template_id)
    
    async def _try_llm_providers(self, prompt: str, section_name: str) -> Optional[str]:
        """Try multiple LLM providers with intelligent fallback"""
        
        for provider_name, provider in self.llm_providers.items():
            try:
                logger.info(f"🔄 Trying {provider_name} provider...")
                result = await self._call_llm_provider(provider_name, provider, prompt)
                
                logger.info(f"📝 {provider_name} raw response: {result[:200]}...")
                
                if result and self._validate_llm_response(result, section_name):
                    logger.info(f"✅ {provider_name} provider succeeded")
                    return result
                else:
                    logger.warning(f"⚠️  {provider_name} response validation failed")
                    
            except Exception as e:
                logger.warning(f"⚠️  {provider_name} provider failed: {e}")
        
        return None
    
    async def _call_llm_provider(self, provider_name: str, provider: Any, prompt: str) -> str:
        """Call specific LLM provider"""
        
        if provider_name == 'gemini':
            # Gemini is synchronous, so we run it in a thread pool with timeout
            loop = asyncio.get_event_loop()
            try:
                response = await asyncio.wait_for(
                    loop.run_in_executor(None, provider.generate_content, prompt),
                    timeout=30.0
                )
                return response.text
            except asyncio.TimeoutError:
                logger.warning("⚠️  Gemini request timed out")
                raise Exception("Gemini request timed out")
        
        elif provider_name == 'openai':
            response = provider.chat.completions.create(
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
        
        # Clean response from markdown code blocks
        response_clean = response.strip()
        
        # Remove markdown code blocks
        if response_clean.startswith('```json'):
            response_clean = response_clean[7:]  # Remove ```json
        if response_clean.startswith('```'):
            response_clean = response_clean[3:]  # Remove ```
        if response_clean.endswith('```'):
            response_clean = response_clean[:-3]  # Remove ```
        
        response_clean = response_clean.strip()
        
        # Check if response looks like JSON
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
        
        try:
            # Clean response from markdown code blocks
            result_clean = result.strip()
            
            # Remove markdown code blocks
            if result_clean.startswith('```json'):
                result_clean = result_clean[7:]  # Remove ```json
            if result_clean.startswith('```'):
                result_clean = result_clean[3:]  # Remove ```
            if result_clean.endswith('```'):
                result_clean = result_clean[:-3]  # Remove ```
            
            result_clean = result_clean.strip()
            
            # Parse JSON response
            parsed_data = json.loads(result_clean)
            
            # Basic validation
            if self._validate_section_data(parsed_data, section_name):
                return {
                    'status': 'success',
                    'updated_section': json.dumps(parsed_data),
                    'rephrased_content': self._extract_text_content(parsed_data, section_name),
                    'quality_score': 0.8
                }
            else:
                logger.warning("⚠️  Data validation failed, using fallback")
                return self._rule_based_fallback(section_name, raw_input)
                
        except json.JSONDecodeError as e:
            logger.warning(f"⚠️  JSON parsing failed: {e}")
            return self._rule_based_fallback(section_name, raw_input)
    
    def _validate_section_data(self, data: Dict[str, Any], section_name: str) -> bool:
        """Basic validation of section data"""
        
        if not isinstance(data, dict):
            return False
        
        # Check for required fields based on section
        required_fields = {
            'work_experience': ['name', 'position'],
            'education': ['institution', 'studyType', 'area'],
            'skills': ['name'],
            'projects': ['name', 'description']
        }
        
        required = required_fields.get(section_name, [])
        return all(field in data for field in required)
    
    def _rule_based_fallback(self, section_name: str, raw_input: str, template_id: int = 1) -> Dict[str, Any]:
        """Rule-based fallback when AI providers fail"""
        
        logger.info(f"🔄 Using rule-based fallback for {section_name}")
        
        try:
            if section_name == "work":
                result = self._extract_work_experience(raw_input)
            elif section_name == "education":
                result = self._extract_education(raw_input)
            elif section_name == "skills":
                result = self._extract_skills(raw_input)
            elif section_name == "projects":
                result = self._extract_projects(raw_input)
            elif section_name == "basics":
                result = self._extract_basics(raw_input)
            else:
                result = self._extract_generic_section(raw_input, section_name)
            
            return {
                'status': 'fallback_success',
                'updated_section': json.dumps(result),
                'rephrased_content': self._extract_text_content(result, section_name),
                'quality_score': 0.6
            }
            
        except Exception as e:
            logger.error(f"❌ Rule-based fallback failed: {e}")
            return {
                'status': 'error',
                'updated_section': '{}',
                'rephrased_content': raw_input,
                'quality_score': 0.0
            }
    
    def _extract_work_experience(self, raw_input: str) -> Dict[str, Any]:
        """Extract work experience using rule-based approach - only extract what's provided"""
        
        # Simple extraction logic - only extract what's explicitly mentioned
        lines = raw_input.split('.')
        
        # Try to extract company and position
        company = None
        position = None
        
        for line in lines:
            line = line.strip().lower()
            if 'at' in line:
                parts = line.split('at')
                if len(parts) >= 2:
                    position = parts[0].strip().title()
                    company = parts[1].strip().title()
                    break
        
        # Only create work experience if we have the essential information
        if company and position:
            work_data = {
                "name": company,
                "position": position,
                "summary": raw_input,
                "highlights": [raw_input]
            }
            
            # Only add dates if they're explicitly mentioned
            # Don't assume dates - let Voiceflow ask for them
            return work_data
        else:
            # Return empty if we don't have enough information
            return {}
    
    def _extract_education(self, raw_input: str) -> Dict[str, Any]:
        """Extract education using rule-based approach - only extract what's provided"""
        
        institution = None
        study_type = None
        area = None
        
        # Simple extraction - only what's explicitly mentioned
        if 'bachelor' in raw_input.lower():
            study_type = "Bachelor's"
        elif 'master' in raw_input.lower():
            study_type = "Master's"
        elif 'phd' in raw_input.lower() or 'doctorate' in raw_input.lower():
            study_type = "PhD"
        
        # Try to extract institution name
        if 'university' in raw_input.lower() or 'college' in raw_input.lower():
            # Simple extraction - could be improved
            words = raw_input.split()
            for i, word in enumerate(words):
                if word.lower() in ['university', 'college', 'institute']:
                    if i > 0:
                        institution = words[i-1] + " " + word
                    break
        
        # Only create education if we have essential information
        if institution or study_type:
            edu_data = {
                "institution": institution or "Institution Name",
                "studyType": study_type or "Degree",
                "area": area or "Field of Study"
            }
            
            # Don't assume dates - let Voiceflow ask for them
            return edu_data
        else:
            return {}
    
    def _extract_skills(self, raw_input: str) -> Dict[str, Any]:
        """Extract skills using rule-based approach - only extract what's provided"""
        
        skills = raw_input.split(',')
        valid_skills = [skill.strip() for skill in skills if skill.strip()]
        
        if valid_skills:
            return {
                "name": valid_skills[0],
                "level": "Intermediate",  # Default level
                "keywords": valid_skills[1:] if len(valid_skills) > 1 else []
            }
        else:
            return {}
    
    def _extract_projects(self, raw_input: str) -> Dict[str, Any]:
        """Extract projects using rule-based approach - only extract what's provided"""
        
        # Try to extract project name
        project_name = "Project"
        if 'project' in raw_input.lower():
            # Simple extraction
            words = raw_input.split()
            for i, word in enumerate(words):
                if word.lower() == 'project':
                    if i > 0:
                        project_name = words[i-1]
                    break
        
        return {
            "name": project_name,
            "description": raw_input,
            "highlights": [raw_input]
            # Don't assume dates - let Voiceflow ask for them
        }
    
    def _extract_generic_section(self, raw_input: str, section_name: str) -> Dict[str, Any]:
        """Extract generic section data"""
        
        return {
            "name": section_name.replace('_', ' ').title(),
            "description": raw_input,
            "content": raw_input
        }
    
    def _extract_basics(self, raw_input: str) -> Dict[str, Any]:
        """Extract basic information using rule-based approach"""
        
        # Simple extraction for basics
        basics_data = {
            "name": None,
            "email": None,
            "phone": None,
            "summary": raw_input
        }
        
        # Try to extract email
        import re
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        email_match = re.search(email_pattern, raw_input)
        if email_match:
            basics_data["email"] = email_match.group()
        
        # Try to extract phone
        phone_pattern = r'(\+?1?[-.\s]?)?\(?([0-9]{3})\)?[-.\s]?([0-9]{3})[-.\s]?([0-9]{4})'
        phone_match = re.search(phone_pattern, raw_input)
        if phone_match:
            basics_data["phone"] = phone_match.group()
        
        # Try to extract name (simple approach)
        words = raw_input.split()
        if len(words) >= 2:
            basics_data["name"] = f"{words[0]} {words[1]}"
        
        # Remove None values
        basics_data = {k: v for k, v in basics_data.items() if v is not None}
        
        return basics_data
    
    def _extract_text_content(self, data: Dict[str, Any], section_name: str) -> str:
        """Extract human-readable text from structured data"""
        
        if section_name == "work":
            return f"{data.get('position', '')} at {data.get('name', '')}"
        elif section_name == "education":
            return f"{data.get('studyType', '')} in {data.get('area', '')} from {data.get('institution', '')}"
        elif section_name == "skills":
            return f"{data.get('name', '')} ({data.get('level', '')})"
        elif section_name == "basics":
            return f"{data.get('name', '')} - {data.get('email', '')}"
        else:
            return data.get('description', str(data))
    
    def get_health_status(self) -> Dict[str, Any]:
        """Get health status of the AI agent"""
        
        return {
            'status': 'healthy' if self.llm_providers else 'degraded',
            'providers_available': len(self.llm_providers),
            'stats': self.stats,
            'knowledge_base_loaded': len(self.knowledge_base) > 0
        } 
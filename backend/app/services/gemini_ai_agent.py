#!/usr/bin/env python3
"""
Gemini AI Agent for Resume Generation
Replaces OpenAI to avoid rate limits and costs
"""

import os
import json
from typing import Dict, Any, Optional
import google.generativeai as genai
from app.models.resume import ResumeData, ResumeCompletenessSummary, JSONResume
from app.services.template_service import TemplateService

class GeminiResumeAgent:
    """
    Resume generation agent using Google Gemini
    """
    
    def __init__(self):
        # Configure Gemini
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            print("⚠️  GEMINI_API_KEY not set, using mock responses")
            self.model = None
        else:
            genai.configure(api_key=api_key)
            self.model = genai.GenerativeModel('gemini-1.5-flash')
        
        self.template_service = TemplateService()
        
    def generate_section(self, template_id: int, section_name: str, raw_input: str, 
                        current_resume_data: Optional[ResumeData] = None) -> Dict[str, Any]:
        """Generate resume section using Gemini"""
        
        if not self.model:
            # Mock response when no API key
            return self._generate_mock_response(section_name, raw_input)
        
        try:
            # Get template guidelines
            guidelines = self.template_service.get_template_style_guidelines(template_id)
            
            # Create prompt
            prompt = self._create_prompt(section_name, raw_input, guidelines, current_resume_data)
            
            # Generate response
            response = self.model.generate_content(prompt)
            
            # Parse response
            return self._parse_response(response.text, section_name)
            
        except Exception as e:
            print(f"⚠️  Gemini generation failed: {e}")
            return self._generate_mock_response(section_name, raw_input)
    
    def _create_prompt(self, section_name: str, raw_input: str, guidelines: Dict[str, Any], 
                      current_resume_data: Optional[ResumeData] = None) -> str:
        """Create prompt for Gemini"""
        
        # Get current resume context
        current_context = {}
        if current_resume_data and current_resume_data.json_resume:
            current_context = current_resume_data.json_resume.dict()
        
        # Create context-aware instructions
        context_instructions = self._get_context_instructions(section_name, current_context)
        
        prompt = f"""
You are a professional resume writer specializing in JSON Resume format. Generate content for the '{section_name}' section.

Template Guidelines:
- Tone: {guidelines.get('tone', 'professional')}
- Emphasis: {guidelines.get('emphasis', 'content over design')}
- Format: JSON Resume standard

User Input: "{raw_input}"

Current Resume Context:
{json.dumps(current_context, indent=2)}

{context_instructions}

Instructions:
1. Convert the user input into professional resume content
2. Follow the template guidelines and maintain consistency with existing content
3. Return ONLY a valid JSON object with the processed content
4. Use JSON Resume schema format exactly as specified
5. Ensure all dates are in YYYY-MM format (or YYYY for education)
6. Use action verbs and quantify achievements where possible
7. OMIT any fields that are empty or not provided - do not include null values

Expected JSON structure for {section_name}:
{self._get_section_structure(section_name)}

Generate the content now. Return ONLY the JSON object:
"""
        return prompt
    
    def _get_section_structure(self, section_name: str) -> str:
        """Get expected JSON structure for a section"""
        structures = {
            "work": """{
  "work": [
    {
      "name": "Company Name",
      "position": "Job Title",
      "startDate": "YYYY-MM",
      "endDate": "YYYY-MM or Present",
      "summary": "Brief description of role and responsibilities",
      "highlights": ["Achievement 1", "Achievement 2"]
    }
  ]
}""",
            "education": """{
  "education": [
    {
      "institution": "University Name",
      "area": "Field of Study",
      "studyType": "Bachelor's",
      "startDate": "YYYY",
      "endDate": "YYYY"
    }
  ]
}""",
            "skills": """{
  "skills": [
    {
      "name": "Skill Name",
      "level": "Expert/Proficient/Beginner",
      "keywords": ["related", "terms"]
    }
  ]
}""",
            "projects": """{
  "projects": [
    {
      "name": "Project Name",
      "description": "Project description",
      "highlights": ["achievement 1", "achievement 2"],
      "keywords": ["technology", "framework"],
      "startDate": "YYYY-MM",
      "endDate": "YYYY-MM"
    }
  ]
}""",
            "basics": """{
  "basics": {
    "name": "Full Name",
    "email": "email@example.com",
    "phone": "+1-234-567-8900",
    "summary": "Professional summary (2-3 sentences)",
    "location": {
      "city": "City",
      "region": "State/Province",
      "countryCode": "US"
    }
  }
}"""
        }
        return structures.get(section_name, "{}")
    
    def _get_context_instructions(self, section_name: str, current_context: Dict[str, Any]) -> str:
        """Generate context-aware instructions based on current resume data"""
        instructions = []
        
        # Check if this is the first section being added
        has_any_content = any(
            current_context.get(key) and current_context[key] 
            for key in ['basics', 'work', 'education', 'skills', 'projects']
        )
        
        if not has_any_content:
            instructions.append("This is the first section being added to the resume. Set a professional foundation.")
        
        # Section-specific context instructions
        if section_name == "basics":
            if current_context.get('basics', {}).get('name'):
                instructions.append("Maintain consistency with existing personal information.")
            else:
                instructions.append("Create a complete personal details section with name, contact info, and professional summary.")
        
        elif section_name == "work":
            existing_work = current_context.get('work', [])
            if existing_work:
                instructions.append(f"Add to existing {len(existing_work)} work experience entries. Maintain consistent formatting and detail level.")
            else:
                instructions.append("Create the first work experience entry. Use strong action verbs and quantify achievements.")
        
        elif section_name == "education":
            existing_education = current_context.get('education', [])
            if existing_education:
                instructions.append(f"Add to existing {len(existing_education)} education entries. Maintain consistent formatting.")
            else:
                instructions.append("Create the first education entry. Include relevant academic achievements.")
        
        elif section_name == "skills":
            existing_skills = current_context.get('skills', [])
            if existing_skills:
                instructions.append(f"Add to existing {len(existing_skills)} skill categories. Avoid duplicates and maintain consistent skill levels.")
            else:
                instructions.append("Create the first skills section. Group related skills and specify proficiency levels.")
        
        elif section_name == "projects":
            existing_projects = current_context.get('projects', [])
            if existing_projects:
                instructions.append(f"Add to existing {len(existing_projects)} project entries. Maintain consistent detail level and formatting.")
            else:
                instructions.append("Create the first project entry. Include technologies used and measurable outcomes.")
        
        # General consistency instructions
        if has_any_content:
            instructions.append("Maintain consistency with existing content style, tone, and detail level.")
        
        return "\n".join(instructions) if instructions else ""
    
    def _clean_null_values(self, data: Any) -> Any:
        """Remove null values from data to comply with JSON Resume schema"""
        if isinstance(data, dict):
            cleaned = {}
            for key, value in data.items():
                if value is not None:
                    cleaned[key] = self._clean_null_values(value)
            return cleaned
        elif isinstance(data, list):
            return [self._clean_null_values(item) for item in data if item is not None]
        else:
            return data
    
    def _parse_response(self, response_text: str, section_name: str) -> Dict[str, Any]:
        """Parse Gemini response into structured format"""
        try:
            # Try to extract JSON from response
            if "```json" in response_text:
                json_start = response_text.find("```json") + 7
                json_end = response_text.find("```", json_start)
                json_str = response_text[json_start:json_end].strip()
            elif "```" in response_text:
                # Handle other code blocks
                json_start = response_text.find("```") + 3
                json_end = response_text.find("```", json_start)
                json_str = response_text[json_start:json_end].strip()
            else:
                # Look for JSON-like content
                start = response_text.find("{")
                end = response_text.rfind("}") + 1
                if start >= 0 and end > start:
                    json_str = response_text[start:end]
                else:
                    raise ValueError("No JSON content found in response")
            
            parsed_data = json.loads(json_str)
            
            # Clean up null values to comply with JSON Resume schema
            cleaned_data = self._clean_null_values(parsed_data)
            
            # Return the parsed data in the correct format for the main endpoint
            # The main endpoint expects the full section structure, not just the content
            return {
                "status": "success",
                "updated_section": json.dumps(cleaned_data, indent=2),
                "rephrased_content": response_text,
                "resume_completeness_summary": self._update_completeness(section_name)
            }
            
        except Exception as e:
            print(f"⚠️  Failed to parse Gemini response: {e}")
            print(f"Response text: {response_text[:200]}...")
            return self._generate_mock_response(section_name, response_text)
    
    def _generate_mock_response(self, section_name: str, raw_input: str) -> Dict[str, Any]:
        """Generate mock response when API is not available"""
        
        mock_content = {
            "work": {
                "work": [{
                    "name": "Company",
                    "position": "Position",
                    "startDate": "2020-01",
                    "endDate": "2023-01",
                    "summary": f"Processed: {raw_input}",
                    "highlights": ["Achievement 1", "Achievement 2"]
                }]
            },
            "education": {
                "education": [{
                    "institution": "University",
                    "area": "Field of Study",
                    "studyType": "Bachelor's",
                    "startDate": "2016",
                    "endDate": "2020"
                }]
            },
            "skills": {
                "skills": [{
                    "name": "Skill",
                    "level": "Proficient",
                    "keywords": ["keyword1", "keyword2"]
                }]
            },
            "projects": {
                "projects": [{
                    "name": "Project",
                    "description": f"Project description: {raw_input}",
                    "highlights": ["Feature 1", "Feature 2"],
                    "keywords": ["tech1", "tech2"]
                }]
            },
            "basics": {
                "basics": {
                    "name": "Your Name",
                    "email": "email@example.com",
                    "phone": "Phone",
                    "summary": f"Professional summary: {raw_input}",
                    "location": {
                        "city": "City",
                        "region": "State"
                    }
                }
            }
        }
        
        content = mock_content.get(section_name, {})
        
        return {
            "status": "success",
            "updated_section": json.dumps(content, indent=2),
            "rephrased_content": f"Mock processed content for {section_name}: {raw_input}",
            "resume_completeness_summary": self._update_completeness(section_name),
            "resume_data": None
        }
    
    def _update_completeness(self, section_name: str) -> ResumeCompletenessSummary:
        """Update completeness summary"""
        summary = ResumeCompletenessSummary()
        
        # Map section names to completeness fields
        section_mapping = {
            "basics": "basics",
            "work": "work_experience", 
            "education": "education",
            "skills": "skills",
            "projects": "projects"
        }
        
        if section_name in section_mapping:
            setattr(summary, section_mapping[section_name], "complete")
        
        return summary 
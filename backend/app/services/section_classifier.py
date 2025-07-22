import os
from typing import Optional
import logging

# Try to import LLM providers
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

logger = logging.getLogger(__name__)

SECTION_LIST = [
    'basics', 'work', 'education', 'skills', 'projects',
    'awards', 'languages', 'interests', 'volunteer',
    'publications', 'references'
]

def keyword_infer_section(raw_input: str) -> str:
    text = raw_input.lower()
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
    return "basics"

def llm_infer_section_from_input(raw_input: str, current_resume_data: Optional[dict] = None) -> str:
    """Use an LLM to classify which section the input belongs to. Fallback to keyword method if LLM unavailable."""
    prompt = f"""
Given the following user input and current resume context, which JSON Resume section does this input best belong to? Respond with only the section name from this list: {SECTION_LIST}.
User input: \"{raw_input}\"
Resume context: {current_resume_data if current_resume_data else '{}'}
"""
    # Try Gemini
    if GEMINI_AVAILABLE:
        try:
            api_key = os.getenv("GEMINI_API_KEY")
            if api_key:
                genai.configure(api_key=api_key)
                model = genai.GenerativeModel('gemini-1.5-flash')
                response = model.generate_content(prompt)
                answer = response.text.strip().lower()
                for section in SECTION_LIST:
                    if section in answer:
                        return section
        except Exception as e:
            logger.warning(f"Gemini LLM section classification failed: {e}")
    # Try OpenAI
    if OPENAI_AVAILABLE:
        try:
            api_key = os.getenv("OPENAI_API_KEY")
            if api_key:
                client = OpenAI(api_key=api_key)
                completion = client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[{"role": "user", "content": prompt}],
                    temperature=0.0,
                    max_tokens=10
                )
                answer = completion.choices[0].message.content.strip().lower()
                for section in SECTION_LIST:
                    if section in answer:
                        return section
        except Exception as e:
            logger.warning(f"OpenAI LLM section classification failed: {e}")
    # Fallback to keyword method
    return keyword_infer_section(raw_input) 
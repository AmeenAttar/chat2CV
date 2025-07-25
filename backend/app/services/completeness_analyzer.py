#!/usr/bin/env python3
"""
Smart Completeness Analyzer for Voiceflow Integration
Provides conversational intelligence rather than rigid rules
"""

from typing import Dict, List, Any, Optional
from app.models.resume import JSONResume

class QualityChecklistGenerator:
    """Generates a per-field quality checklist for a JSON Resume dict, supporting skipped fields."""
    def __init__(self):
        pass

    def detect_skipped_fields(self, user_input: str) -> set:
        """Detect which fields the user wants to skip based on input phrases and field keywords."""
        skip_phrases = [
            'skip',
            "don’t want to provide",
            "don't want to provide",
            "not comfortable sharing",
            "prefer not to say",
            "no comment",
            "leave blank"
        ]
        field_keywords = {
            'name': ['name', 'full name'],
            'email': ['email', 'e-mail'],
            'phone': ['phone', 'phone number'],
            'summary': ['summary', 'about me', 'bio'],
            'position': ['position', 'job title', 'role'],
            'company': ['company', 'employer', 'organization'],
            'institution': ['institution', 'university', 'college', 'school'],
            'degree': ['degree', 'studytype', 'qualification'],
            'area': ['area', 'field', 'major', 'specialization'],
            'skills': ['skills', 'technologies', 'tools'],
            'projects': ['projects', 'project'],
            'awards': ['awards', 'certifications', 'certification'],
            'languages': ['languages', 'language'],
            'interests': ['interests', 'hobbies'],
            'volunteer': ['volunteer', 'volunteering'],
            'publications': ['publications', 'publication'],
            'references': ['references', 'referee']
        }
        lowered = user_input.lower()
        skipped = set()
        for phrase in skip_phrases:
            if phrase in lowered:
                for field, keywords in field_keywords.items():
                    for keyword in keywords:
                        if keyword in lowered:
                            skipped.add(field)
                            # Add full path for basics fields
                            if field in ['name', 'email', 'phone', 'summary', 'location', 'profiles']:
                                skipped.add(f"basics.{field}")
        return skipped

    def generate(self, json_resume: dict, skipped_fields: set = None) -> dict:
        checklist = {}
        skipped_fields = skipped_fields or set()
        def check_field(path, value):
            if path in skipped_fields:
                return "skipped"
            if value is None or (isinstance(value, str) and not value.strip()):
                return "missing"
            if isinstance(value, list) and not value:
                return "missing"
            # Add more sophisticated checks here (e.g., email format, date plausibility, length)
            if isinstance(value, str) and len(value.strip()) < 3:
                return "low_quality"
            return "ok"
        def walk(obj, path=""):
            if isinstance(obj, dict):
                # Always check for skipped fields, even if missing from dict
                for k in set(list(obj.keys()) + [f for f in skipped_fields if f.startswith(path + ".") or (not path and f.count(".") == 1)]):
                    v = obj.get(k, None)
                    full_path = f"{path}.{k}" if path else k
                    checklist[full_path] = check_field(full_path, v)
                    walk(v, full_path)
            elif isinstance(obj, list):
                for idx, item in enumerate(obj):
                    full_path = f"{path}[{idx}]"
                    checklist[full_path] = check_field(full_path, item)
                    walk(item, full_path)
        walk(json_resume)
        # Also add any skipped fields that were not present in the data
        for skipped in skipped_fields:
            if skipped not in checklist:
                checklist[skipped] = "skipped"
        return checklist

class CompletenessAnalyzer:
    """Analyzes resume completeness and provides smart guidance for Voiceflow"""
    
    def __init__(self):
        # Section priority mapping (higher number = higher priority)
        self.section_priority = {
            "basics": 1,
            "work": 2,
            "education": 3,
            "skills": 4,
            "projects": 5,
            "awards": 6,
            "languages": 7,
            "interests": 8,
            "volunteer": 9,
            "publications": 10,
            "references": 11
        }
        
        # Required fields for each section
        self.required_fields = {
            "basics": ["name", "email", "summary"],
            "work": ["name", "position"],
            "education": ["institution", "studyType", "area"],
            "skills": ["name"],
            "projects": ["name", "description"]
        }
    
    def analyze_completeness(self, resume_data: JSONResume, template_id: int = 1) -> Dict[str, Any]:
        """Analyze resume and provide smart completeness guidance"""
        
        # Basic section status
        completeness = {}
        
        # Analyze each section
        completeness["basics"] = self._analyze_section("basics", resume_data.basics)
        completeness["work"] = self._analyze_section("work", resume_data.work)
        completeness["education"] = self._analyze_section("education", resume_data.education)
        completeness["skills"] = self._analyze_section("skills", resume_data.skills)
        completeness["projects"] = self._analyze_section("projects", resume_data.projects)
        completeness["awards"] = self._analyze_section("awards", resume_data.awards)
        completeness["languages"] = self._analyze_section("languages", resume_data.languages)
        completeness["interests"] = self._analyze_section("interests", resume_data.interests)
        completeness["volunteer"] = self._analyze_section("volunteer", resume_data.volunteer)
        completeness["publications"] = self._analyze_section("publications", resume_data.publications)
        completeness["references"] = self._analyze_section("references", resume_data.references)
        
        # Generate smart conversational guidance
        completeness["conversation_context"] = self._generate_conversation_context(resume_data, template_id)
        completeness["suggested_topics"] = self._generate_suggested_topics(resume_data, template_id)
        completeness["missing_critical_info"] = self._identify_missing_critical_info(resume_data)
        completeness["conversation_flow_hints"] = self._generate_flow_hints(resume_data, template_id)
        completeness["user_progress_insights"] = self._generate_progress_insights(resume_data, template_id)
        
        return completeness
    
    def _analyze_section(self, section_name: str, section_data: Any) -> Dict[str, Any]:
        """Analyze completeness of a specific section"""
        
        if not section_data:
            return {"status": "not_started", "details": "No data for this section."}
        
        # Section-specific analysis
        if section_name == "basics":
            return self._analyze_basics(section_data)
        elif section_name == "work":
            return self._analyze_work(section_data)
        elif section_name == "education":
            return self._analyze_education(section_data)
        elif section_name == "skills":
            return self._analyze_skills(section_data)
        elif section_name == "projects":
            return self._analyze_projects(section_data)
        elif section_name == "awards":
            return self._analyze_awards(section_data)
        elif section_name == "languages":
            return self._analyze_languages(section_data)
        elif section_name == "interests":
            return self._analyze_interests(section_data)
        elif section_name == "volunteer":
            return self._analyze_volunteer(section_data)
        elif section_name == "publications":
            return self._analyze_publications(section_data)
        elif section_name == "references":
            return self._analyze_references(section_data)
        else:
            return {"status": "not_started", "details": "Unknown section."}
    
    def _analyze_basics(self, basics: Any) -> Dict[str, Any]:
        """Analyze basics section completeness"""
        if not basics:
            return {"status": "not_started", "details": "No basic information provided."}
        
        # Check required fields
        has_name = basics.name is not None and basics.name.strip() != ""
        has_email = basics.email is not None and basics.email.strip() != ""
        has_summary = basics.summary is not None and basics.summary.strip() != ""
        
        if has_name and has_email and has_summary:
            return {"status": "complete", "details": "Basic information is complete."}
        elif has_name or has_email:
            return {"status": "partial", "details": "Basic information is partially complete."}
        else:
            return {"status": "not_started", "details": "Basic information is incomplete."}
    
    def _analyze_work(self, work: List[Any]) -> Dict[str, Any]:
        """Analyze work experience section completeness"""
        if not work or len(work) == 0:
            return {"status": "not_started", "details": "No work experience provided."}
        
        # Check if at least one work experience has required fields
        for job in work:
            has_company = job.name is not None and job.name.strip() != ""
            has_position = job.position is not None and job.position.strip() != ""
            if has_company and has_position:
                return {"status": "complete", "details": "Work experience is complete."}
        
        return {"status": "partial", "details": "Work experience is partially complete."}
    
    def _analyze_education(self, education: List[Any]) -> Dict[str, Any]:
        """Analyze education completeness"""
        if not education:
            return {"status": "not_started", "details": "No education information provided."}
        
        if len(education) >= 1:
            return {"status": "complete", "details": "Education is complete."}
        else:
            return {"status": "incomplete", "details": "Education is incomplete."}
    
    def _analyze_skills(self, skills: List[Any]) -> Dict[str, Any]:
        """Analyze skills completeness"""
        if not skills:
            return {"status": "not_started", "details": "No skills provided."}
        
        if len(skills) >= 5:
            return {"status": "complete", "details": "Skills are complete."}
        elif len(skills) >= 2:
            return {"status": "partial", "details": "Skills are partially complete."}
        else:
            return {"status": "incomplete", "details": "Skills are incomplete."}
    
    def _analyze_projects(self, projects: List[Any]) -> Dict[str, Any]:
        """Analyze projects completeness"""
        if not projects:
            return {"status": "not_started", "details": "No projects provided."}
        
        if len(projects) >= 2:
            return {"status": "complete", "details": "Projects are complete."}
        elif len(projects) == 1:
            return {"status": "partial", "details": "Projects are partially complete."}
        else:
            return {"status": "incomplete", "details": "Projects are incomplete."}
    
    def _analyze_awards(self, awards: List[Any]) -> Dict[str, Any]:
        """Analyze awards section completeness"""
        if not awards or len(awards) == 0:
            return {"status": "not_started", "details": "No awards provided."}
        
        # Check if at least one award has required fields
        for award in awards:
            has_title = award.title is not None and award.title.strip() != ""
            if has_title:
                return {"status": "complete", "details": "Awards are complete."}
        
        return {"status": "partial", "details": "Awards are partially complete."}
    
    def _analyze_volunteer(self, volunteer: List[Any]) -> Dict[str, Any]:
        """Analyze volunteer section completeness"""
        if not volunteer or len(volunteer) == 0:
            return {"status": "not_started", "details": "No volunteer experience provided."}
        
        # Check if at least one volunteer experience has required fields
        for vol in volunteer:
            has_organization = vol.organization is not None and vol.organization.strip() != ""
            has_position = vol.position is not None and vol.position.strip() != ""
            if has_organization and has_position:
                return {"status": "complete", "details": "Volunteer experience is complete."}
        
        return {"status": "partial", "details": "Volunteer experience is partially complete."}
    
    def _analyze_publications(self, publications: List[Any]) -> Dict[str, Any]:
        """Analyze publications section completeness"""
        if not publications or len(publications) == 0:
            return {"status": "not_started", "details": "No publications provided."}
        
        # Check if at least one publication has required fields
        for pub in publications:
            has_name = pub.name is not None and pub.name.strip() != ""
            if has_name:
                return {"status": "complete", "details": "Publications are complete."}
        
        return {"status": "partial", "details": "Publications are partially complete."}
    
    def _analyze_references(self, references: List[Any]) -> Dict[str, Any]:
        """Analyze references section completeness"""
        if not references or len(references) == 0:
            return {"status": "not_started", "details": "No references provided."}
        
        # Check if at least one reference has required fields
        for ref in references:
            has_name = ref.name is not None and ref.name.strip() != ""
            has_reference = ref.reference is not None and ref.reference.strip() != ""
            if has_name and has_reference:
                return {"status": "complete", "details": "References are complete."}
        
        return {"status": "partial", "details": "References are partially complete."}
    
    def _analyze_languages(self, languages: List[Any]) -> Dict[str, Any]:
        """Analyze languages completeness"""
        if not languages:
            return {"status": "not_started", "details": "No languages provided."}
        
        if len(languages) >= 1:
            return {"status": "complete", "details": "Languages are complete."}
        else:
            return {"status": "incomplete", "details": "Languages are incomplete."}
    
    def _analyze_interests(self, interests: List[Any]) -> Dict[str, Any]:
        """Analyze interests completeness"""
        if not interests:
            return {"status": "not_started", "details": "No interests provided."}
        
        if len(interests) >= 2:
            return {"status": "complete", "details": "Interests are complete."}
        elif len(interests) == 1:
            return {"status": "partial", "details": "Interests are partially complete."}
        else:
            return {"status": "incomplete", "details": "Interests are incomplete."}
    
    def _generate_conversation_context(self, resume_data: JSONResume, template_id: int) -> Dict[str, Any]:
        """Generate context for Voiceflow conversations"""
        context = {
            "resume_stage": self._determine_resume_stage(resume_data),
            "user_experience_level": self._determine_experience_level(resume_data),
            "industry_focus": self._determine_industry_focus(resume_data),
            "template_requirements": self._get_template_requirements(template_id),
            "conversation_tone": self._suggest_conversation_tone(resume_data),
            "user_engagement_level": self._assess_user_engagement(resume_data)
        }
        return context
    
    def _generate_suggested_topics(self, resume_data: JSONResume, template_id: int) -> List[str]:
        """Generate specific suggested topics based on missing information"""
        topics = []
        
        # Check personal details
        if not resume_data.basics:
            topics.append("What's your full name?")
            topics.append("What's your email address?")
            topics.append("What's your phone number?")
            topics.append("Tell me about yourself - what's your professional summary?")
        else:
            if not resume_data.basics.name:
                topics.append("What's your full name?")
            if not resume_data.basics.email:
                topics.append("What's your email address?")
            if not resume_data.basics.phone:
                topics.append("What's your phone number?")
            if not resume_data.basics.summary:
                topics.append("Tell me about yourself - what's your professional summary?")
        
        # Check work experience
        if not resume_data.work:
            topics.append("Tell me about your work experience")
            topics.append("What companies have you worked for?")
        else:
            # Check each work experience for missing details
            for i, work in enumerate(resume_data.work):
                if not work.startDate:
                    topics.append(f"When did you start at {work.name}?")
                if not work.endDate:
                    topics.append(f"When did you leave {work.name}? (or are you still there?)")
                if not work.highlights or len(work.highlights) == 0:
                    topics.append(f"What were your key achievements at {work.name}?")
                if not work.summary:
                    topics.append(f"Can you describe your role at {work.name}?")
        
        # Check education
        if not resume_data.education:
            topics.append("Tell me about your education")
            topics.append("What degrees do you have?")
        else:
            # Check each education for missing details
            for i, edu in enumerate(resume_data.education):
                if not edu.startDate:
                    topics.append(f"When did you start at {edu.institution}?")
                if not edu.endDate:
                    topics.append(f"When did you graduate from {edu.institution}?")
                if not edu.area:
                    topics.append(f"What did you study at {edu.institution}?")
                if not edu.studyType:
                    topics.append(f"What type of degree did you get from {edu.institution}?")
        
        # Check skills
        if not resume_data.skills:
            topics.append("What technical skills do you have?")
            topics.append("What programming languages do you know?")
            topics.append("What tools and technologies are you familiar with?")
        
        # Check projects
        if not resume_data.projects:
            topics.append("Tell me about any projects you've worked on")
            topics.append("What personal or professional projects have you completed?")
        
        # Check awards
        if not resume_data.awards or len(resume_data.awards) == 0:
            topics.append("Do you have any certifications or awards?")
            topics.append("What professional certifications do you hold?")
        
        # Check languages
        if not resume_data.languages:
            topics.append("What languages do you speak?")
            topics.append("Are you fluent in any languages besides English?")
        
        # Check interests
        if not resume_data.interests:
            topics.append("What are your professional interests?")
            topics.append("What industries or technologies interest you?")
        
        return topics[:5]  # Limit to 5 most important topics
    
    def _identify_missing_critical_info(self, resume_data: JSONResume) -> List[str]:
        """Identify what critical information is missing"""
        missing = []
        
        # Check personal details
        if not resume_data.basics:
            missing.append("basics")
        else:
            if not resume_data.basics.name:
                missing.append("name")
            if not resume_data.basics.email:
                missing.append("email")
            if not resume_data.basics.phone:
                missing.append("phone")
            if not resume_data.basics.summary:
                missing.append("summary")
        
        # Check work experience
        if not resume_data.work:
            missing.append("work")
        else:
            # Check each work experience for missing critical fields
            for i, work in enumerate(resume_data.work):
                if not work.startDate:
                    missing.append(f"work_{i+1}_start_date")
                if not work.endDate:
                    missing.append(f"work_{i+1}_end_date")
                if not work.highlights or len(work.highlights) == 0:
                    missing.append(f"work_{i+1}_achievements")
        
        # Check education
        if not resume_data.education:
            missing.append("education")
        else:
            # Check each education for missing critical fields
            for i, edu in enumerate(resume_data.education):
                if not edu.startDate:
                    missing.append(f"education_{i+1}_start_date")
                if not edu.endDate:
                    missing.append(f"education_{i+1}_end_date")
                if not edu.area:
                    missing.append(f"education_{i+1}_field_of_study")
        
        # Check skills
        if not resume_data.skills:
            missing.append("skills")
        
        # Check projects (optional but valuable)
        if not resume_data.projects:
            missing.append("projects")
        
        return missing
    
    def _generate_flow_hints(self, resume_data: JSONResume, template_id: int) -> List[str]:
        """Generate hints for conversation flow"""
        hints = []
        
        # Progress-based hints
        completed_sections = sum(1 for section in [
            resume_data.basics, resume_data.work, resume_data.education, 
            resume_data.skills, resume_data.projects
        ] if section)
        
        if completed_sections == 0:
            hints.append("user_needs_guidance")
            hints.append("start_with_basics")
        elif completed_sections <= 2:
            hints.append("user_is_engaged")
            hints.append("build_momentum")
        elif completed_sections <= 4:
            hints.append("user_is_committed")
            hints.append("polish_details")
        else:
            hints.append("user_is_finishing")
            hints.append("review_and_refine")
        
        # Content-based hints
        if resume_data.work and len(resume_data.work) > 0:
            hints.append("has_experience")
        if resume_data.education and len(resume_data.education) > 0:
            hints.append("has_education")
        if resume_data.skills and len(resume_data.skills) > 0:
            hints.append("has_skills")
        
        return hints
    
    def _generate_progress_insights(self, resume_data: JSONResume, template_id: int) -> Dict[str, Any]:
        """Generate insights about user progress"""
        insights = {
            "completion_percentage": self._calculate_completion_percentage(resume_data),
            "estimated_time_remaining": self._estimate_time_remaining(resume_data),
            "quality_score": self._assess_quality_score(resume_data),
            "next_priority": self._determine_next_priority(resume_data),
            "user_pattern": self._analyze_user_pattern(resume_data)
        }
        return insights
    
    def _determine_resume_stage(self, resume_data: JSONResume) -> str:
        """Determine what stage the resume is in"""
        if not resume_data.basics or not resume_data.basics.name:
            return "initial_setup"
        elif not resume_data.work:
            return "gathering_experience"
        elif not resume_data.education:
            return "adding_education"
        elif not resume_data.skills:
            return "defining_skills"
        elif not resume_data.projects:
            return "adding_projects"
        else:
            return "polishing"
    
    def _determine_experience_level(self, resume_data: JSONResume) -> str:
        """Determine user's experience level"""
        if not resume_data.work:
            return "entry_level"
        
        work_count = len(resume_data.work)
        if work_count <= 1:
            return "entry_level"
        elif work_count <= 3:
            return "mid_level"
        else:
            return "senior_level"
    
    def _determine_industry_focus(self, resume_data: JSONResume) -> str:
        """Determine industry focus based on content"""
        # This would be enhanced with NLP analysis
        return "general"  # Placeholder
    
    def _get_template_requirements(self, template_id: int) -> Dict[str, Any]:
        """Get template-specific requirements"""
        requirements = {
            "required_sections": ["basics", "work", "education"],
            "optional_sections": ["skills", "projects", "awards", "languages", "interests", "volunteer", "publications", "references"],
            "section_priorities": {
                "basics": 1,
                "work": 2,
                "education": 3,
                "skills": 4,
                "projects": 5
            }
        }
        return requirements
    
    def _suggest_conversation_tone(self, resume_data: JSONResume) -> str:
        """Suggest appropriate conversation tone"""
        if not resume_data.basics or not resume_data.basics.name:
            return "welcoming_and_helpful"
        elif not resume_data.work:
            return "encouraging_and_guiding"
        else:
            return "collaborative_and_refining"
    
    def _assess_user_engagement(self, resume_data: JSONResume) -> str:
        """Assess user engagement level"""
        completed_sections = sum(1 for section in [
            resume_data.basics, resume_data.work, resume_data.education, 
            resume_data.skills, resume_data.projects
        ] if section)
        
        if completed_sections == 0:
            return "new_user"
        elif completed_sections <= 2:
            return "exploring"
        elif completed_sections <= 4:
            return "engaged"
        else:
            return "committed"
    
    def _calculate_completion_percentage(self, resume_data: JSONResume) -> float:
        """Calculate overall completion percentage"""
        sections = [
            resume_data.basics, resume_data.work, resume_data.education,
            resume_data.skills, resume_data.projects, resume_data.awards,
            resume_data.languages, resume_data.interests
        ]
        
        completed = sum(1 for section in sections if section)
        return (completed / len(sections)) * 100
    
    def _estimate_time_remaining(self, resume_data: JSONResume) -> int:
        """Estimate time remaining in minutes"""
        completion = self._calculate_completion_percentage(resume_data)
        if completion < 25:
            return 20
        elif completion < 50:
            return 15
        elif completion < 75:
            return 10
        else:
            return 5
    
    def _assess_quality_score(self, resume_data: JSONResume) -> float:
        """Assess the quality of content"""
        # Placeholder - would be enhanced with content analysis
        return 75.0
    
    def _determine_next_priority(self, resume_data: JSONResume) -> str:
        """Determine the next priority section to complete"""
        if not resume_data.basics or not resume_data.basics.name:
            return "basics"
        elif not resume_data.work:
            return "work"
        elif not resume_data.education:
            return "education"
        elif not resume_data.skills:
            return "skills"
        elif not resume_data.projects:
            return "projects"
        else:
            return "polish"
    
    def _analyze_user_pattern(self, resume_data: JSONResume) -> str:
        """Analyze user's pattern of interaction"""
        # Placeholder - would analyze how user provides information
        return "methodical" 
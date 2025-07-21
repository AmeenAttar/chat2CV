#!/usr/bin/env python3
"""
Simple script to view all resume data
"""

import json
from app.database import get_db
from app.models.database_models import Resume, ResumeSection

def view_all_data():
    """Display all resume data"""
    
    for session in get_db():
        print("📊 ALL RESUME DATA")
        print("=" * 60)
        
        # Get all resumes
        resumes = session.query(Resume).all()
        
        for resume in resumes:
            print(f"\n📄 Resume ID: {resume.id}")
            print(f"   Title: {resume.title}")
            print(f"   Template: {resume.template_id}")
            print(f"   User ID: {resume.user_id}")
            print(f"   Created: {resume.created_at}")
            print(f"   Updated: {resume.updated_at}")
            
            # Get sections for this resume
            sections = session.query(ResumeSection).filter(ResumeSection.resume_id == resume.id).all()
            
            if sections:
                print(f"   📝 Sections ({len(sections)}):")
                for section in sections:
                    print(f"\n      🔹 {section.section_name.upper()}")
                    print(f"         Status: {section.status}")
                    print(f"         Created: {section.created_at}")
                    
                    # Original input
                    print(f"         📥 ORIGINAL INPUT:")
                    print(f"            '{section.original_input}'")
                    
                    # AI processed content
                    if section.processed_content:
                        if isinstance(section.processed_content, dict):
                            ai_output = section.processed_content.get('content', 'No content')
                        else:
                            try:
                                content_data = json.loads(section.processed_content)
                                ai_output = content_data.get('content', 'No content')
                            except (json.JSONDecodeError, TypeError):
                                ai_output = str(section.processed_content)
                        
                        print(f"         🤖 AI OUTPUT:")
                        print(f"            '{ai_output}'")
                    else:
                        print(f"         🤖 AI OUTPUT: No content")
                    
                    print(f"         {'─' * 50}")
            else:
                print("   📝 No sections found")
            
            print(f"\n{'=' * 60}")

if __name__ == "__main__":
    view_all_data() 
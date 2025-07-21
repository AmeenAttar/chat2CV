#!/usr/bin/env python3
"""
Script to view resume data showing original input vs AI processed content
"""


import json
from app.services.database_service import DatabaseService
from app.database import get_db
from app.models.database_models import User

def view_resume_data():
    """Display resume data in a readable format"""
    
    for session in get_db():
        db_service = DatabaseService(session)
        
        print("📊 RESUME DATA ANALYSIS")
        print("=" * 50)
        
        # Get all resumes (get first user's resumes as example)
        first_user = db_service.db.query(User).first()
        if first_user:
            resumes = db_service.get_user_resumes(first_user.id)
        else:
            resumes = []
        
        for resume in resumes:
            print(f"\n📄 Resume ID: {resume.id}")
            print(f"   Title: {resume.title}")
            print(f"   Template: {resume.template_id}")
            print(f"   Created: {resume.created_at}")
            print(f"   Updated: {resume.updated_at}")
            
            # Get sections for this resume
            sections = db_service.get_resume_sections(resume.id)
            
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
                        try:
                            content_data = json.loads(section.processed_content)
                            ai_output = content_data.get('content', 'No content')
                            print(f"         🤖 AI OUTPUT:")
                            print(f"            '{ai_output}'")
                        except json.JSONDecodeError:
                            print(f"         🤖 AI OUTPUT (raw):")
                            print(f"            {section.processed_content}")
                    else:
                        print(f"         🤖 AI OUTPUT: No content")
                    
                    print(f"         {'─' * 40}")
            else:
                print("   📝 No sections found")
            
            print(f"\n{'=' * 50}")

if __name__ == "__main__":
    view_resume_data() 
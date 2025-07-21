#!/usr/bin/env python3
"""
Direct database viewing script
"""

import json
from app.database import get_db
from app.models.database_models import Resume, ResumeSection, User, Template

def view_database_direct():
    """View database directly with detailed information"""
    
    for session in get_db():
        print("🗄️  DIRECT DATABASE VIEW")
        print("=" * 80)
        
        # View Users
        print("\n👥 USERS:")
        users = session.query(User).all()
        for user in users:
            print(f"   User ID: {user.id}")
            print(f"   Email: {user.email}")
            print(f"   Created: {user.created_at}")
            print(f"   {'─' * 40}")
        
        # View Templates
        print("\n📋 TEMPLATES:")
        templates = session.query(Template).all()
        for template in templates:
            print(f"   Template ID: {template.id}")
            print(f"   Template Name: {template.name}")
            print(f"   Template ID (string): {template.template_id}")
            print(f"   Category: {template.category}")
            print(f"   Active: {template.is_active}")
            print(f"   {'─' * 40}")
        
        # View Resumes with JSON data
        print("\n📄 RESUMES WITH JSON DATA:")
        resumes = session.query(Resume).all()
        for resume in resumes:
            print(f"\n   📄 Resume ID: {resume.id}")
            print(f"      Title: {resume.title}")
            print(f"      Template: {resume.template_id}")
            print(f"      User ID: {resume.user_id}")
            print(f"      Complete: {resume.is_complete}")
            print(f"      Paid: {resume.is_paid}")
            print(f"      Created: {resume.created_at}")
            print(f"      Updated: {resume.updated_at}")
            
            # Show JSON Resume data
            if resume.json_resume_data:
                print(f"      📊 JSON Resume Data:")
                print(f"         {json.dumps(resume.json_resume_data, indent=8)}")
            
            # Show completeness summary
            if resume.completeness_summary:
                print(f"      📈 Completeness Summary:")
                print(f"         {json.dumps(resume.completeness_summary, indent=8)}")
            
            print(f"      {'─' * 60}")
        
        # View Resume Sections
        print("\n📝 RESUME SECTIONS:")
        sections = session.query(ResumeSection).all()
        for section in sections:
            print(f"\n   🔹 Section ID: {section.id}")
            print(f"      Resume ID: {section.resume_id}")
            print(f"      Section Name: {section.section_name}")
            print(f"      Status: {section.status}")
            print(f"      Created: {section.created_at}")
            print(f"      Updated: {section.updated_at}")
            
            # Original input
            print(f"      📥 Original Input: '{section.original_input}'")
            
            # Processed content
            if section.processed_content:
                if isinstance(section.processed_content, dict):
                    print(f"      🤖 AI Output: {section.processed_content.get('content', 'No content')}")
                    if 'structured_data' in section.processed_content:
                        print(f"      📊 Structured Data: {json.dumps(section.processed_content['structured_data'], indent=8)}")
                else:
                    print(f"      🤖 AI Output: {section.processed_content}")
            else:
                print(f"      🤖 AI Output: No content")
            
            print(f"      {'─' * 40}")

if __name__ == "__main__":
    view_database_direct() 
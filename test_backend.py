#!/usr/bin/env python3
"""
Test script for Chat-to-CV Backend
Demonstrates the core functionality without requiring OpenAI API key
"""

import asyncio
import json
from app.services.ai_agent import ResumeWriterAgent
from app.services.template_service import TemplateService

async def test_ai_agent():
    """Test the AI agent with fallback functionality"""
    print("🧪 Testing Resume Writer AI Agent...")
    
    # Test without OpenAI API key (should use fallback)
    try:
        agent = ResumeWriterAgent()
        
        # Test the fallback rephrasing
        result = await agent.generate_section(
            template_id="professional",
            section_name="work_experience",
            raw_input="I managed a team of 5 developers and did code reviews",
            user_id="test_user_123"
        )
        
        print(f"✅ AI Agent Test Result:")
        print(f"   Status: {result.status}")
        print(f"   Section: {result.updated_section}")
        print(f"   Rephrased Content: {result.rephrased_content}")
        print(f"   Completeness Summary: {result.resume_completeness_summary.model_dump()}")
        
    except Exception as e:
        print(f"❌ AI Agent Test Failed: {e}")

def test_template_service():
    """Test the template service"""
    print("\n🎨 Testing Template Service...")
    
    try:
        service = TemplateService()
        templates = service.get_available_templates()
        
        print(f"✅ Found {len(templates)} templates:")
        for template in templates:
            print(f"   - {template.name} ({template.id}): {template.description}")
        
        # Test getting a specific template
        professional = service.get_template_by_id("professional")
        print(f"\n✅ Professional template details:")
        print(f"   ID: {professional.id}")
        print(f"   Name: {professional.name}")
        print(f"   Description: {professional.description}")
        
        # Test style guidelines
        guidelines = service.get_template_style_guidelines("modern")
        print(f"\n✅ Modern template guidelines:")
        print(f"   Tone: {guidelines['tone']}")
        print(f"   Font: {guidelines['font_family']}")
        print(f"   Emphasis: {guidelines['emphasis']}")
        
    except Exception as e:
        print(f"❌ Template Service Test Failed: {e}")

def test_resume_models():
    """Test the resume data models"""
    print("\n📄 Testing Resume Models...")
    
    try:
        from app.models.resume import (
            ResumeData, 
            ResumeSection, 
            ResumeCompletenessSummary,
            SectionStatus
        )
        
        # Create a sample resume
        resume = ResumeData(
            user_id="test_user_123",
            template_id="professional",
            sections={
                "work_experience": ResumeSection(
                    name="work_experience",
                    content=["• Led a team of 5 developers", "• Accomplished code reviews"],
                    status=SectionStatus.PARTIAL
                )
            }
        )
        
        print(f"✅ Resume Model Test:")
        print(f"   User ID: {resume.user_id}")
        print(f"   Template: {resume.template_id}")
        print(f"   Sections: {list(resume.sections.keys())}")
        print(f"   Work Experience Content: {resume.sections['work_experience'].content}")
        
    except Exception as e:
        print(f"❌ Resume Models Test Failed: {e}")

async def main():
    """Run all tests"""
    print("🚀 Starting Chat-to-CV Backend Tests\n")
    
    # Test models first
    test_resume_models()
    
    # Test template service
    test_template_service()
    
    # Test AI agent
    await test_ai_agent()
    
    print("\n🎉 All tests completed!")

if __name__ == "__main__":
    asyncio.run(main()) 
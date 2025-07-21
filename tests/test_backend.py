#!/usr/bin/env python3
"""
Test script for Chat-to-CV Backend
Demonstrates the core functionality without requiring OpenAI API key
"""

import asyncio
import json
from app.services.ai_agent import ResumeWriterAgent
from app.services.template_service import TemplateService
from app.services.resume_renderer import ResumeRenderer
from app.models.resume import JSONResume

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
        professional = service.get_template_by_id(1)
        print(f"\n✅ Professional template details:")
        print(f"   ID: {professional.id}")
        print(f"   Name: {professional.name}")
        print(f"   Description: {professional.description}")
        
        # Test style guidelines
        guidelines = service.get_template_style_guidelines(2)
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

def test_json_resume():
    """Test JSON Resume functionality"""
    print("\n📄 Testing JSON Resume...")
    
    try:
        # Load sample JSON Resume data
        with open("sample_resume_data.json", "r") as f:
            resume_data = json.load(f)
        
        # Create JSONResume object
        json_resume = JSONResume(**resume_data)
        
        print(f"✅ JSON Resume Test:")
        print(f"   Name: {json_resume.basics.name}")
        print(f"   Label: {json_resume.basics.label}")
        print(f"   Work Experience: {len(json_resume.work or [])} positions")
        print(f"   Education: {len(json_resume.education or [])} institutions")
        print(f"   Skills: {len(json_resume.skills or [])} skill categories")
        
        # Test resume renderer
        renderer = ResumeRenderer()
        html_content = renderer.render_html(json_resume, "professional")
        
        if html_content:
            print(f"   ✅ HTML rendering successful (length: {len(html_content)} chars)")
        else:
            print(f"   ❌ HTML rendering failed")
        
        # Test available themes
        themes = renderer.get_available_themes()
        print(f"   Available themes: {list(themes.keys())}")
        
    except Exception as e:
        print(f"❌ JSON Resume Test Failed: {e}")

async def main():
    """Run all tests"""
    print("🚀 Starting Chat-to-CV Backend Tests\n")
    
    # Test models first
    test_resume_models()
    
    # Test template service
    test_template_service()
    
    # Test AI agent
    await test_ai_agent()
    
    # Test JSON Resume
    test_json_resume()
    
    print("\n🎉 All tests completed!")

if __name__ == "__main__":
    asyncio.run(main()) 
#!/usr/bin/env python3
"""
Test script for AI Agent integration with LlamaIndex RAG service
"""

import os
import sys
import asyncio
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Add the app directory to the path
sys.path.append(str(Path(__file__).parent / "app"))

from app.services.ai_agent import ResumeWriterAgent

async def test_ai_agent_integration():
    """Test the AI agent with LlamaIndex RAG integration"""
    print("🧪 Testing AI Agent with LlamaIndex RAG Integration")
    print("=" * 60)
    
    # Check if OpenAI API key is set
    if not os.getenv("OPENAI_API_KEY"):
        print("❌ OPENAI_API_KEY not set. Please set it in your environment.")
        return False
    
    try:
        # Initialize the AI agent
        print("📦 Initializing ResumeWriterAgent...")
        agent = ResumeWriterAgent()
        
        # Test RAG health
        print("\n🏥 RAG Health Check:")
        rag_health = agent.get_rag_health()
        for key, value in rag_health.items():
            print(f"  {key}: {value}")
        
        if rag_health["status"] != "healthy":
            print("❌ RAG service is not healthy")
            return False
        
        # Test resume section generation
        print("\n🎯 Testing Resume Section Generation:")
        
        test_cases = [
            {
                "template_id": "professional",
                "section_name": "work",
                "raw_input": "I managed social media accounts and helped with customer service",
                "user_id": "test_user_1"
            },
            {
                "template_id": "modern",
                "section_name": "skills",
                "raw_input": "python, javascript, project management, communication",
                "user_id": "test_user_1"
            }
        ]
        
        for i, test_case in enumerate(test_cases, 1):
            print(f"\nTest Case {i}: {test_case['section_name']} for {test_case['template_id']} template")
            print(f"Input: '{test_case['raw_input']}'")
            
            try:
                result = await agent.generate_section(
                    template_id=test_case["template_id"],
                    section_name=test_case["section_name"],
                    raw_input=test_case["raw_input"],
                    user_id=test_case["user_id"]
                )
                
                if result.status == "success":
                    print(f"✅ Success! Rephrased content: '{result.rephrased_content[:100]}...'")
                    print(f"   Updated section: {result.updated_section}")
                    print(f"   Completeness: {result.resume_completeness_summary.total_sections_completed}/{result.resume_completeness_summary.total_sections} sections")
                else:
                    print(f"❌ Failed: {result.status}")
                    
            except Exception as e:
                print(f"❌ Error: {e}")
                continue
        
        print("\n✅ AI Agent integration test completed!")
        return True
        
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = asyncio.run(test_ai_agent_integration())
    sys.exit(0 if success else 1) 
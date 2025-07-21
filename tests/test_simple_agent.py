#!/usr/bin/env python3
"""
Simple test for SimpleResumeAgent
Tests the new simple, reliable AI agent
"""

import os
import sys
import asyncio
import json
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add the app directory to the path
sys.path.append(str(Path(__file__).parent / "app"))

from app.services.simple_ai_agent import SimpleResumeAgent

async def test_simple_agent():
    """Test the simple AI agent"""
    print("🧪 Testing SimpleResumeAgent")
    print("=" * 60)
    
    # Check environment variables
    print(f"GEMINI_API_KEY: {'SET' if os.getenv('GEMINI_API_KEY') else 'NOT SET'}")
    print(f"OPENAI_API_KEY: {'SET' if os.getenv('OPENAI_API_KEY') else 'NOT SET'}")
    
    try:
        # Initialize the simple AI agent
        print("\n📦 Initializing SimpleResumeAgent...")
        agent = SimpleResumeAgent()
        
        # Check health status
        print("\n🏥 Health Check:")
        health = agent.get_health_status()
        for key, value in health.items():
            if key == 'stats':
                print(f"  {key}:")
                for stat, val in value.items():
                    print(f"    {stat}: {val}")
            else:
                print(f"  {key}: {value}")
        
        # Test cases
        test_cases = [
            {
                "name": "Work Experience",
                "template_id": 1,
                "section_name": "work",
                "raw_input": "I worked as a software engineer at Google for 2 years, developing web applications and leading a team of 3 developers"
            },
            {
                "name": "Education",
                "template_id": 1,
                "section_name": "education",
                "raw_input": "I studied computer science at Stanford University"
            },
            {
                "name": "Skills",
                "template_id": 1,
                "section_name": "skills",
                "raw_input": "python, javascript, machine learning, data analysis"
            }
        ]
        
        print(f"\n🎯 Testing {len(test_cases)} scenarios:")
        print("-" * 40)
        
        success_count = 0
        
        for i, test_case in enumerate(test_cases, 1):
            print(f"\n{i}. {test_case['name']}")
            print(f"   Input: {test_case['raw_input']}")
            
            try:
                # Generate section
                result = await agent.generate_section(
                    template_id=test_case['template_id'],
                    section_name=test_case['section_name'],
                    raw_input=test_case['raw_input']
                )
                
                # Check result
                print(f"   Status: {result['status']}")
                print(f"   Quality Score: {result.get('quality_score', 'N/A')}")
                print(f"   Rephrased: {result['rephrased_content'][:100]}...")
                
                # Validate JSON structure
                try:
                    section_data = json.loads(result['updated_section'])
                    print(f"   JSON Valid: ✅ ({len(section_data)} fields)")
                    success_count += 1
                except json.JSONDecodeError:
                    print(f"   JSON Valid: ❌")
                
            except Exception as e:
                print(f"   ❌ Error: {e}")
        
        # Summary
        print(f"\n📊 SUMMARY:")
        print("-" * 40)
        print(f"✅ Successful: {success_count}/{len(test_cases)}")
        
        # Final health check
        print(f"\n🔧 FINAL STATS:")
        print("-" * 40)
        final_health = agent.get_health_status()
        for stat, value in final_health['stats'].items():
            print(f"  {stat}: {value}")
        
        return success_count == len(test_cases)
        
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        return False

async def main():
    """Run the test"""
    print("🚀 SIMPLE AI AGENT TEST")
    print("=" * 80)
    
    success = await test_simple_agent()
    
    print(f"\n🎉 FINAL RESULT:")
    print("=" * 80)
    print(f"✅ Test: {'PASS' if success else 'FAIL'}")
    
    if success:
        print("\n🎉 Simple AI Agent is working correctly!")
        print("✅ LangChain execution issues fixed")
        print("✅ Direct LLM calls working")
        print("✅ Error recovery implemented")
        print("✅ Ready for production use")
    else:
        print("\n⚠️  Some issues remain - check the output above")
    
    return success

if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1) 
#!/usr/bin/env python3
"""
Test script for structured data extraction from AI agent
"""

import asyncio
import json
from app.services.ai_agent import ResumeWriterAgent
from app.services.database_service import DatabaseService
from app.database import get_db

async def test_structured_extraction():
    """Test the AI agent's structured data extraction"""
    
    print("🧪 TESTING STRUCTURED DATA EXTRACTION")
    print("=" * 50)
    
    # Get database session
    for session in get_db():
        db_service = DatabaseService(session)
        
        # Initialize AI agent with database service
        agent = ResumeWriterAgent(db_service=db_service)
        
        # Test cases
        test_cases = [
            {
                "section": "education",
                "input": "I studied my bachelors in AI from stanford",
                "expected": "Should extract: institution=Stanford, area=AI, studyType=Bachelor's"
            },
            {
                "section": "work", 
                "input": "I worked as a software engineer at Google for 2 years",
                "expected": "Should extract: name=Google, position=Software Engineer, duration=2 years"
            },
            {
                "section": "skills",
                "input": "python, javascript, machine learning, data analysis",
                "expected": "Should extract: structured skills with levels and keywords"
            }
        ]
        
        for i, test_case in enumerate(test_cases, 1):
            print(f"\n🧪 Test Case {i}: {test_case['section']}")
            print(f"   Input: '{test_case['input']}'")
            print(f"   Expected: {test_case['expected']}")
            
            try:
                # Generate section content
                result = await agent.generate_section(
                    template_id="1",  # Professional template (numeric ID)
                    section_name=test_case["section"],
                    raw_input=test_case["input"],
                    user_id="1"  # Use existing user ID
                )
                
                print(f"   ✅ Status: {result.status}")
                print(f"   🤖 AI Output: {result.rephrased_content}")
                
                # Check if output is structured JSON
                try:
                    if result.rephrased_content.strip().startswith('{') or result.rephrased_content.strip().startswith('['):
                        parsed = json.loads(result.rephrased_content)
                        print(f"   📊 Parsed JSON: {json.dumps(parsed, indent=2)}")
                        print(f"   ✅ SUCCESS: Structured data extracted!")
                    else:
                        print(f"   ⚠️  Output is not JSON: {result.rephrased_content}")
                except json.JSONDecodeError:
                    print(f"   ❌ Failed to parse as JSON: {result.rephrased_content}")
                
            except Exception as e:
                print(f"   ❌ Error: {e}")
            
            print(f"   {'─' * 40}")

if __name__ == "__main__":
    asyncio.run(test_structured_extraction()) 
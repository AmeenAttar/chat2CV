#!/usr/bin/env python3
"""
Test LLM Agent Template Structure Output
Verifies that the agent generates properly structured JSON for different templates
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

async def test_template_structure():
    """Test LLM agent structure output for different templates"""
    print("🧪 Testing LLM Agent Template Structure Output")
    print("=" * 80)
    
    try:
        # Initialize the simple AI agent
        print("📦 Initializing SimpleResumeAgent...")
        agent = SimpleResumeAgent()
        
        # Test cases for different templates and sections
        test_cases = [
            {
                "name": "Professional Template - Work Experience",
                "template_id": 1,
                "section_name": "work",
                "raw_input": "I worked as a Senior Software Engineer at Microsoft for 3 years, leading a team of 8 developers and delivering 5 major projects that increased revenue by 25%",
                "expected_structure": ["name", "position", "startDate", "endDate", "summary", "highlights"]
            },
            {
                "name": "Modern Template - Education",
                "template_id": 2,
                "section_name": "education",
                "raw_input": "I earned a Master's degree in Computer Science from MIT with a 3.9 GPA, specializing in artificial intelligence and machine learning",
                "expected_structure": ["institution", "studyType", "area", "startDate", "endDate", "score"]
            },
            {
                "name": "Creative Template - Skills",
                "template_id": 3,
                "section_name": "skills",
                "raw_input": "Expert in Python, JavaScript, React, Node.js, and AWS. Also skilled in UI/UX design and project management",
                "expected_structure": ["name", "level", "keywords"]
            },
            {
                "name": "Minimalist Template - Projects",
                "template_id": 4,
                "section_name": "projects",
                "raw_input": "Built a full-stack e-commerce platform using React and Node.js. Processed $100K in transactions and reduced checkout time by 40%",
                "expected_structure": ["name", "description", "highlights", "keywords", "startDate", "endDate"]
            },
            {
                "name": "Executive Template - Work Experience",
                "template_id": 5,
                "section_name": "work",
                "raw_input": "As VP of Engineering at Google, I led a team of 50 engineers across 3 continents, increased team productivity by 35%, and delivered 12 major products generating $50M in revenue",
                "expected_structure": ["name", "position", "startDate", "endDate", "summary", "highlights"]
            }
        ]
        
        print(f"\n🎯 Testing {len(test_cases)} template scenarios:")
        print("-" * 60)
        
        results = []
        
        for i, test_case in enumerate(test_cases, 1):
            print(f"\n{i}. {test_case['name']}")
            print(f"   Template ID: {test_case['template_id']}")
            print(f"   Section: {test_case['section_name']}")
            print(f"   Input: {test_case['raw_input'][:80]}...")
            
            try:
                # Generate section
                result = await agent.generate_section(
                    template_id=test_case['template_id'],
                    section_name=test_case['section_name'],
                    raw_input=test_case['raw_input']
                )
                
                # Parse the JSON response
                section_data = json.loads(result['updated_section'])
                
                # Check structure
                expected_fields = test_case['expected_structure']
                actual_fields = list(section_data.keys())
                
                # Find missing and extra fields
                missing_fields = [field for field in expected_fields if field not in actual_fields]
                extra_fields = [field for field in actual_fields if field not in expected_fields]
                
                # Calculate structure score
                structure_score = len([f for f in expected_fields if f in actual_fields]) / len(expected_fields)
                
                # Check data quality
                quality_checks = []
                
                # Check for required content
                if 'name' in section_data and section_data['name'] and section_data['name'] != "Company Name":
                    quality_checks.append("✅ Company/Institution name extracted")
                else:
                    quality_checks.append("❌ Company/Institution name missing/generic")
                
                if 'position' in section_data and section_data['position'] and section_data['position'] != "Job Title":
                    quality_checks.append("✅ Position/Title extracted")
                else:
                    quality_checks.append("❌ Position/Title missing/generic")
                
                # Check for realistic dates
                if 'startDate' in section_data and section_data['startDate'] and 'MM' not in section_data['startDate']:
                    quality_checks.append("✅ Realistic start date")
                else:
                    quality_checks.append("❌ Generic or placeholder start date")
                
                # Check for highlights/achievements
                if 'highlights' in section_data and section_data['highlights'] and len(section_data['highlights']) > 0:
                    quality_checks.append("✅ Achievements/highlights included")
                else:
                    quality_checks.append("❌ No achievements/highlights")
                
                # Display results
                print(f"   Status: {result['status']}")
                print(f"   Quality Score: {result.get('quality_score', 'N/A')}")
                print(f"   Structure Score: {structure_score:.2f}")
                
                if missing_fields:
                    print(f"   Missing Fields: {missing_fields}")
                if extra_fields:
                    print(f"   Extra Fields: {extra_fields}")
                
                print(f"   Quality Checks:")
                for check in quality_checks:
                    print(f"     {check}")
                
                print(f"   Generated JSON:")
                print(f"     {json.dumps(section_data, indent=6)}")
                
                # Store results
                results.append({
                    'test_case': test_case['name'],
                    'status': result['status'],
                    'structure_score': structure_score,
                    'quality_score': result.get('quality_score', 0),
                    'missing_fields': missing_fields,
                    'extra_fields': extra_fields,
                    'quality_checks': quality_checks
                })
                
            except Exception as e:
                print(f"   ❌ Error: {e}")
                results.append({
                    'test_case': test_case['name'],
                    'status': 'error',
                    'structure_score': 0,
                    'quality_score': 0,
                    'error': str(e)
                })
        
        # Summary
        print(f"\n📊 TEMPLATE STRUCTURE ANALYSIS:")
        print("=" * 80)
        
        successful_tests = [r for r in results if r['status'] != 'error']
        avg_structure_score = sum(r['structure_score'] for r in successful_tests) / len(successful_tests) if successful_tests else 0
        avg_quality_score = sum(r['quality_score'] for r in successful_tests) / len(successful_tests) if successful_tests else 0
        
        print(f"✅ Successful Tests: {len(successful_tests)}/{len(test_cases)}")
        print(f"📊 Average Structure Score: {avg_structure_score:.2f}")
        print(f"📊 Average Quality Score: {avg_quality_score:.2f}")
        
        # Template-specific analysis
        print(f"\n🎨 TEMPLATE-SPECIFIC ANALYSIS:")
        print("-" * 60)
        
        template_results = {}
        for result in successful_tests:
            template_id = next(tc['template_id'] for tc in test_cases if tc['name'] == result['test_case'])
            if template_id not in template_results:
                template_results[template_id] = []
            template_results[template_id].append(result)
        
        for template_id, template_tests in template_results.items():
            avg_structure = sum(t['structure_score'] for t in template_tests) / len(template_tests)
            avg_quality = sum(t['quality_score'] for t in template_tests) / len(template_tests)
            print(f"Template {template_id}: Structure {avg_structure:.2f}, Quality {avg_quality:.2f}")
        
        # Building readiness assessment
        print(f"\n🏗️  BUILDING READINESS ASSESSMENT:")
        print("-" * 60)
        
        if avg_structure_score >= 0.8:
            print("✅ EXCELLENT: Structure is consistent and predictable")
            print("   - Easy to build UI components")
            print("   - Reliable data parsing")
            print("   - Minimal edge case handling needed")
        elif avg_structure_score >= 0.6:
            print("✅ GOOD: Structure is mostly consistent")
            print("   - Some edge case handling needed")
            print("   - Minor UI adjustments may be required")
        else:
            print("⚠️  NEEDS IMPROVEMENT: Structure is inconsistent")
            print("   - Significant edge case handling needed")
            print("   - UI components may need fallbacks")
        
        if avg_quality_score >= 0.7:
            print("✅ EXCELLENT: Content quality is high")
            print("   - Realistic, professional content")
            print("   - Good for production use")
        elif avg_quality_score >= 0.5:
            print("✅ ACCEPTABLE: Content quality is adequate")
            print("   - Some manual review may be needed")
            print("   - Suitable for MVP")
        else:
            print("⚠️  NEEDS IMPROVEMENT: Content quality is low")
            print("   - Significant manual review needed")
            print("   - May need prompt improvements")
        
        return avg_structure_score >= 0.7 and avg_quality_score >= 0.6
        
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        return False

async def main():
    """Run the template structure test"""
    print("🚀 LLM AGENT TEMPLATE STRUCTURE TEST")
    print("=" * 80)
    
    success = await test_template_structure()
    
    print(f"\n🎉 FINAL ASSESSMENT:")
    print("=" * 80)
    print(f"✅ Ready for Building: {'YES' if success else 'NO'}")
    
    if success:
        print("\n🎉 The LLM agent generates properly structured output!")
        print("✅ Consistent JSON structure across templates")
        print("✅ High-quality content generation")
        print("✅ Easy to build UI components")
        print("✅ Ready for iOS integration")
    else:
        print("\n⚠️  Some improvements needed before building")
        print("   - Check structure consistency")
        print("   - Review content quality")
        print("   - Consider prompt improvements")
    
    return success

if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1) 
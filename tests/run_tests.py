#!/usr/bin/env python3
"""
Test runner for the AI Resume Builder
Runs all tests and provides a summary report
"""

import subprocess
import sys
import os
from pathlib import Path

def run_tests():
    """Run all tests and return results"""
    
    print("🧪 RUNNING AI RESUME BUILDER TEST SUITE")
    print("=" * 60)
    
    # Ensure we're in the right directory
    project_root = Path(__file__).parent
    os.chdir(project_root)
    
    # Activate virtual environment if it exists
    venv_python = project_root / "venv" / "bin" / "python"
    if venv_python.exists():
        python_cmd = str(venv_python)
    else:
        python_cmd = "python"
    
    # Run pytest with coverage
    cmd = [
        python_cmd, "-m", "pytest",
        "test_ai_agent.py",
        "-v",
        "--tb=short",
        "--color=yes"
    ]
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        print("📊 TEST RESULTS:")
        print("-" * 40)
        
        if result.returncode == 0:
            print("✅ ALL TESTS PASSED!")
        else:
            print("❌ SOME TESTS FAILED!")
        
        print("\n📝 TEST OUTPUT:")
        print(result.stdout)
        
        if result.stderr:
            print("\n⚠️  ERRORS/WARNINGS:")
            print(result.stderr)
        
        return result.returncode == 0
        
    except Exception as e:
        print(f"❌ ERROR RUNNING TESTS: {e}")
        return False

def run_specific_test(test_name):
    """Run a specific test"""
    
    print(f"🧪 RUNNING SPECIFIC TEST: {test_name}")
    print("=" * 60)
    
    project_root = Path(__file__).parent
    os.chdir(project_root)
    
    venv_python = project_root / "venv" / "bin" / "python"
    if venv_python.exists():
        python_cmd = str(venv_python)
    else:
        python_cmd = "python"
    
    cmd = [
        python_cmd, "-m", "pytest",
        f"test_ai_agent.py::{test_name}",
        "-v",
        "--tb=long",
        "--color=yes"
    ]
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        print("📊 TEST RESULT:")
        print("-" * 40)
        
        if result.returncode == 0:
            print("✅ TEST PASSED!")
        else:
            print("❌ TEST FAILED!")
        
        print("\n📝 TEST OUTPUT:")
        print(result.stdout)
        
        if result.stderr:
            print("\n⚠️  ERRORS/WARNINGS:")
            print(result.stderr)
        
        return result.returncode == 0
        
    except Exception as e:
        print(f"❌ ERROR RUNNING TEST: {e}")
        return False

def show_test_summary():
    """Show a summary of available tests"""
    
    print("📋 AVAILABLE TESTS:")
    print("=" * 60)
    
    test_categories = {
        "AI Agent Tests": [
            "TestAIAgent::test_agent_initialization",
            "TestAIAgent::test_agent_tools_available",
            "TestAIAgent::test_education_extraction",
            "TestAIAgent::test_work_extraction",
            "TestAIAgent::test_skills_extraction",
            "TestAIAgent::test_fallback_extraction_methods"
        ],
        "RAG Service Tests": [
            "TestRAGService::test_rag_service_initialization",
            "TestRAGService::test_template_guidelines_retrieval",
            "TestRAGService::test_action_verbs_retrieval",
            "TestRAGService::test_best_practices_retrieval",
            "TestRAGService::test_industry_guidelines_retrieval",
            "TestRAGService::test_similarity_search"
        ],
        "Database Tests": [
            "TestDatabaseIntegration::test_database_connection",
            "TestDatabaseIntegration::test_resume_creation",
            "TestDatabaseIntegration::test_section_creation"
        ],
        "API Tests": [
            "TestAPIEndpoints::test_health_endpoint",
            "TestAPIEndpoints::test_templates_endpoint",
            "TestAPIEndpoints::test_generate_resume_section_endpoint"
        ],
        "Quality Tests": [
            "TestContentQuality::test_json_structure_validation",
            "TestContentQuality::test_content_length_validation",
            "TestContentQuality::test_action_verb_validation"
        ],
        "Performance Tests": [
            "TestPerformance::test_response_time",
            "TestPerformance::test_memory_usage"
        ]
    }
    
    for category, tests in test_categories.items():
        print(f"\n🔹 {category}:")
        for test in tests:
            print(f"   - {test}")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        if sys.argv[1] == "--list":
            show_test_summary()
        elif sys.argv[1] == "--test":
            if len(sys.argv) > 2:
                run_specific_test(sys.argv[2])
            else:
                print("❌ Please specify a test name: python run_tests.py --test TestName::test_method")
        else:
            print("❌ Unknown option. Use --list to see available tests or --test to run a specific test")
    else:
        success = run_tests()
        sys.exit(0 if success else 1) 
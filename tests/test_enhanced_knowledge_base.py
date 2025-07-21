#!/usr/bin/env python3
"""
Test script to validate enhanced knowledge base content loading and usage.
This tests the new comprehensive template style guides, industry guidelines, and action verbs.
"""

import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add app directory to path
sys.path.append('app')

from services.llama_index_rag import LlamaIndexRAGService

def test_enhanced_knowledge_base():
    """Test the enhanced knowledge base with comprehensive content"""
    
    print("🧪 Testing Enhanced Knowledge Base Content")
    print("=" * 50)
    
    # Initialize RAG service
    rag_service = LlamaIndexRAGService()
    
    # Check health
    health = rag_service.health_check()
    print(f"Health Check: {health}")
    
    if health['status'] != 'healthy':
        print("❌ RAG service not healthy, skipping tests")
        return
    
    print(f"✅ Documents loaded: {health['documents_loaded']}")
    
    # Test 1: Template Style Guides
    print("\n📋 Test 1: Template Style Guides")
    print("-" * 30)
    
    templates = ['professional', 'modern', 'creative', 'minimalist', 'executive']
    
    for template in templates:
        print(f"\nTesting {template.upper()} template:")
        guidelines = rag_service.get_template_guidelines(template)
        print(f"Guidelines length: {len(guidelines)} characters")
        print(f"Sample: {guidelines[:200]}...")
    
    # Test 2: Industry Guidelines
    print("\n🏭 Test 2: Industry Guidelines")
    print("-" * 30)
    
    industries = ['technology', 'finance', 'healthcare', 'marketing', 'education']
    
    for industry in industries:
        print(f"\nTesting {industry.upper()} industry:")
        guidelines = rag_service.get_industry_guidelines(industry)
        print(f"Guidelines length: {len(guidelines)} characters")
        print(f"Sample: {guidelines[:200]}...")
    
    # Test 3: Resume Section Best Practices
    print("\n📝 Test 3: Resume Section Best Practices")
    print("-" * 30)
    
    sections = ['work', 'education', 'skills', 'projects']
    
    for section in sections:
        print(f"\nTesting {section.replace('_', ' ').title()} section:")
        practices = rag_service.get_best_practices(section)
        print(f"Practices length: {len(practices)} characters")
        print(f"Sample: {practices[:200]}...")
    
    # Test 4: Action Verbs by Industry
    print("\n⚡ Test 4: Action Verbs by Industry")
    print("-" * 30)
    
    for industry in industries:
        print(f"\nTesting {industry.upper()} action verbs:")
        verbs = rag_service.get_action_verbs(industry)
        print(f"Verbs length: {len(verbs)} characters")
        print(f"Sample: {verbs[:200]}...")
    
    # Test 5: Semantic Search Queries
    print("\n🔍 Test 5: Semantic Search Queries")
    print("-" * 30)
    
    test_queries = [
        "professional template formatting rules",
        "technology industry keywords and jargon",
        "work experience bullet point examples",
        "leadership action verbs for executives",
        "ATS optimization tips for resumes"
    ]
    
    for query in test_queries:
        print(f"\nQuery: '{query}'")
        results = rag_service.query(query, n_results=2)
        print(f"Results: {len(results)} found")
        for i, result in enumerate(results):
            print(f"  {i+1}. Source: {result['metadata']['source']}")
            print(f"     Content: {result['content'][:150]}...")
    
    # Test 6: Specific Template Queries
    print("\n🎨 Test 6: Specific Template Style Queries")
    print("-" * 30)
    
    template_queries = [
        "creative template design philosophy",
        "executive template leadership focus",
        "minimalist template clean formatting",
        "modern template contemporary style"
    ]
    
    for query in template_queries:
        print(f"\nQuery: '{query}'")
        results = rag_service.query(query, n_results=1)
        if results:
            print(f"Found: {results[0]['content'][:200]}...")
        else:
            print("No results found")
    
    print("\n✅ Enhanced Knowledge Base Testing Complete!")

async def test_ai_agent_integration():
    """Test AI agent integration with enhanced knowledge base"""
    
    print("\n🤖 Testing AI Agent Integration with Enhanced Knowledge Base")
    print("=" * 60)
    
    try:
        from services.ai_agent import ResumeWriterAgent
        
        # Initialize AI agent
        agent = ResumeWriterAgent()
        
        # Test cases with different templates and industries
        test_cases = [
            {
                "template_id": "professional",
                "section": "work",
                "content": "I managed a team and helped with customer service",
                "industry": "technology"
            },
            {
                "template_id": "creative",
                "section": "skills",
                "content": "design, creativity, problem solving",
                "industry": "marketing"
            },
            {
                "template_id": "executive",
                "section": "work",
                "content": "I led projects and made strategic decisions",
                "industry": "finance"
            }
        ]
        
        for i, test_case in enumerate(test_cases, 1):
            print(f"\n🧪 Test Case {i}: {test_case['template_id']} template, {test_case['industry']} industry")
            print("-" * 50)
            
            try:
                result = await agent.generate_section(
                    template_id=test_case['template_id'],
                    section_name=test_case['section'],
                    raw_input=test_case['content'],
                    user_id="test_user"
                )
                
                print(f"✅ Success!")
                print(f"Input: {test_case['content']}")
                print(f"Output: {result.rephrased_content if hasattr(result, 'rephrased_content') else result}")
                
            except Exception as e:
                print(f"❌ Error: {e}")
        
        print("\n✅ AI Agent Integration Testing Complete!")
        
    except ImportError as e:
        print(f"❌ Could not import AI agent: {e}")
    except Exception as e:
        print(f"❌ AI agent test failed: {e}")

async def main():
    print("🚀 Starting Enhanced Knowledge Base Testing")
    print("=" * 50)
    
    # Test enhanced knowledge base
    test_enhanced_knowledge_base()
    
    # Test AI agent integration
    await test_ai_agent_integration()
    
    print("\n🎉 All Enhanced Knowledge Base Tests Complete!")

if __name__ == "__main__":
    import asyncio
    asyncio.run(main()) 
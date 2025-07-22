#!/usr/bin/env python3
"""
Full Resume Building Test
Tests the complete workflow of building a resume using all APIs
"""

import requests
import json
import time
from typing import Dict, Any

BASE_URL = "http://localhost:8000"
USER_EMAIL = "test.user@example.com"

class ResumeBuilderTest:
    def __init__(self):
        self.session = requests.Session()
        self.resume_id = None
        self.user_id = USER_EMAIL
        
    def test_health_check(self):
        """Test health endpoint"""
        print("🔍 Testing Health Check...")
        response = self.session.get(f"{BASE_URL}/health")
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            health_data = response.json()
            print(f"System Status: {health_data['status']}")
            print(f"AI Agent: {health_data['services']['ai_agent']['status']}")
            print(f"Template Service: {health_data['services']['template_service']['status']}")
        return response.status_code == 200
    
    def test_get_templates(self):
        """Test template listing"""
        print("\n📋 Testing Template Listing...")
        response = self.session.get(f"{BASE_URL}/templates")
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            templates = response.json()
            print(f"Available Templates: {len(templates)}")
            for template in templates[:3]:  # Show first 3
                print(f"  - {template['name']} (ID: {template['id']})")
        return response.status_code == 200
    
    def test_create_resume(self):
        """Test resume creation"""
        print("\n📝 Testing Resume Creation...")
        data = {
            "template_id": 1,  # Professional template
            "title": "John Doe - Software Engineer Resume",
            "user_email": self.user_id
        }
        response = self.session.post(f"{BASE_URL}/resumes", json=data)
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            resume_data = response.json()
            self.resume_id = resume_data['resume_id']
            print(f"Resume Created: ID {self.resume_id}")
            print(f"Template ID: {resume_data['template_id']}")
            print(f"User ID: {resume_data['user_id']}")
        return response.status_code == 200
    
    def test_generate_basics(self):
        """Test generating personal details section"""
        print("\n👤 Testing Personal Details Generation...")
        data = {
            "template_id": 1,
            "section_name": "basics",
            "raw_input": "My name is John Doe, I'm a software engineer with 5 years of experience. My email is john.doe@email.com and phone is 555-123-4567. I live in San Francisco, CA. I'm passionate about building scalable web applications and have expertise in Python, JavaScript, and cloud technologies.",
            "user_id": self.user_id,
            "resume_id": self.resume_id
        }
        response = self.session.post(f"{BASE_URL}/generate-resume-section", json=data)
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            print(f"Status: {result['status']}")
            print(f"json_resume keys: {list(result['json_resume'].keys())}")
            print(f"Checklist sample: {list(result['quality_checklist'].items())[:5]}")
        return response.status_code == 200
    
    def test_generate_work(self):
        """Test generating work experience section"""
        print("\n💼 Testing Work Experience Generation...")
        data = {
            "template_id": 1,
            "section_name": "work",
            "raw_input": "I worked as a Senior Software Engineer at TechCorp from January 2022 to present. I led a team of 5 developers and managed the development of a microservices architecture. I increased system performance by 40% and reduced deployment time by 60%. I also worked as a Software Engineer at StartupXYZ from March 2020 to December 2021 where I built REST APIs and implemented CI/CD pipelines.",
            "user_id": self.user_id,
            "resume_id": self.resume_id
        }
        response = self.session.post(f"{BASE_URL}/generate-resume-section", json=data)
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            print(f"Status: {result['status']}")
            print(f"Rephrased Content: {result['rephrased_content'][:100]}...")
            print(f"Completeness: {result['resume_completeness_summary']['work']}")
        return response.status_code == 200
    
    def test_generate_education(self):
        """Test education generation"""
        print("\n🎓 Testing Education Generation...")
        data = {
            "template_id": 1,
            "section_name": "education",
            "raw_input": "I have a Bachelor's degree in Computer Science from Stanford University, graduated in 2020 with a 3.8 GPA. I also completed relevant coursework in Data Structures, Algorithms, Database Systems, and Software Engineering.",
            "user_id": self.user_id,
            "resume_id": self.resume_id
        }
        response = self.session.post(f"{BASE_URL}/generate-resume-section", json=data)
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            print(f"Status: {result['status']}")
            print(f"Rephrased Content: {result['rephrased_content'][:100]}...")
            print(f"Completeness: {result['resume_completeness_summary']['education']}")
        return response.status_code == 200
    
    def test_generate_skills(self):
        """Test skills generation"""
        print("\n🛠️ Testing Skills Generation...")
        data = {
            "template_id": 1,
            "section_name": "skills",
            "raw_input": "Python, JavaScript, React, Node.js, PostgreSQL, MongoDB, AWS, Docker, Kubernetes, Git, CI/CD, REST APIs, Microservices, Agile, Scrum",
            "user_id": self.user_id,
            "resume_id": self.resume_id
        }
        response = self.session.post(f"{BASE_URL}/generate-resume-section", json=data)
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            print(f"Status: {result['status']}")
            print(f"Rephrased Content: {result['rephrased_content'][:100]}...")
            print(f"Completeness: {result['resume_completeness_summary']['skills']}")
        return response.status_code == 200
    
    def test_generate_projects(self):
        """Test projects generation"""
        print("\n🚀 Testing Projects Generation...")
        data = {
            "template_id": 1,
            "section_name": "projects",
            "raw_input": "I built an e-commerce platform using React and Node.js that processed $50K in transactions in the first month. I also developed a machine learning model for customer segmentation that improved marketing efficiency by 25%. Another project was a real-time chat application using WebSockets and Redis.",
            "user_id": self.user_id,
            "resume_id": self.resume_id
        }
        response = self.session.post(f"{BASE_URL}/generate-resume-section", json=data)
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            print(f"Status: {result['status']}")
            print(f"Rephrased Content: {result['rephrased_content'][:100]}...")
            print(f"Completeness: {result['resume_completeness_summary']['projects']}")
        return response.status_code == 200
    
    def test_get_resume_data(self):
        """Test retrieving complete resume data"""
        print("\n📄 Testing Resume Data Retrieval...")
        response = self.session.get(f"{BASE_URL}/resumes/{self.user_id}")
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            resumes = response.json()
            print(f"User Resumes: {len(resumes)}")
            if resumes:
                latest_resume = resumes[0]
                print(f"Latest Resume ID: {latest_resume['id']}")
                print(f"Title: {latest_resume['title']}")
                print(f"Template ID: {latest_resume['template_id']}")
                print(f"Completeness: {latest_resume['completeness_summary']}")
        return response.status_code == 200
    
    def test_get_specific_resume(self):
        """Test getting specific resume with sections"""
        if not self.resume_id:
            print("❌ No resume ID available")
            return False
            
        print(f"\n📋 Testing Specific Resume Retrieval (ID: {self.resume_id})...")
        response = self.session.get(f"{BASE_URL}/resumes/{self.resume_id}/data")
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            resume_data = response.json()
            print(f"Resume Title: {resume_data['title']}")
            print(f"Template ID: {resume_data['template_id']}")
            print(f"Sections: {len(resume_data['sections'])}")
            for section in resume_data['sections']:
                print(f"  - {section['section_name']}: {section['status']}")
        return response.status_code == 200
    
    def test_voiceflow_guidance(self):
        """Test Voiceflow guidance endpoint"""
        if not self.resume_id:
            print("❌ No resume ID available")
            return False
            
        print(f"\n🎤 Testing Voiceflow Guidance...")
        response = self.session.get(f"{BASE_URL}/resumes/{self.resume_id}/voiceflow-guidance")
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            guidance = response.json()
            print(f"Template ID: {guidance['template_id']}")
            print(f"Suggested Topics: {len(guidance['voiceflow_context']['suggested_topics'])}")
            print(f"Missing Info: {len(guidance['voiceflow_context']['missing_critical_info'])}")
        return response.status_code == 200
    
    def test_resume_html_generation(self):
        """Test HTML resume generation"""
        print("\n🌐 Testing HTML Resume Generation...")
        response = self.session.get(f"{BASE_URL}/resume/{self.user_id}/html?theme=professional")
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            html_data = response.json()
            print(f"Theme: {html_data['theme']}")
            print(f"HTML Length: {len(html_data['html'])} characters")
        return response.status_code == 200
    
    def test_metrics_endpoint(self):
        """Test metrics endpoint"""
        print("\n📊 Testing Metrics Endpoint...")
        response = self.session.get(f"{BASE_URL}/metrics")
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            metrics = response.json()
            print(f"Total Errors: {metrics['error_summary']['total_errors']}")
            print(f"Active Users: {metrics['rate_limits']['active_users']}")
            print(f"Total Requests: {metrics['rate_limits']['total_requests']}")
        return response.status_code == 200
    
    def run_full_test(self):
        """Run the complete resume building test"""
        print("🚀 Starting Full Resume Building Test")
        print("=" * 50)
        
        tests = [
            ("Health Check", self.test_health_check),
            ("Get Templates", self.test_get_templates),
            ("Create Resume", self.test_create_resume),
            ("Personal Details", self.test_generate_basics),
            ("Work Experience", self.test_generate_work),
            ("Education", self.test_generate_education),
            ("Skills", self.test_generate_skills),
            ("Projects", self.test_generate_projects),
            ("Get Resume Data", self.test_get_resume_data),
            ("Specific Resume", self.test_get_specific_resume),
            ("Voiceflow Guidance", self.test_voiceflow_guidance),
            ("HTML Generation", self.test_resume_html_generation),
            ("Metrics", self.test_metrics_endpoint),
        ]
        
        results = []
        for test_name, test_func in tests:
            try:
                success = test_func()
                results.append((test_name, success))
                if not success:
                    print(f"❌ {test_name} failed")
                else:
                    print(f"✅ {test_name} passed")
            except Exception as e:
                print(f"❌ {test_name} failed with error: {e}")
                results.append((test_name, False))
            
            time.sleep(1)  # Small delay between tests
        
        print("\n" + "=" * 50)
        print("📋 Test Results Summary")
        print("=" * 50)
        
        passed = sum(1 for _, success in results if success)
        total = len(results)
        
        for test_name, success in results:
            status = "✅ PASS" if success else "❌ FAIL"
            print(f"{status} {test_name}")
        
        print(f"\nOverall: {passed}/{total} tests passed ({passed/total*100:.1f}%)")
        
        if passed == total:
            print("🎉 All tests passed! Resume building system is working correctly.")
        else:
            print("⚠️ Some tests failed. Check the output above for details.")

if __name__ == "__main__":
    tester = ResumeBuilderTest()
    tester.run_full_test() 
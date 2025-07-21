#!/usr/bin/env python3
"""
Theme Preview Generator for JSON Resume Themes
Generates previews for themes using sample data
"""

import json
import subprocess
import tempfile
import os
from typing import Optional, Dict, Any

class ThemePreviewGenerator:
    """Generates previews for JSON Resume themes"""
    
    def __init__(self):
        self.sample_data = self._get_sample_data()
    
    def _get_sample_data(self) -> Dict[str, Any]:
        """Get sample JSON Resume data for previews"""
        return {
            "$schema": "https://raw.githubusercontent.com/jsonresume/resume-schema/v1.0.0/schema.json",
            "basics": {
                "name": "John Doe",
                "label": "Software Engineer",
                "email": "john.doe@example.com",
                "phone": "(555) 123-4567",
                "url": "https://johndoe.dev",
                "summary": "Experienced software engineer with expertise in web development, machine learning, and cloud technologies. Passionate about creating scalable solutions and mentoring junior developers.",
                "location": {
                    "address": "123 Main St",
                    "postalCode": "12345",
                    "city": "San Francisco",
                    "countryCode": "US",
                    "region": "CA"
                },
                "profiles": [
                    {
                        "network": "LinkedIn",
                        "username": "johndoe",
                        "url": "https://linkedin.com/in/johndoe"
                    },
                    {
                        "network": "GitHub",
                        "username": "johndoe",
                        "url": "https://github.com/johndoe"
                    }
                ]
            },
            "work": [
                {
                    "name": "TechCorp Inc",
                    "position": "Senior Software Engineer",
                    "url": "https://techcorp.com",
                    "startDate": "2020-01",
                    "endDate": "2023-01",
                    "summary": "Led development of microservices architecture and mentored junior developers.",
                    "highlights": [
                        "Developed 5 microservices using Node.js and Python",
                        "Improved system performance by 40%",
                        "Mentored 3 junior developers",
                        "Implemented CI/CD pipeline reducing deployment time by 60%"
                    ],
                    "location": "San Francisco, CA"
                },
                {
                    "name": "StartupXYZ",
                    "position": "Full Stack Developer",
                    "url": "https://startupxyz.com",
                    "startDate": "2018-03",
                    "endDate": "2019-12",
                    "summary": "Built and maintained web applications using React and Node.js.",
                    "highlights": [
                        "Developed customer-facing web application",
                        "Integrated third-party APIs",
                        "Optimized database queries",
                        "Implemented responsive design"
                    ],
                    "location": "Remote"
                }
            ],
            "education": [
                {
                    "institution": "University of Technology",
                    "url": "https://university.edu",
                    "area": "Computer Science",
                    "studyType": "Bachelor",
                    "startDate": "2014-09",
                    "endDate": "2018-05",
                    "score": "3.8/4.0",
                    "courses": [
                        "Data Structures and Algorithms",
                        "Database Systems",
                        "Software Engineering",
                        "Machine Learning"
                    ]
                }
            ],
            "skills": [
                {
                    "name": "JavaScript",
                    "level": "Expert",
                    "keywords": ["React", "Node.js", "TypeScript", "Express"]
                },
                {
                    "name": "Python",
                    "level": "Advanced",
                    "keywords": ["Django", "Flask", "Pandas", "NumPy"]
                },
                {
                    "name": "Cloud Platforms",
                    "level": "Intermediate",
                    "keywords": ["AWS", "Docker", "Kubernetes", "Terraform"]
                },
                {
                    "name": "Databases",
                    "level": "Advanced",
                    "keywords": ["PostgreSQL", "MongoDB", "Redis", "MySQL"]
                }
            ],
            "projects": [
                {
                    "name": "E-commerce Platform",
                    "description": "Full-stack e-commerce platform with payment integration and admin dashboard.",
                    "highlights": [
                        "Built with React, Node.js, and PostgreSQL",
                        "Integrated Stripe payment processing",
                        "Implemented real-time inventory management",
                        "Deployed on AWS with Docker"
                    ],
                    "keywords": ["React", "Node.js", "PostgreSQL", "Stripe", "AWS"],
                    "startDate": "2022-01",
                    "endDate": "2022-06",
                    "url": "https://github.com/johndoe/ecommerce",
                    "roles": ["Full Stack Developer", "Project Lead"],
                    "entity": "Personal Project",
                    "type": "Web Application"
                },
                {
                    "name": "Machine Learning API",
                    "description": "RESTful API for image classification using TensorFlow and FastAPI.",
                    "highlights": [
                        "Built with Python, FastAPI, and TensorFlow",
                        "Achieved 95% accuracy on test dataset",
                        "Implemented caching with Redis",
                        "Containerized with Docker"
                    ],
                    "keywords": ["Python", "FastAPI", "TensorFlow", "Redis", "Docker"],
                    "startDate": "2021-03",
                    "endDate": "2021-08",
                    "url": "https://github.com/johndoe/ml-api",
                    "roles": ["Backend Developer"],
                    "entity": "Open Source",
                    "type": "API"
                }
            ],
            "volunteer": [
                {
                    "organization": "Code for Good",
                    "position": "Volunteer Developer",
                    "url": "https://codeforgood.org",
                    "startDate": "2021-01",
                    "endDate": "2022-01",
                    "summary": "Developed web applications for non-profit organizations.",
                    "highlights": [
                        "Built donation tracking system",
                        "Created volunteer management platform",
                        "Mentored new volunteers"
                    ]
                }
            ],
            "awards": [
                {
                    "title": "Best Developer Award",
                    "date": "2022-12",
                    "awarder": "TechCorp Inc",
                    "summary": "Recognized for outstanding contributions to the engineering team."
                }
            ],
            "certificates": [
                {
                    "name": "AWS Certified Developer",
                    "date": "2022-06",
                    "issuer": "Amazon Web Services",
                    "url": "https://aws.amazon.com/certification/"
                },
                {
                    "name": "Google Cloud Professional Developer",
                    "date": "2021-09",
                    "issuer": "Google",
                    "url": "https://cloud.google.com/certification/"
                }
            ],
            "languages": [
                {
                    "language": "English",
                    "fluency": "Native"
                },
                {
                    "language": "Spanish",
                    "fluency": "Intermediate"
                }
            ],
            "interests": [
                {
                    "name": "Open Source",
                    "keywords": ["Contributing", "Maintaining", "Community"]
                },
                {
                    "name": "Photography",
                    "keywords": ["Landscape", "Street", "Portrait"]
                }
            ]
        }
    
    def generate_preview(self, theme_package: str) -> Optional[str]:
        """Generate preview for a theme using sample data"""
        try:
            # Create temporary file for sample data
            with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
                json.dump(self.sample_data, f, indent=2)
                json_file = f.name
            
            try:
                # Use resume-cli to generate preview
                cmd = [
                    "resume", "export",
                    "-r", json_file,
                    "-t", theme_package,
                    "-f", "html",
                    "preview.html"
                ]
                
                result = subprocess.run(
                    cmd, 
                    capture_output=True, 
                    text=True, 
                    timeout=30
                )
                
                if result.returncode == 0:
                    # Read the generated HTML file
                    try:
                        with open("preview.html", "r", encoding="utf-8") as f:
                            html_content = f.read()
                        # Clean up the output file
                        os.unlink("preview.html")
                        return html_content
                    except FileNotFoundError:
                        print("Preview file not found")
                        return None
                else:
                    print(f"Preview generation failed for {theme_package}: {result.stderr}")
                    return None
                    
            finally:
                # Clean up temporary file
                os.unlink(json_file)
                
        except Exception as e:
            print(f"Error generating preview for {theme_package}: {e}")
            return None
    
    def generate_all_previews(self) -> Dict[str, Optional[str]]:
        """Generate previews for all JSON Resume themes"""
        themes = [
            "jsonresume-theme-classy",
            "jsonresume-theme-elegant",
            "jsonresume-theme-kendall",
            "jsonresume-theme-cora",
            "jsonresume-theme-even",
            "jsonresume-theme-lowmess",
            "jsonresume-theme-waterfall",
            "jsonresume-theme-straightforward",
            "jsonresume-theme-sceptile",
            "jsonresume-theme-bufferbloat",
            "jsonresume-theme-modern",
            "jsonresume-theme-msresume",
            "jsonresume-theme-projects",
            "jsonresume-theme-umennel",
            "jsonresume-theme-even-crewshin",
            "jsonresume-theme-stackoverflow-ru"
        ]
        
        previews = {}
        for theme in themes:
            print(f"Generating preview for {theme}...")
            preview = self.generate_preview(theme)
            previews[theme] = preview
        
        return previews
    
    def save_preview(self, theme_package: str, output_path: str) -> bool:
        """Generate and save preview to file"""
        preview = self.generate_preview(theme_package)
        if preview:
            try:
                with open(output_path, 'w', encoding='utf-8') as f:
                    f.write(preview)
                return True
            except Exception as e:
                print(f"Error saving preview to {output_path}: {e}")
                return False
        return False
    
    def get_sample_data(self) -> Dict[str, Any]:
        """Get the sample data used for previews"""
        return self.sample_data.copy() 
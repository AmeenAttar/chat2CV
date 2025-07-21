#!/usr/bin/env python3
"""
Generate Resume HTML Preview
Creates a simple HTML preview of the generated resume
"""

import requests
import json

def generate_resume_preview():
    """Generate and display resume preview"""
    
    # Resume data from our test
    resume_data = {
        "basics": {
            "name": "John Doe",
            "label": "Software Engineer",
            "email": "john.doe@email.com",
            "phone": "555-123-4567",
            "summary": "Software Engineer with 5 years of experience in building scalable web applications. Expertise in Python, JavaScript, and cloud technologies. Passionate about developing innovative and efficient solutions.",
            "location": {
                "city": "San Francisco",
                "region": "CA"
            }
        },
        "work": [
            {
                "name": "TechCorp",
                "position": "Senior Software Engineer",
                "startDate": "2022-01",
                "endDate": "Present",
                "summary": "Led a team of 5 developers and managed the development of a microservices architecture",
                "highlights": [
                    "Increased system performance by 40%",
                    "Reduced deployment time by 60%",
                    "Managed microservices architecture development"
                ]
            },
            {
                "name": "StartupXYZ",
                "position": "Software Engineer",
                "startDate": "2020-03",
                "endDate": "2021-12",
                "summary": "Built REST APIs and implemented CI/CD pipelines",
                "highlights": [
                    "Developed REST APIs for web applications",
                    "Implemented CI/CD pipelines",
                    "Collaborated with cross-functional teams"
                ]
            }
        ],
        "education": [
            {
                "institution": "Stanford University",
                "studyType": "Bachelor's",
                "area": "Computer Science",
                "startDate": "2016",
                "endDate": "2020",
                "score": "3.8"
            }
        ],
        "skills": [
            {
                "name": "Python",
                "level": "Expert",
                "keywords": ["Django", "Flask", "Data Analysis"]
            },
            {
                "name": "JavaScript",
                "level": "Expert",
                "keywords": ["React", "Node.js", "ES6"]
            },
            {
                "name": "Cloud Technologies",
                "level": "Advanced",
                "keywords": ["AWS", "Docker", "Kubernetes"]
            },
            {
                "name": "Databases",
                "level": "Advanced",
                "keywords": ["PostgreSQL", "MongoDB", "Redis"]
            }
        ],
        "projects": [
            {
                "name": "E-commerce Platform",
                "description": "Built a full-stack e-commerce platform using React and Node.js",
                "highlights": [
                    "Processed $50K in transactions in first month",
                    "Implemented secure payment processing",
                    "Scalable microservices architecture"
                ],
                "keywords": ["React", "Node.js", "MongoDB", "Stripe"]
            },
            {
                "name": "ML Customer Segmentation",
                "description": "Developed machine learning model for customer segmentation",
                "highlights": [
                    "Improved marketing efficiency by 25%",
                    "Implemented predictive analytics",
                    "Automated customer insights"
                ],
                "keywords": ["Python", "Scikit-learn", "Pandas", "NumPy"]
            }
        ]
    }
    
    # Generate HTML
    html = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>{resume_data['basics']['name']} - Resume</title>
        <style>
            body {{
                font-family: 'Arial', sans-serif;
                line-height: 1.6;
                margin: 0;
                padding: 20px;
                background-color: #f5f5f5;
            }}
            .resume-container {{
                max-width: 800px;
                margin: 0 auto;
                background: white;
                padding: 40px;
                box-shadow: 0 0 20px rgba(0,0,0,0.1);
                border-radius: 8px;
            }}
            .header {{
                text-align: center;
                border-bottom: 3px solid #2c3e50;
                padding-bottom: 20px;
                margin-bottom: 30px;
            }}
            .header h1 {{
                color: #2c3e50;
                margin: 0;
                font-size: 2.5em;
            }}
            .header .title {{
                color: #7f8c8d;
                font-size: 1.2em;
                margin: 10px 0;
            }}
            .contact-info {{
                color: #34495e;
                margin: 15px 0;
            }}
            .contact-info a {{
                color: #3498db;
                text-decoration: none;
            }}
            .summary {{
                background-color: #ecf0f1;
                padding: 20px;
                border-radius: 5px;
                margin-bottom: 30px;
                font-style: italic;
            }}
            .section {{
                margin-bottom: 30px;
            }}
            .section h2 {{
                color: #2c3e50;
                border-bottom: 2px solid #3498db;
                padding-bottom: 5px;
                margin-bottom: 20px;
            }}
            .job, .education-item, .project {{
                margin-bottom: 25px;
            }}
            .job-header, .education-header, .project-header {{
                display: flex;
                justify-content: space-between;
                align-items: center;
                margin-bottom: 10px;
            }}
            .job-title, .education-degree, .project-name {{
                font-weight: bold;
                color: #2c3e50;
                font-size: 1.1em;
            }}
            .job-company, .education-school {{
                color: #3498db;
                font-weight: bold;
            }}
            .job-dates, .education-dates {{
                color: #7f8c8d;
                font-style: italic;
            }}
            .job-summary, .project-description {{
                margin: 10px 0;
                color: #34495e;
            }}
            .highlights {{
                margin-left: 20px;
            }}
            .highlights li {{
                margin: 5px 0;
                color: #34495e;
            }}
            .skills-grid {{
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
                gap: 15px;
                margin-top: 15px;
            }}
            .skill-item {{
                background-color: #ecf0f1;
                padding: 10px;
                border-radius: 5px;
                border-left: 4px solid #3498db;
            }}
            .skill-name {{
                font-weight: bold;
                color: #2c3e50;
            }}
            .skill-level {{
                color: #7f8c8d;
                font-size: 0.9em;
            }}
            .skill-keywords {{
                color: #34495e;
                font-size: 0.9em;
                margin-top: 5px;
            }}
        </style>
    </head>
    <body>
        <div class="resume-container">
            <div class="header">
                <h1>{resume_data['basics']['name']}</h1>
                <div class="title">{resume_data['basics']['label']}</div>
                <div class="contact-info">
                    <a href="mailto:{resume_data['basics']['email']}">{resume_data['basics']['email']}</a> | 
                    {resume_data['basics']['phone']} | 
                    {resume_data['basics']['location']['city']}, {resume_data['basics']['location']['region']}
                </div>
            </div>
            
            <div class="summary">
                {resume_data['basics']['summary']}
            </div>
            
            <div class="section">
                <h2>Work Experience</h2>
                {''.join([f'''
                <div class="job">
                    <div class="job-header">
                        <div>
                            <div class="job-title">{job['position']}</div>
                            <div class="job-company">{job['name']}</div>
                        </div>
                        <div class="job-dates">{job['startDate']} - {job['endDate']}</div>
                    </div>
                    <div class="job-summary">{job['summary']}</div>
                    <ul class="highlights">
                        {''.join([f'<li>{highlight}</li>' for highlight in job['highlights']])}
                    </ul>
                </div>
                ''' for job in resume_data['work']])}
            </div>
            
            <div class="section">
                <h2>Education</h2>
                {''.join([f'''
                <div class="education-item">
                    <div class="education-header">
                        <div>
                            <div class="education-degree">{edu['studyType']} in {edu['area']}</div>
                            <div class="education-school">{edu['institution']}</div>
                        </div>
                        <div class="education-dates">{edu['startDate']} - {edu['endDate']}</div>
                    </div>
                    {f'<div>GPA: {edu["score"]}</div>' if edu.get('score') else ''}
                </div>
                ''' for edu in resume_data['education']])}
            </div>
            
            <div class="section">
                <h2>Skills</h2>
                <div class="skills-grid">
                    {''.join([f'''
                    <div class="skill-item">
                        <div class="skill-name">{skill['name']}</div>
                        <div class="skill-level">{skill['level']}</div>
                        <div class="skill-keywords">{', '.join(skill['keywords'])}</div>
                    </div>
                    ''' for skill in resume_data['skills']])}
                </div>
            </div>
            
            <div class="section">
                <h2>Projects</h2>
                {''.join([f'''
                <div class="project">
                    <div class="project-header">
                        <div class="project-name">{project['name']}</div>
                    </div>
                    <div class="project-description">{project['description']}</div>
                    <ul class="highlights">
                        {''.join([f'<li>{highlight}</li>' for highlight in project['highlights']])}
                    </ul>
                    <div class="skill-keywords">Technologies: {', '.join(project['keywords'])}</div>
                </div>
                ''' for project in resume_data['projects']])}
            </div>
        </div>
    </body>
    </html>
    """
    
    # Save HTML file
    with open('resume_preview.html', 'w') as f:
        f.write(html)
    
    print("✅ Resume preview generated: resume_preview.html")
    print("📄 Open resume_preview.html in your browser to view the resume")
    
    return html

if __name__ == "__main__":
    generate_resume_preview() 
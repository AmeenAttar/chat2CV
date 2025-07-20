import json
import subprocess
import tempfile
import os
from typing import Optional
from app.models.resume import JSONResume

class ResumeRenderer:
    """
    Service for rendering JSON Resume data using various themes.
    Uses JSON Resume themes from npm to generate HTML output.
    """
    
    def __init__(self):
        self.themes = {
            "professional": "jsonresume-theme-standard",
            "modern": "jsonresume-theme-even", 
            "creative": "jsonresume-theme-kendall",
            "minimalist": "jsonresume-theme-tan-responsive",
            "executive": "jsonresume-theme-randytarampi"
        }
    
    def render_html(self, json_resume: JSONResume, theme: str = "professional") -> Optional[str]:
        """
        Render JSON Resume data as HTML using the specified theme.
        
        Args:
            json_resume: JSON Resume data
            theme: Theme name (professional, modern, creative, etc.)
            
        Returns:
            HTML string or None if rendering fails
        """
        try:
            # Get theme package name
            theme_package = self.themes.get(theme, "jsonresume-theme-standard")
            
            # Create temporary file for JSON data
            with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
                json.dump(json_resume.model_dump(), f, indent=2)
                json_file = f.name
            
            try:
                # Use resume-cli to render the resume
                # Note: This requires resume-cli to be installed globally
                cmd = [
                    "resume", "export", json_file, 
                    "--theme", theme_package,
                    "--format", "html"
                ]
                
                result = subprocess.run(
                    cmd, 
                    capture_output=True, 
                    text=True, 
                    timeout=30
                )
                
                if result.returncode == 0:
                    return result.stdout
                else:
                    print(f"Resume rendering failed: {result.stderr}")
                    return self._fallback_html(json_resume, theme)
                    
            finally:
                # Clean up temporary file
                os.unlink(json_file)
                
        except Exception as e:
            print(f"Error rendering resume: {e}")
            return self._fallback_html(json_resume, theme)
    
    def _fallback_html(self, json_resume: JSONResume, theme: str) -> str:
        """Generate a simple fallback HTML when theme rendering fails"""
        basics = json_resume.basics
        
        html = f"""
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>{basics.name if basics else 'Resume'}</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 40px; }}
                .header {{ text-align: center; margin-bottom: 30px; }}
                .section {{ margin-bottom: 25px; }}
                .section h2 {{ color: #333; border-bottom: 2px solid #333; }}
                .item {{ margin-bottom: 15px; }}
                .item h3 {{ margin: 0; color: #555; }}
                .item p {{ margin: 5px 0; }}
                .highlights {{ margin-left: 20px; }}
                .highlights li {{ margin: 5px 0; }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1>{basics.name if basics else 'Your Name'}</h1>
                <p>{basics.label if basics else 'Professional Title'}</p>
                <p>{basics.email if basics else 'email@example.com'}</p>
                <p>{basics.phone if basics else 'Phone Number'}</p>
            </div>
        """
        
        # Add work experience
        if json_resume.work:
            html += '<div class="section"><h2>Work Experience</h2>'
            for work in json_resume.work:
                html += f'''
                <div class="item">
                    <h3>{work.position} at {work.name}</h3>
                    <p>{work.startDate} - {work.endDate or 'Present'}</p>
                    <p>{work.summary or ''}</p>
                '''
                if work.highlights:
                    html += '<ul class="highlights">'
                    for highlight in work.highlights:
                        html += f'<li>{highlight}</li>'
                    html += '</ul>'
                html += '</div>'
            html += '</div>'
        
        # Add education
        if json_resume.education:
            html += '<div class="section"><h2>Education</h2>'
            for edu in json_resume.education:
                html += f'''
                <div class="item">
                    <h3>{edu.studyType} in {edu.area}</h3>
                    <p>{edu.institution}</p>
                    <p>{edu.startDate} - {edu.endDate or 'Present'}</p>
                </div>
                '''
            html += '</div>'
        
        # Add skills
        if json_resume.skills:
            html += '<div class="section"><h2>Skills</h2>'
            for skill in json_resume.skills:
                html += f'''
                <div class="item">
                    <h3>{skill.name}</h3>
                    <p>Level: {skill.level or 'Proficient'}</p>
                '''
                if skill.keywords:
                    html += f'<p>Keywords: {", ".join(skill.keywords)}</p>'
                html += '</div>'
            html += '</div>'
        
        html += """
        </body>
        </html>
        """
        
        return html
    
    def get_available_themes(self) -> dict:
        """Get list of available themes"""
        return self.themes.copy()
    
    def validate_theme(self, theme: str) -> bool:
        """Check if a theme is available"""
        return theme in self.themes 
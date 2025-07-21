#!/usr/bin/env python3
"""
JSON Resume Schema Validator
Validates resume data against the official JSON Resume schema
"""

import json
import os
from jsonschema import validate, ValidationError
from typing import Dict, Any, List, Optional

class JSONResumeValidator:
    """Validates resume data against JSON Resume schema"""
    
    def __init__(self):
        self.schema = self._load_schema()
    
    def _load_schema(self) -> Dict[str, Any]:
        """Load JSON Resume schema from file or use default"""
        schema_path = 'json_resume_schema.json'
        
        if os.path.exists(schema_path):
            with open(schema_path, 'r') as f:
                return json.load(f)
        else:
            # Fallback to basic schema structure
            return self._get_basic_schema()
    
    def _get_basic_schema(self) -> Dict[str, Any]:
        """Basic JSON Resume schema structure"""
        return {
            "$schema": "https://json-schema.org/draft-07/schema#",
            "type": "object",
            "properties": {
                "$schema": {
                    "type": "string",
                    "format": "uri"
                },
                "basics": {
                    "type": "object",
                    "properties": {
                        "name": {"type": "string"},
                        "label": {"type": "string"},
                        "image": {"type": "string"},
                        "email": {"type": "string", "format": "email"},
                        "phone": {"type": "string"},
                        "url": {"type": "string", "format": "uri"},
                        "summary": {"type": "string"},
                        "location": {
                            "type": "object",
                            "properties": {
                                "address": {"type": "string"},
                                "postalCode": {"type": "string"},
                                "city": {"type": "string"},
                                "countryCode": {"type": "string"},
                                "region": {"type": "string"}
                            }
                        },
                        "profiles": {
                            "type": "array",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "network": {"type": "string"},
                                    "username": {"type": "string"},
                                    "url": {"type": "string", "format": "uri"}
                                },
                                "required": ["network", "username"]
                            }
                        }
                    },
                    "required": ["name", "email"]
                },
                "work": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "name": {"type": "string"},
                            "position": {"type": "string"},
                            "url": {"type": "string", "format": "uri"},
                            "startDate": {"type": "string"},
                            "endDate": {"type": "string"},
                            "summary": {"type": "string"},
                            "highlights": {
                                "type": "array",
                                "items": {"type": "string"}
                            },
                            "location": {"type": "string"},
                            "description": {"type": "string"}
                        },
                        "required": ["name", "position", "startDate"]
                    }
                },
                "education": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "institution": {"type": "string"},
                            "url": {"type": "string", "format": "uri"},
                            "area": {"type": "string"},
                            "studyType": {"type": "string"},
                            "startDate": {"type": "string"},
                            "endDate": {"type": "string"},
                            "score": {"type": "string"},
                            "courses": {
                                "type": "array",
                                "items": {"type": "string"}
                            }
                        },
                        "required": ["institution", "area", "studyType"]
                    }
                },
                "skills": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "name": {"type": "string"},
                            "level": {"type": "string"},
                            "keywords": {
                                "type": "array",
                                "items": {"type": "string"}
                            }
                        },
                        "required": ["name"]
                    }
                },
                "projects": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "name": {"type": "string"},
                            "description": {"type": "string"},
                            "highlights": {
                                "type": "array",
                                "items": {"type": "string"}
                            },
                            "keywords": {
                                "type": "array",
                                "items": {"type": "string"}
                            },
                            "startDate": {"type": "string"},
                            "endDate": {"type": "string"},
                            "url": {"type": "string", "format": "uri"},
                            "roles": {
                                "type": "array",
                                "items": {"type": "string"}
                            },
                            "entity": {"type": "string"},
                            "type": {"type": "string"}
                        },
                        "required": ["name", "description"]
                    }
                },
                "volunteer": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "organization": {"type": "string"},
                            "position": {"type": "string"},
                            "url": {"type": "string", "format": "uri"},
                            "startDate": {"type": "string"},
                            "endDate": {"type": "string"},
                            "summary": {"type": "string"},
                            "highlights": {
                                "type": "array",
                                "items": {"type": "string"}
                            }
                        },
                        "required": ["organization", "position", "startDate"]
                    }
                },
                "awards": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "title": {"type": "string"},
                            "date": {"type": "string"},
                            "awarder": {"type": "string"},
                            "summary": {"type": "string"}
                        },
                        "required": ["title", "date", "awarder"]
                    }
                },
                "certificates": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "name": {"type": "string"},
                            "date": {"type": "string"},
                            "issuer": {"type": "string"},
                            "url": {"type": "string", "format": "uri"}
                        },
                        "required": ["name", "date", "issuer"]
                    }
                },
                "publications": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "name": {"type": "string"},
                            "publisher": {"type": "string"},
                            "releaseDate": {"type": "string"},
                            "url": {"type": "string", "format": "uri"},
                            "summary": {"type": "string"}
                        },
                        "required": ["name", "publisher", "releaseDate"]
                    }
                },
                "languages": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "language": {"type": "string"},
                            "fluency": {"type": "string"}
                        },
                        "required": ["language", "fluency"]
                    }
                },
                "interests": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "name": {"type": "string"},
                            "keywords": {
                                "type": "array",
                                "items": {"type": "string"}
                            }
                        },
                        "required": ["name"]
                    }
                },
                "references": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "name": {"type": "string"},
                            "reference": {"type": "string"}
                        },
                        "required": ["name", "reference"]
                    }
                },
                "meta": {
                    "type": "object",
                    "properties": {
                        "theme": {"type": "string"},
                        "format": {"type": "string"},
                        "version": {"type": "string"}
                    }
                }
            },
            "required": ["basics"]
        }
    
    def validate_resume(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate resume data against JSON Resume schema"""
        issues = []
        warnings = []
        
        try:
            validate(instance=data, schema=self.schema)
        except ValidationError as e:
            issues.append(f"Schema validation error: {e.message}")
        
        # Additional business logic validation
        validation_result = self._validate_business_logic(data)
        issues.extend(validation_result["issues"])
        warnings.extend(validation_result["warnings"])
        
        return {
            "is_valid": len(issues) == 0,
            "issues": issues,
            "warnings": warnings,
            "schema_version": "v1.0.0"
        }
    
    def _validate_business_logic(self, data: Dict[str, Any]) -> Dict[str, List[str]]:
        """Validate business logic beyond schema"""
        issues = []
        warnings = []
        
        # Check basics section
        if 'basics' not in data:
            issues.append("Missing required section: basics")
        else:
            basics = data['basics']
            if not basics.get('name'):
                issues.append("Missing required field: basics.name")
            if not basics.get('email'):
                issues.append("Missing required field: basics.email")
            elif not self._is_valid_email(basics['email']):
                issues.append("Invalid email format: basics.email")
            
            # Check summary length
            if basics.get('summary') and len(basics['summary']) > 500:
                warnings.append("basics.summary exceeds recommended length (500 characters)")
        
        # Check work experience
        if 'work' in data and isinstance(data['work'], list):
            for i, work in enumerate(data['work']):
                if not work.get('name'):
                    issues.append(f"Missing required field: work[{i}].name")
                if not work.get('position'):
                    issues.append(f"Missing required field: work[{i}].position")
                if not work.get('startDate'):
                    issues.append(f"Missing required field: work[{i}].startDate")
                
                # Check date format
                if work.get('startDate') and not self._is_valid_date(work['startDate']):
                    warnings.append(f"Invalid date format: work[{i}].startDate (use YYYY-MM format)")
                if work.get('endDate') and not self._is_valid_date(work['endDate']):
                    warnings.append(f"Invalid date format: work[{i}].endDate (use YYYY-MM format)")
        
        # Check education
        if 'education' in data and isinstance(data['education'], list):
            for i, education in enumerate(data['education']):
                if not education.get('institution'):
                    issues.append(f"Missing required field: education[{i}].institution")
                if not education.get('area'):
                    issues.append(f"Missing required field: education[{i}].area")
                if not education.get('studyType'):
                    issues.append(f"Missing required field: education[{i}].studyType")
        
        # Check skills
        if 'skills' in data and isinstance(data['skills'], list):
            for i, skill in enumerate(data['skills']):
                if not skill.get('name'):
                    issues.append(f"Missing required field: skills[{i}].name")
        
        return {"issues": issues, "warnings": warnings}
    
    def _is_valid_email(self, email: str) -> bool:
        """Basic email validation"""
        import re
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return bool(re.match(pattern, email))
    
    def _is_valid_date(self, date: str) -> bool:
        """Validate date format (YYYY-MM or YYYY-MM-DD)"""
        import re
        pattern = r'^\d{4}-\d{2}(-\d{2})?$'
        return bool(re.match(pattern, date))
    
    def get_schema_version(self) -> str:
        """Get the schema version being used"""
        return self.schema.get("$schema", "v1.0.0")
    
    def validate_section(self, section_name: str, section_data: Any) -> Dict[str, Any]:
        """Validate a specific section of the resume"""
        # Create a minimal resume with just this section
        test_resume = {
            "basics": {"name": "Test User", "email": "test@example.com"},
            section_name: section_data
        }
        
        return self.validate_resume(test_resume) 
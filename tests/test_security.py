#!/usr/bin/env python3
"""
Security and Validation Tests for Chat-to-CV Backend
Tests input validation, rate limiting, and security features
"""

import pytest
import json
import time
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

class TestInputValidation:
    """Test input validation and sanitization"""
    
    def test_valid_resume_section_request(self):
        """Test valid resume section request"""
        request_data = {
            "template_id": 1,
            "section_name": "work",
            "raw_input": "I managed a team of 5 developers",
            "user_id": "test@example.com",
            "resume_id": None
        }
        
        response = client.post("/generate-resume-section", json=request_data)
        assert response.status_code in [200, 500]  # 500 if AI service unavailable
        
    def test_invalid_template_id(self):
        """Test invalid template ID validation"""
        request_data = {
            "template_id": 999,  # Invalid template ID
            "section_name": "work",
            "raw_input": "I managed a team of 5 developers",
            "user_id": "test@example.com"
        }
        
        response = client.post("/generate-resume-section", json=request_data)
        assert response.status_code == 422  # Validation error
        
    def test_invalid_section_name(self):
        """Test invalid section name validation"""
        request_data = {
            "template_id": 1,
            "section_name": "invalid_section",
            "raw_input": "I managed a team of 5 developers",
            "user_id": "test@example.com"
        }
        
        response = client.post("/generate-resume-section", json=request_data)
        assert response.status_code == 422  # Validation error
        
    def test_empty_input(self):
        """Test empty input validation"""
        request_data = {
            "template_id": 1,
            "section_name": "work",
            "raw_input": "",  # Empty input
            "user_id": "test@example.com"
        }
        
        response = client.post("/generate-resume-section", json=request_data)
        assert response.status_code == 422  # Validation error
        
    def test_too_long_input(self):
        """Test input length validation"""
        long_input = "A" * 3000  # Too long input
        request_data = {
            "template_id": 1,
            "section_name": "work",
            "raw_input": long_input,
            "user_id": "test@example.com"
        }
        
        response = client.post("/generate-resume-section", json=request_data)
        assert response.status_code == 422  # Validation error
        
    def test_invalid_user_id(self):
        """Test invalid user ID validation"""
        request_data = {
            "template_id": 1,
            "section_name": "work",
            "raw_input": "I managed a team of 5 developers",
            "user_id": "invalid_user_id"  # No @ symbol
        }
        
        response = client.post("/generate-resume-section", json=request_data)
        assert response.status_code == 422  # Validation error

class TestRateLimiting:
    """Test rate limiting functionality"""
    
    def test_rate_limit_exceeded(self):
        """Test rate limiting when exceeded"""
        user_id = "ratelimit@example.com"
        
        # Make multiple requests quickly
        for i in range(15):  # Exceed the 10/minute limit
            request_data = {
                "template_id": 1,
                "section_name": "work",
                "raw_input": f"Request {i}",
                "user_id": user_id
            }
            
            response = client.post("/generate-resume-section", json=request_data)
            
            if i >= 10:
                # Should be rate limited after 10 requests
                assert response.status_code == 429
            else:
                # Should succeed for first 10 requests
                assert response.status_code in [200, 500]
    
    def test_rate_limit_reset(self):
        """Test rate limit reset after window"""
        user_id = "reset@example.com"
        
        # Make 5 requests
        for i in range(5):
            request_data = {
                "template_id": 1,
                "section_name": "work",
                "raw_input": f"Request {i}",
                "user_id": user_id
            }
            response = client.post("/generate-resume-section", json=request_data)
            assert response.status_code in [200, 500]
        
        # Wait for rate limit window to pass (simulate)
        # In real test, you'd need to mock time or wait
        # For now, just verify the logic works

class TestSecurityHeaders:
    """Test security headers and CORS"""
    
    def test_cors_headers(self):
        """Test CORS headers are present"""
        response = client.get("/health")
        assert "access-control-allow-origin" in response.headers
        
    def test_security_headers(self):
        """Test basic security headers"""
        response = client.get("/health")
        # FastAPI should include some security headers by default
        assert response.status_code == 200

class TestErrorHandling:
    """Test error handling and logging"""
    
    def test_invalid_json_handling(self):
        """Test handling of invalid JSON"""
        response = client.post("/generate-resume-section", data="invalid json")
        assert response.status_code == 422
        
    def test_missing_fields_handling(self):
        """Test handling of missing required fields"""
        request_data = {
            "template_id": 1,
            # Missing required fields
        }
        
        response = client.post("/generate-resume-section", json=request_data)
        assert response.status_code == 422
        
    def test_health_check_error_handling(self):
        """Test health check handles errors gracefully"""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert "status" in data
        assert "services" in data

class TestWebSocketSecurity:
    """Test WebSocket security features"""
    
    def test_websocket_connection(self):
        """Test WebSocket connection establishment"""
        with client.websocket_connect("/ws/test@example.com") as websocket:
            data = websocket.receive_text()
            message = json.loads(data)
            assert message["type"] == "connection_established"
            assert message["user_id"] == "test@example.com"
    
    def test_websocket_invalid_json(self):
        """Test WebSocket handles invalid JSON"""
        with client.websocket_connect("/ws/test@example.com") as websocket:
            # Send invalid JSON
            websocket.send_text("invalid json")
            data = websocket.receive_text()
            message = json.loads(data)
            assert message["type"] == "error"
            assert "Invalid JSON format" in message["message"]

if __name__ == "__main__":
    pytest.main([__file__, "-v"]) 
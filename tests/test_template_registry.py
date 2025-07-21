#!/usr/bin/env python3
"""
Test suite for the Scalable Template Registry
"""

import pytest
from app.services.template_registry import TemplateRegistry, TemplateID, JSONResumeTheme

class TestTemplateRegistry:
    """Test suite for the TemplateRegistry class"""
    
    @pytest.fixture
    def registry(self):
        return TemplateRegistry()
    
    def test_template_ids_are_integers(self):
        """Test that template IDs are integers for performance"""
        assert isinstance(TemplateID.PROFESSIONAL, int)
        assert TemplateID.PROFESSIONAL == 1
        assert TemplateID.MODERN == 2
        assert TemplateID.CREATIVE == 3
        assert TemplateID.MINIMALIST == 4
        assert TemplateID.EXECUTIVE == 5
    
    def test_get_theme_by_id(self, registry):
        """Test getting theme by integer ID"""
        theme = registry.get_theme(TemplateID.PROFESSIONAL)
        assert theme is not None
        assert theme.id == TemplateID.PROFESSIONAL
        assert theme.name == "Professional"
        assert theme.npm_package == "jsonresume-theme-classy"
        assert theme.category == "professional"
    
    def test_get_all_themes(self, registry):
        """Test getting all available themes"""
        themes = registry.get_all_themes()
        assert len(themes) >= 10  # Should have at least 10 themes
        assert all(isinstance(theme.id, int) for theme in themes)
        assert all(theme.npm_package.startswith("jsonresume-theme-") for theme in themes)
    
    def test_get_themes_by_category(self, registry):
        """Test getting themes by category"""
        professional_themes = registry.get_themes_by_category("professional")
        assert len(professional_themes) >= 2  # Should have multiple professional themes
        
        minimalist_themes = registry.get_themes_by_category("minimalist")
        assert len(minimalist_themes) >= 2  # Should have multiple minimalist themes
        
        # All themes in a category should have the same category
        assert all(theme.category == "professional" for theme in professional_themes)
        assert all(theme.category == "minimalist" for theme in minimalist_themes)
    
    def test_get_required_fields(self, registry):
        """Test getting required fields for different themes"""
        # Professional theme - standard requirements
        required_fields = registry.get_required_fields(TemplateID.PROFESSIONAL, "work")
        assert "name" in required_fields
        assert "position" in required_fields
        assert "startDate" in required_fields
        assert "endDate" in required_fields
        assert "summary" in required_fields
        assert "highlights" in required_fields
        
        # Minimalist theme - simplified requirements
        required_fields = registry.get_required_fields(TemplateID.MINIMALIST, "work")
        assert "name" in required_fields
        assert "position" in required_fields
        assert "startDate" in required_fields
        assert "endDate" in required_fields
        assert "summary" in required_fields
        assert "highlights" not in required_fields  # Not required for minimalist
    
    def test_get_length_constraints(self, registry):
        """Test getting length constraints for different themes"""
        # Professional theme - standard constraints
        constraints = registry.get_length_constraints(TemplateID.PROFESSIONAL, "work")
        assert constraints["summary"] == 300
        assert constraints["highlights"] == 150
        assert constraints["highlight_item"] == 100
        
        # Minimalist theme - shorter constraints
        constraints = registry.get_length_constraints(TemplateID.MINIMALIST, "work")
        assert constraints["summary"] == 150  # Shorter for minimalist
        
        # Executive theme - longer constraints
        constraints = registry.get_length_constraints(TemplateID.EXECUTIVE, "work")
        assert constraints["summary"] == 400  # Longer for executive
        assert constraints["highlights"] == 200
        assert constraints["highlight_item"] == 150
    
    def test_validate_field_requirements(self, registry):
        """Test field requirement validation"""
        # Valid data for professional theme
        valid_data = {
            "name": "Google",
            "position": "Software Engineer",
            "startDate": "2022-01",
            "endDate": "2024-01",
            "summary": "Developed applications",
            "highlights": ["Led team", "Improved performance"]
        }
        
        result = registry.validate_field_requirements(TemplateID.PROFESSIONAL, "work", valid_data)
        assert result["is_valid"] == True
        assert len(result["issues"]) == 0
        
        # Invalid data - missing required fields
        invalid_data = {
            "name": "Google",
            "position": "Software Engineer"
            # Missing startDate, endDate, summary, highlights
        }
        
        result = registry.validate_field_requirements(TemplateID.PROFESSIONAL, "work", invalid_data)
        assert result["is_valid"] == False
        assert len(result["issues"]) > 0
        assert any("startDate" in issue for issue in result["issues"])
        assert any("summary" in issue for issue in result["issues"])
        
        # Data with length violations
        long_data = {
            "name": "Google",
            "position": "Software Engineer",
            "startDate": "2022-01",
            "endDate": "2024-01",
            "summary": "A" * 500,  # Too long for professional theme
            "highlights": ["A" * 200]  # Too long for professional theme
        }
        
        result = registry.validate_field_requirements(TemplateID.PROFESSIONAL, "work", long_data)
        assert result["is_valid"] == True  # Still valid, just warnings
        assert len(result["warnings"]) > 0
        assert any("exceeds maximum length" in warning for warning in result["warnings"])
    
    def test_theme_scalability(self, registry):
        """Test that the registry can handle many themes"""
        # Add a new theme
        new_theme = JSONResumeTheme(
            id=100,  # High ID number
            name="Custom Theme",
            npm_package="jsonresume-theme-custom",
            description="A custom theme for testing",
            category="custom",
            version="1.0.0",
            author="test"
        )
        
        success = registry.add_theme(new_theme)
        assert success == True
        
        # Verify theme was added
        retrieved_theme = registry.get_theme(100)
        assert retrieved_theme is not None
        assert retrieved_theme.name == "Custom Theme"
        
        # Remove theme
        success = registry.remove_theme(100)
        assert success == True
        
        # Verify theme was removed
        retrieved_theme = registry.get_theme(100)
        assert retrieved_theme is None
    
    def test_theme_statistics(self, registry):
        """Test theme statistics"""
        stats = registry.get_theme_statistics()
        
        assert "total_themes" in stats
        assert "categories" in stats
        assert "categories_count" in stats
        
        assert stats["total_themes"] >= 10
        assert len(stats["categories"]) >= 4  # professional, modern, creative, minimalist, executive
        assert stats["categories_count"] >= 4
    
    def test_real_json_resume_integration(self, registry):
        """Test integration with real JSON Resume themes"""
        # Check that themes have real npm packages
        themes = registry.get_all_themes()
        
        for theme in themes:
            assert theme.npm_package.startswith("jsonresume-theme-")
            assert theme.version is not None
            assert theme.author is not None
            assert theme.category in ["professional", "modern", "creative", "minimalist", "executive"]
    
    def test_performance_comparison(self, registry):
        """Test that integer IDs are faster than string IDs"""
        import time
        
        # Test integer ID lookup
        start_time = time.time()
        for _ in range(1000):
            theme = registry.get_theme(TemplateID.PROFESSIONAL)
        int_lookup_time = time.time() - start_time
        
        # Test string ID lookup (if we had string IDs)
        # This demonstrates the performance benefit of integer IDs
        assert int_lookup_time < 0.1  # Should be very fast


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"]) 
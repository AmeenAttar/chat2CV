#!/usr/bin/env python3
"""
Database setup script for Chat-to-CV application.
This script initializes the database, creates tables, and populates sample data.
"""

import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add app directory to path
sys.path.append('app')

from app.database import init_db, get_db
from app.services.database_service import DatabaseService
from app.models.database_models import UserCreate

def setup_database():
    """Initialize database and create sample data"""
    
    print("🚀 Setting up Chat-to-CV Database")
    print("=" * 40)
    
    try:
        # Initialize database tables
        print("📋 Creating database tables...")
        init_db()
        print("✅ Database tables created successfully")
        
        # Get database session
        db = next(get_db())
        db_service = DatabaseService(db)
        
        # Create sample templates
        print("\n📝 Creating sample templates...")
        templates = [
            {
                "template_id": 1,
                "name": "Professional",
                "description": "Clean, traditional resume template suitable for corporate environments",
                "category": "professional",
                "preview_url": "/static/templates/professional_preview.png"
            },
            {
                "template_id": 2,
                "name": "Modern",
                "description": "Contemporary design with clean lines and modern typography",
                "category": "modern",
                "preview_url": "/static/templates/modern_preview.png"
            },
            {
                "template_id": 3,
                "name": "Creative",
                "description": "Bold, artistic template perfect for creative industries",
                "category": "creative",
                "preview_url": "/static/templates/creative_preview.png"
            },
            {
                "template_id": 4,
                "name": "Minimalist",
                "description": "Simple, clean design focusing on content over decoration",
                "category": "minimalist",
                "preview_url": "/static/templates/minimalist_preview.png"
            },
            {
                "template_id": 5,
                "name": "Executive",
                "description": "Sophisticated template designed for senior-level positions",
                "category": "executive",
                "preview_url": "/static/templates/executive_preview.png"
            }
        ]
        
        for template_data in templates:
            existing = db_service.get_template_by_id(template_data["template_id"])
            if not existing:
                db_service.create_template(**template_data)
                print(f"✅ Created template: {template_data['name']}")
            else:
                print(f"⚠️  Template already exists: {template_data['name']}")
        
        # Create sample user
        print("\n👤 Creating sample user...")
        sample_user_data = UserCreate(
            email="test@example.com",
            name="Test User"
        )
        
        existing_user = db_service.get_user_by_email(sample_user_data.email)
        if not existing_user:
            user = db_service.create_user(sample_user_data)
            print(f"✅ Created sample user: {user.email}")
            
            # Create sample resume for the user
            print("\n📄 Creating sample resume...")
            resume = db_service.create_resume(
                user_id=user.id,
                template_id="professional",
                title="Sample Professional Resume"
            )
            print(f"✅ Created sample resume: {resume.title}")
        else:
            print(f"⚠️  Sample user already exists: {existing_user.email}")
        
        print("\n🎉 Database setup completed successfully!")
        print("\n📊 Database Summary:")
        print(f"   - Templates: {len(db_service.get_all_templates())}")
        print(f"   - Users: 1 (sample user)")
        print(f"   - Resumes: 1 (sample resume)")
        
        return True
        
    except Exception as e:
        print(f"❌ Database setup failed: {e}")
        return False

def run_migrations():
    """Run database migrations using Alembic"""
    
    print("\n🔄 Running database migrations...")
    
    try:
        import subprocess
        result = subprocess.run(
            ["alembic", "upgrade", "head"],
            capture_output=True,
            text=True
        )
        
        if result.returncode == 0:
            print("✅ Database migrations completed successfully")
            return True
        else:
            print(f"❌ Migration failed: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"❌ Migration error: {e}")
        return False

def check_database_connection():
    """Check if database connection is working"""
    
    print("🔍 Checking database connection...")
    
    try:
        db = next(get_db())
        db_service = DatabaseService(db)
        
        # Try a simple query
        templates = db_service.get_all_templates()
        print(f"✅ Database connection successful (found {len(templates)} templates)")
        return True
        
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Chat-to-CV Database Setup")
    print("=" * 40)
    
    # Check database connection
    if not check_database_connection():
        print("\n❌ Cannot proceed without database connection")
        print("Please ensure PostgreSQL is running and DATABASE_URL is set correctly")
        sys.exit(1)
    
    # Run migrations
    if not run_migrations():
        print("\n❌ Migration failed, but continuing with setup...")
    
    # Setup database
    if setup_database():
        print("\n🎉 All done! Database is ready for use.")
    else:
        print("\n❌ Database setup failed!")
        sys.exit(1) 
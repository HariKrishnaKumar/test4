#!/usr/bin/env python3
"""
Setup script for Language Selection API
This script helps set up the language selection functionality
"""

import os
import subprocess
import sys

def check_environment():
    """Check if required environment variables are set"""
    print("Checking environment variables...")

    required_vars = ['GEMINI_API_KEY']
    missing_vars = []

    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)

    if missing_vars:
        print(f"❌ Missing environment variables: {', '.join(missing_vars)}")
        print("Please set these in your .env file or environment")
        return False
    else:
        print("✅ All required environment variables are set")
        return True

def run_migration():
    """Run database migration to create languages table"""
    print("\nRunning database migration...")

    try:
        result = subprocess.run(['alembic', 'upgrade', 'head'],
                              capture_output=True, text=True, check=True)
        print("✅ Database migration completed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Migration failed: {e}")
        print(f"Error output: {e.stderr}")
        return False
    except FileNotFoundError:
        print("❌ Alembic not found. Make sure you're in the project directory")
        return False

def test_imports():
    """Test if all required modules can be imported"""
    print("\nTesting imports...")

    try:
        from models.language import Language, LanguageSelectionRequest
        from services.language_service import LanguageService
        from app.routes.language_routes import router
        print("✅ All modules imported successfully")
        return True
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False

def check_database_connection():
    """Check if database connection works"""
    print("\nChecking database connection...")

    try:
        from database.database import get_db
        from sqlalchemy.orm import Session

        # Try to get a database session
        db_gen = get_db()
        db = next(db_gen)
        db.close()
        print("✅ Database connection successful")
        return True
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        return False

def main():
    """Main setup function"""
    print("Language Selection API Setup")
    print("=" * 40)

    # Check environment
    if not check_environment():
        print("\nPlease set up your environment variables and try again")
        return False

    # Test imports
    if not test_imports():
        print("\nPlease fix import errors and try again")
        return False

    # Check database connection
    if not check_database_connection():
        print("\nPlease check your database connection and try again")
        return False

    # Run migration
    if not run_migration():
        print("\nPlease fix migration issues and try again")
        return False

    print("\n" + "=" * 40)
    print("✅ Language Selection API setup completed successfully!")
    print("\nNext steps:")
    print("1. Start your FastAPI server: uvicorn main:app --reload")
    print("2. Test the API using: python test_language_api.py")
    print("3. View API documentation at: http://localhost:8000/docs")

    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

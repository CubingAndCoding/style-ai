#!/usr/bin/env python3
"""
Database Connection Test Script
Tests PostgreSQL connection and creates tables if needed
"""

import os
import sys
from dotenv import load_dotenv

# Add the backend directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_database_connection():
    """Test database connection and create tables"""
    try:
        # Load environment variables
        load_dotenv()
        
        # Import Flask app components
        from app import app, db
        from models import User, SavedPrompt
        
        print("🔍 Testing Database Connection...")
        print("=" * 50)
        
        # Check environment variables
        database_url = os.getenv('DATABASE_URL')
        sqlalchemy_uri = os.getenv('SQLALCHEMY_DATABASE_URI')
        
        print(f"DATABASE_URL: {'✅ Set' if database_url else '❌ Not set'}")
        print(f"SQLALCHEMY_DATABASE_URI: {'✅ Set' if sqlalchemy_uri else '❌ Not set'}")
        
        if database_url:
            print(f"Using PostgreSQL: {database_url[:20]}...")
        elif sqlalchemy_uri:
            print(f"Using SQLite: {sqlalchemy_uri}")
        else:
            print("❌ No database configuration found!")
            return False
        
        # Test database connection
        with app.app_context():
            print("\n🔗 Testing database connection...")
            
            # Create tables
            db.create_all()
            print("✅ Database tables created successfully")
            
            # Test a simple query
            user_count = User.query.count()
            print(f"✅ Database query successful - Users in database: {user_count}")
            
            # Test SavedPrompt table
            prompt_count = SavedPrompt.query.count()
            print(f"✅ Database query successful - Saved prompts: {prompt_count}")
            
        print("\n🎉 Database connection test PASSED!")
        return True
        
    except Exception as e:
        print(f"\n❌ Database connection test FAILED!")
        print(f"Error: {str(e)}")
        return False

def main():
    print("🗄️ Style AI Backend - Database Connection Test")
    print("=" * 60)
    
    success = test_database_connection()
    
    if success:
        print("\n✅ Your database is ready for production!")
        print("\n📋 Next steps:")
        print("1. Deploy your backend to Railway")
        print("2. Ensure DATABASE_URL is set in Railway Variables")
        print("3. Your app will automatically use PostgreSQL")
    else:
        print("\n❌ Database setup needs attention")
        print("\n🔧 Troubleshooting:")
        print("1. Check your environment variables")
        print("2. Ensure PostgreSQL service is running on Railway")
        print("3. Verify DATABASE_URL is correctly set")

if __name__ == "__main__":
    main()

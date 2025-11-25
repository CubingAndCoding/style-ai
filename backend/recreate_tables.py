#!/usr/bin/env python
"""Recreate database tables with the new schema"""
from app import app, db
from models import User, SavedPrompt, ProcessedImage

print("Recreating database tables...")
print("=" * 80)

with app.app_context():
    try:
        # Drop all tables
        print("1. Dropping existing tables...")
        db.drop_all()
        print("   ✅ Tables dropped")
        
        # Create all tables with new schema
        print("2. Creating new tables...")
        db.create_all()
        print("   ✅ Tables created")
        
        # Verify tables exist
        print("3. Verifying tables...")
        from sqlalchemy import inspect
        inspector = inspect(db.engine)
        tables = inspector.get_table_names()
        print(f"   ✅ Found {len(tables)} tables: {', '.join(tables)}")
        
        if 'users' in tables:
            print("   ✅ 'users' table exists!")
        else:
            print("   ❌ 'users' table not found!")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        exit(1)

print("\n✅ Database tables recreated successfully!")
print("   You can now restart the backend server.")



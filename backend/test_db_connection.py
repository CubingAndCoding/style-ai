#!/usr/bin/env python
"""Test database connection and bcrypt"""
from app import app, db, User, bcrypt

print("Testing database and bcrypt setup...")
print("=" * 80)

with app.app_context():
    # Test database connection
    try:
        print("1. Testing database connection...")
        db.session.execute(db.text('SELECT 1'))
        print("   ✅ Database connection works")
    except Exception as e:
        print(f"   ❌ Database connection failed: {e}")
        exit(1)
    
    # Test bcrypt
    try:
        print("2. Testing bcrypt...")
        test_password = "test123"
        hashed = bcrypt.generate_password_hash(test_password).decode('utf-8')
        print(f"   ✅ Bcrypt hash generated: {hashed[:50]}...")
        
        # Test password check
        is_valid = bcrypt.check_password_hash(hashed, test_password)
        if is_valid:
            print("   ✅ Bcrypt password check works")
        else:
            print("   ❌ Bcrypt password check failed")
            exit(1)
    except Exception as e:
        print(f"   ❌ Bcrypt failed: {e}")
        import traceback
        traceback.print_exc()
        exit(1)
    
    # Test User model
    try:
        print("3. Testing User model...")
        user_count = User.query.count()
        print(f"   ✅ User model works (found {user_count} users)")
    except Exception as e:
        print(f"   ❌ User model failed: {e}")
        import traceback
        traceback.print_exc()
        exit(1)

print("\n✅ All tests passed!")



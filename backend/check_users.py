#!/usr/bin/env python
"""Check users in database"""
from app import app, db, User

with app.app_context():
    users = User.query.all()
    print(f"\n📊 Users in database: {len(users)}")
    if users:
        print("\n👥 User list:")
        for u in users:
            print(f"  - Username: {u.username}")
            print(f"    Email: {u.email}")
            print(f"    ID: {u.id}")
            print(f"    Active: {u.is_active}")
            print(f"    Credits: {u.image_credits}")
            print()
    else:
        print("\n⚠️  No users found in database!")
        print("   You need to register a user first before you can login.")
        print("   Go to the frontend and register a new account.")



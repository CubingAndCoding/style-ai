#!/usr/bin/env python3
"""
Production Setup Script for Style AI Backend
Generates secure keys and validates environment configuration
"""

import secrets
import os
import sys
from dotenv import load_dotenv

def generate_secure_key():
    """Generate a secure random key"""
    return secrets.token_urlsafe(32)

def check_environment():
    """Check if required environment variables are set"""
    required_vars = [
        'JWT_SECRET_KEY',
        'GOOGLE_API_KEY',
        'STRIPE_SECRET_KEY'
    ]
    
    missing_vars = []
    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)
    
    return missing_vars

def main():
    print("🔐 Style AI Backend - Production Setup")
    print("=" * 50)
    
    # Generate secure keys
    print("\n📝 Generated Secure Keys:")
    print(f"JWT_SECRET_KEY={generate_secure_key()}")
    print(f"SECRET_KEY={generate_secure_key()}")
    
    # Check environment
    print("\n🔍 Environment Check:")
    load_dotenv()
    missing = check_environment()
    
    if missing:
        print("❌ Missing required environment variables:")
        for var in missing:
            print(f"   - {var}")
        print("\n💡 Add these to your Railway project Variables tab")
    else:
        print("✅ All required environment variables are set!")
    
    print("\n📋 Next Steps:")
    print("1. Copy the generated keys to your Railway Variables")
    print("2. Set your API keys (Google, Stripe, etc.)")
    print("3. Update CORS_ORIGINS with your frontend domain")
    print("4. Deploy to Railway")
    
    print("\n🚀 Ready for production deployment!")

if __name__ == "__main__":
    main()

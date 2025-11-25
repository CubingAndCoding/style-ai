#!/usr/bin/env python
"""Quick test script to check registration functionality"""
import requests
import json

# Test registration endpoint
API_URL = "http://127.0.0.1:5000"

print("Testing registration endpoint...")
print("=" * 80)

# Test data
test_username = input("Enter username to register: ").strip()
test_email = input("Enter email to register: ").strip()
test_password = input("Enter password to register: ").strip()

data = {
    "username": test_username,
    "email": test_email,
    "password": test_password
}

print(f"\n📤 Sending POST request to: {API_URL}/auth/register")
print(f"📤 Request data: {json.dumps(data, indent=2)}")

try:
    response = requests.post(f"{API_URL}/auth/register", json=data, timeout=10)
    print(f"\n📥 Response Status: {response.status_code}")
    print(f"📥 Response Headers: {dict(response.headers)}")
    
    try:
        response_data = response.json()
        print(f"📥 Response Data: {json.dumps(response_data, indent=2)}")
    except:
        print(f"📥 Response Text: {response.text}")
        
    if response.status_code == 201:
        print("\n✅ Registration successful!")
        if 'access_token' in response_data:
            print(f"   Access token received: {response_data['access_token'][:50]}...")
    else:
        print(f"\n❌ Registration failed with status {response.status_code}")
        
except requests.exceptions.ConnectionError:
    print("\n❌ ERROR: Could not connect to backend!")
    print("   Make sure the backend is running on http://127.0.0.1:5000")
except Exception as e:
    print(f"\n❌ ERROR: {e}")



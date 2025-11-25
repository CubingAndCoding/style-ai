#!/usr/bin/env python
"""Quick test script to check login functionality"""
import requests
import json

# Test login endpoint
API_URL = "http://127.0.0.1:5000"

print("Testing login endpoint...")
print("=" * 80)

# Test data - adjust these to match what you're trying to login with
test_username = input("Enter username/email to test: ").strip()
test_password = input("Enter password to test: ").strip()

data = {
    "username": test_username,
    "password": test_password
}

print(f"\n📤 Sending POST request to: {API_URL}/auth/login")
print(f"📤 Request data: {json.dumps(data, indent=2)}")

try:
    response = requests.post(f"{API_URL}/auth/login", json=data, timeout=10)
    print(f"\n📥 Response Status: {response.status_code}")
    print(f"📥 Response Headers: {dict(response.headers)}")
    
    try:
        response_data = response.json()
        print(f"📥 Response Data: {json.dumps(response_data, indent=2)}")
    except:
        print(f"📥 Response Text: {response.text}")
        
    if response.status_code == 200:
        print("\n✅ Login successful!")
    else:
        print(f"\n❌ Login failed with status {response.status_code}")
        
except requests.exceptions.ConnectionError:
    print("\n❌ ERROR: Could not connect to backend!")
    print("   Make sure the backend is running on http://127.0.0.1:5000")
except Exception as e:
    print(f"\n❌ ERROR: {e}")



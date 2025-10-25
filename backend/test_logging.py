#!/usr/bin/env python3
"""
Backend Logging Test Script
This script tests the backend API endpoints to verify logging is working correctly.
"""

import requests
import json
import time
import sys

# Configuration
BASE_URL = "http://localhost:5000"  # Change this to your backend URL
TEST_USERNAME = f"testuser_{int(time.time())}"
TEST_EMAIL = f"test_{int(time.time())}@example.com"
TEST_PASSWORD = "testpass123"

def test_registration():
    """Test user registration endpoint"""
    print("🧪 Testing Registration Endpoint...")
    print("=" * 50)
    
    url = f"{BASE_URL}/auth/register"
    data = {
        "username": TEST_USERNAME,
        "email": TEST_EMAIL,
        "password": TEST_PASSWORD
    }
    
    print(f"📤 Sending POST request to: {url}")
    print(f"📤 Request data: {json.dumps(data, indent=2)}")
    
    try:
        response = requests.post(url, json=data, timeout=10)
        print(f"📥 Response Status: {response.status_code}")
        print(f"📥 Response Data: {json.dumps(response.json(), indent=2)}")
        return response.status_code == 201
    except requests.exceptions.RequestException as e:
        print(f"❌ Request failed: {e}")
        return False

def test_login():
    """Test user login endpoint"""
    print("\n🧪 Testing Login Endpoint...")
    print("=" * 50)
    
    url = f"{BASE_URL}/auth/login"
    data = {
        "username": TEST_USERNAME,
        "password": TEST_PASSWORD
    }
    
    print(f"📤 Sending POST request to: {url}")
    print(f"📤 Request data: {json.dumps(data, indent=2)}")
    
    try:
        response = requests.post(url, json=data, timeout=10)
        print(f"📥 Response Status: {response.status_code}")
        print(f"📥 Response Data: {json.dumps(response.json(), indent=2)}")
        return response.status_code == 200
    except requests.exceptions.RequestException as e:
        print(f"❌ Request failed: {e}")
        return False

def test_duplicate_registration():
    """Test duplicate registration (should fail)"""
    print("\n🧪 Testing Duplicate Registration...")
    print("=" * 50)
    
    url = f"{BASE_URL}/auth/register"
    data = {
        "username": TEST_USERNAME,  # Same username as before
        "email": f"different_{int(time.time())}@example.com",
        "password": TEST_PASSWORD
    }
    
    try:
        response = requests.post(url, json=data, timeout=10)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.json()}")
        return response.status_code == 400  # Should fail
    except requests.exceptions.RequestException as e:
        print(f"Request failed: {e}")
        return False

def test_invalid_login():
    """Test invalid login credentials"""
    print("\n🧪 Testing Invalid Login...")
    print("=" * 50)
    
    url = f"{BASE_URL}/auth/login"
    data = {
        "username": "nonexistent_user",
        "password": "wrongpassword"
    }
    
    try:
        response = requests.post(url, json=data, timeout=10)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.json()}")
        return response.status_code == 401  # Should fail
    except requests.exceptions.RequestException as e:
        print(f"Request failed: {e}")
        return False

def main():
    """Run all tests"""
    print("🚀 Backend Logging Test Suite")
    print("=" * 60)
    print(f"Testing backend at: {BASE_URL}")
    print(f"Test username: {TEST_USERNAME}")
    print(f"Test email: {TEST_EMAIL}")
    print("=" * 60)
    
    # Check if backend is running
    try:
        response = requests.get(f"{BASE_URL}/", timeout=5)
        print("✅ Backend is running")
    except requests.exceptions.RequestException:
        print("❌ Backend is not running or not accessible")
        print("Please start the backend server first:")
        print("  cd backend")
        print("  python app.py")
        sys.exit(1)
    
    # Run tests
    tests = [
        ("Registration", test_registration),
        ("Login", test_login),
        ("Duplicate Registration", test_duplicate_registration),
        ("Invalid Login", test_invalid_login)
    ]
    
    results = []
    for test_name, test_func in tests:
        print(f"\n{'='*60}")
        print(f"Running: {test_name}")
        print(f"{'='*60}")
        
        try:
            result = test_func()
            results.append((test_name, result))
            status = "✅ PASSED" if result else "❌ FAILED"
            print(f"\n{test_name}: {status}")
        except Exception as e:
            print(f"\n{test_name}: ❌ ERROR - {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "="*60)
    print("📊 TEST SUMMARY")
    print("="*60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{test_name}: {status}")
    
    print(f"\nOverall: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Check your backend logs for detailed information.")
    else:
        print("⚠️  Some tests failed. Check the backend logs for more details.")
    
    print("\n💡 Check your backend console/logs to see the detailed logging output!")

if __name__ == "__main__":
    main()

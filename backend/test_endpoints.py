"""Test script to verify all API endpoints are accessible"""
import requests
import sys

# Use your actual Render URL
BASE_URL = "https://agrivision2.onrender.com"

def test_endpoint(url, method="GET", data=None):
    try:
        if method == "GET":
            response = requests.get(url, timeout=10)
        elif method == "POST":
            response = requests.post(url, json=data, timeout=10)
        
        print(f"✓ {method} {url}")
        print(f"  Status: {response.status_code}")
        print(f"  Response: {response.text[:100]}...")
        return response.status_code
    except Exception as e:
        print(f"✗ {method} {url}")
        print(f"  Error: {str(e)}")
        return None

print("=" * 60)
print("Testing AgriVision Backend Endpoints")
print("=" * 60)
print()

# Test root
print("1. Testing Root Endpoint")
test_endpoint(f"{BASE_URL}/")
print()

# Test health
print("2. Testing Health Check")
test_endpoint(f"{BASE_URL}/health")
print()

# Test API v1 root
print("3. Testing API Docs")
test_endpoint(f"{BASE_URL}/api/v1/docs")
print()

# Test auth endpoints
print("4. Testing Login Endpoint (should return 422 without data)")
test_endpoint(f"{BASE_URL}/api/v1/auth/login", method="POST")
print()

print("5. Testing Login with credentials")
login_data = {
    "username": "farmer@test.com",
    "password": "password123"
}
test_endpoint(f"{BASE_URL}/api/v1/auth/login", method="POST", data=login_data)
print()

print("=" * 60)
print("Test Complete")
print("=" * 60)

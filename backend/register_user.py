import requests

url = "http://localhost:8000/api/v1/auth/register"
data = {
    "email": "farmer@example.com",
    "password": "farmer123",
    "full_name": "Test Farmer",
    "role": "farmer"
}

try:
    response = requests.post(url, json=data)
    print(f"Status: {response.status_code}")
    print(f"Response: {response.text}")
except Exception as e:
    print(f"Error: {e}")

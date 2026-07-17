import requests

url = "http://localhost:8000/api/v1/auth/register"

users = [
    {
        "email": "admin@agrivision.com",
        "password": "admin123",
        "full_name": "Admin User",
        "role": "admin"
    },
    {
        "email": "expert@example.com",
        "password": "expert123",
        "full_name": "Agricultural Expert",
        "role": "expert"
    }
]

for user_data in users:
    try:
        response = requests.post(url, json=user_data)
        if response.status_code == 201:
            print(f"✓ Created: {user_data['email']}")
        else:
            print(f"✗ Failed {user_data['email']}: {response.text}")
    except Exception as e:
        print(f"✗ Error {user_data['email']}: {e}")

print("\n✅ All users created! Login credentials:")
print("  - farmer@example.com / farmer123")
print("  - admin@agrivision.com / admin123")
print("  - expert@example.com / expert123")

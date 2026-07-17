import asyncio
import httpx

async def create_users():
    base_url = "http://localhost:8000/api/v1"
    
    users = [
        {
            "email": "farmer@example.com",
            "password": "farmer123",
            "full_name": "Test Farmer",
            "role": "farmer"
        },
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
    
    async with httpx.AsyncClient() as client:
        for user in users:
            try:
                response = await client.post(
                    f"{base_url}/auth/register",
                    json=user
                )
                if response.status_code == 200:
                    print(f"✓ Created user: {user['email']}")
                else:
                    print(f"✗ Failed to create {user['email']}: {response.text}")
            except Exception as e:
                print(f"✗ Error creating {user['email']}: {e}")

if __name__ == "__main__":
    print("Creating test users...")
    asyncio.run(create_users())
    print("\nDone! You can now login with:")
    print("  - farmer@example.com / farmer123")
    print("  - admin@agrivision.com / admin123")
    print("  - expert@example.com / expert123")

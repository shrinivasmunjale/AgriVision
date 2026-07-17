"""Create test accounts for AgriVision"""
import asyncio
import sys
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy.future import select
from app.models.user import User
from app.core.security import get_password_hash
from app.core.config import settings

async def create_test_users():
    # Create async engine
    engine = create_async_engine(settings.DATABASE_URL, echo=False)
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    
    test_users = [
        {
            'email': 'farmer@test.com',
            'name': 'Test Farmer',
            'role': 'farmer',
            'password': 'password123',
            'farm_name': 'Test Farm',
            'phone': '1234567890'
        },
        {
            'email': 'admin@test.com',
            'name': 'Test Admin',
            'role': 'admin',
            'password': 'password123',
            'farm_name': '',
            'phone': ''
        },
        {
            'email': 'expert@test.com',
            'name': 'Test Expert',
            'role': 'expert',
            'password': 'password123',
            'farm_name': '',
            'phone': ''
        }
    ]
    
    print("=" * 60)
    print("Creating Test Users for AgriVision")
    print("=" * 60)
    
    async with async_session() as db:
        for user_data in test_users:
            # Check if user exists
            result = await db.execute(select(User).filter(User.email == user_data['email']))
            existing_user = result.scalars().first()
            
            if existing_user:
                # Update password
                existing_user.hashed_password = get_password_hash(user_data['password'])
                existing_user.name = user_data['name']
                existing_user.role = user_data['role']
                print(f"✓ Updated user: {user_data['email']}")
            else:
                # Create new user
                new_user = User(
                    email=user_data['email'],
                    name=user_data['name'],
                    role=user_data['role'],
                    hashed_password=get_password_hash(user_data['password']),
                    farm_name=user_data.get('farm_name', ''),
                    phone=user_data.get('phone', '')
                )
                db.add(new_user)
                print(f"✓ Created user: {user_data['email']}")
        
        await db.commit()
    
    await engine.dispose()
    
    print("\n" + "=" * 60)
    print("Test Users Created Successfully!")
    print("=" * 60)
    print("\nLogin Credentials:")
    print("  Farmer: farmer@test.com / password123")
    print("  Admin:  admin@test.com  / password123")
    print("  Expert: expert@test.com / password123")
    print("\nYou can now use these credentials to login!")
    print("=" * 60)

if __name__ == "__main__":
    asyncio.run(create_test_users())

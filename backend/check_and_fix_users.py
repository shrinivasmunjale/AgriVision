"""Check database users and ensure test users exist with correct passwords"""
import sqlite3
import asyncio
from app.core.security import get_password_hash, verify_password
from app.db.session import get_db
from app.models.user import User
from sqlalchemy import select

async def check_and_fix_users():
    print("=" * 60)
    print("Checking Database Users")
    print("=" * 60)
    
    # Check using SQLite directly first
    conn = sqlite3.connect('agrivision.db')
    cursor = conn.cursor()
    
    try:
        cursor.execute('SELECT id, email, name, role, hashed_password FROM users')
        rows = cursor.fetchall()
        
        print(f"\nFound {len(rows)} users in database:")
        print("-" * 60)
        
        for row in rows:
            user_id, email, name, role, hashed_password = row
            has_password = bool(hashed_password)
            print(f"ID: {user_id}")
            print(f"  Email: {email}")
            print(f"  Name: {name}")
            print(f"  Role: {role}")
            print(f"  Has Password: {has_password}")
            
            if has_password:
                # Test if password123 works
                try:
                    if verify_password('password123', hashed_password):
                        print(f"  ✓ Password 'password123' works!")
                    else:
                        print(f"  ✗ Password 'password123' does NOT work")
                except Exception as e:
                    print(f"  ✗ Error verifying password: {e}")
            print()
        
        conn.close()
        
        # If no users with hashed passwords, create them
        if not any(row[4] for row in rows):
            print("\n" + "=" * 60)
            print("No users with passwords found. Creating test users...")
            print("=" * 60)
            
            test_users = [
                {
                    'email': 'farmer@test.com',
                    'name': 'Test Farmer',
                    'role': 'farmer',
                    'password': 'password123'
                },
                {
                    'email': 'admin@test.com',
                    'name': 'Test Admin',
                    'role': 'admin',
                    'password': 'password123'
                },
                {
                    'email': 'expert@test.com',
                    'name': 'Test Expert',
                    'role': 'expert',
                    'password': 'password123'
                }
            ]
            
            conn = sqlite3.connect('agrivision.db')
            cursor = conn.cursor()
            
            for user_data in test_users:
                # Check if user exists
                cursor.execute('SELECT id FROM users WHERE email = ?', (user_data['email'],))
                existing = cursor.fetchone()
                
                hashed_pw = get_password_hash(user_data['password'])
                
                if existing:
                    # Update existing user
                    cursor.execute(
                        'UPDATE users SET hashed_password = ?, name = ?, role = ? WHERE email = ?',
                        (hashed_pw, user_data['name'], user_data['role'], user_data['email'])
                    )
                    print(f"✓ Updated {user_data['email']}")
                else:
                    # Insert new user
                    cursor.execute(
                        '''INSERT INTO users (email, name, role, hashed_password, farm_name, phone) 
                           VALUES (?, ?, ?, ?, '', '')''',
                        (user_data['email'], user_data['name'], user_data['role'], hashed_pw)
                    )
                    print(f"✓ Created {user_data['email']}")
            
            conn.commit()
            conn.close()
            
            print("\n" + "=" * 60)
            print("Test users created/updated successfully!")
            print("=" * 60)
            print("\nLogin credentials:")
            print("  Email: farmer@test.com / Password: password123")
            print("  Email: admin@test.com  / Password: password123")
            print("  Email: expert@test.com / Password: password123")
        else:
            print("\n" + "=" * 60)
            print("Users with passwords already exist")
            print("=" * 60)
    
    except Exception as e:
        print(f"\nError: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(check_and_fix_users())

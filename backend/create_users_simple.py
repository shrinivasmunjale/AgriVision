"""Simple script to create test users - no async needed"""
import sqlite3
import bcrypt

# Connect to database
conn = sqlite3.connect('agrivision.db')
cursor = conn.cursor()

# Test users
users = [
    ('farmer@test.com', 'Test Farmer', 'farmer', 'password123'),
    ('admin@test.com', 'Test Admin', 'admin', 'password123'),
    ('expert@test.com', 'Test Expert', 'expert', 'password123'),
]

print("Creating test users...")
print("=" * 60)

for email, name, role, password in users:
    # Hash password
    hashed = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
    
    # Create user ID
    user_id = email.split('@')[0] + '-test-id'
    
    # Check if exists
    cursor.execute('SELECT id FROM users WHERE email = ?', (email,))
    existing = cursor.fetchone()
    
    if existing:
        # Update
        cursor.execute('''
            UPDATE users 
            SET name = ?, role = ?, hashed_password = ?, updated_at = datetime("now")
            WHERE email = ?
        ''', (name, role, hashed, email))
        print(f"✓ Updated: {email}")
    else:
        # Insert
        cursor.execute('''
            INSERT INTO users (id, email, name, role, hashed_password, farm_name, phone, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, '', '', datetime("now"), datetime("now"))
        ''', (user_id, email, name, role, hashed))
        print(f"✓ Created: {email}")

conn.commit()
conn.close()

print("=" * 60)
print("Done! Test accounts:")
print("  farmer@test.com / password123")
print("  admin@test.com / password123")
print("  expert@test.com / password123")

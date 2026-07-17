"""Simple script to check users in database"""
import sqlite3

conn = sqlite3.connect('agrivision.db')
cursor = conn.cursor()

print("=" * 60)
print("Users in Database")
print("=" * 60)

cursor.execute('SELECT id, email, name, role, hashed_password FROM users')
rows = cursor.fetchall()

if not rows:
    print("No users found in database!")
else:
    for row in rows:
        user_id, email, name, role, hashed_password = row
        print(f"\nID: {user_id}")
        print(f"Email: {email}")
        print(f"Name: {name}")
        print(f"Role: {role}")
        print(f"Has Password: {bool(hashed_password)}")
        if hashed_password:
            print(f"Password Hash (first 50 chars): {hashed_password[:50]}...")

conn.close()

print("\n" + "=" * 60)
print(f"Total users: {len(rows)}")
print("=" * 60)

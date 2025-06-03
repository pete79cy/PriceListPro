#!/usr/bin/env python3
"""
Create a working admin user for the orders system
"""
from werkzeug.security import generate_password_hash
import psycopg2
import os

def create_admin():
    # Get database connection
    db_url = os.environ.get('DATABASE_URL')
    
    # Generate proper password hash
    password_hash = generate_password_hash('admin123')
    
    # Connect to database
    conn = psycopg2.connect(db_url)
    cur = conn.cursor()
    
    # Delete existing admin user
    cur.execute('DELETE FROM "user" WHERE username = %s', ('admin',))
    
    # Create new admin user
    cur.execute('''
        INSERT INTO "user" (username, password_hash, is_admin, created_at) 
        VALUES (%s, %s, %s, NOW())
    ''', ('admin', password_hash, True))
    
    conn.commit()
    cur.close()
    conn.close()
    
    print("Admin user created successfully")
    print("Username: admin")
    print("Password: admin123")

if __name__ == '__main__':
    create_admin()
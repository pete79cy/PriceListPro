#!/usr/bin/env python3
"""
Script to set admin password for testing the orders system
"""
from app import app, db
from models import User
from werkzeug.security import generate_password_hash

def set_admin_password():
    with app.app_context():
        # Find the admin user
        admin_user = User.query.filter_by(username='admin').first()
        
        if admin_user:
            # Set password to 'admin123'
            admin_user.password_hash = generate_password_hash('admin123')
            db.session.commit()
            print("Admin password set to 'admin123'")
        else:
            # Create admin user if it doesn't exist
            admin_user = User(
                username='admin',
                password_hash=generate_password_hash('admin123'),
                is_admin=True
            )
            db.session.add(admin_user)
            db.session.commit()
            print("Admin user created with password 'admin123'")

if __name__ == '__main__':
    set_admin_password()
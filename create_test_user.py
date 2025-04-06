from app import app, db
from models import User

with app.app_context():
    # Create a new test user
    user = User(username='testuser', is_admin=True)
    user.set_password('password123')
    db.session.add(user)
    db.session.commit()
    print('Test user created successfully!')
from app import app, db
from models import CustomerCategory, CustomerContact

# Run this script to update the database schema after adding new models

with app.app_context():
    db.create_all()
    
    # Create default customer category if none exists
    if CustomerCategory.query.count() == 0:
        default_category = CustomerCategory(name="General", description="Default category for customers")
        db.session.add(default_category)
        db.session.commit()
        print("Created default customer category 'General'")
    
    print("Database schema updated successfully")
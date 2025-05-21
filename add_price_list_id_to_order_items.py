"""
Migration script to add price_list_id to OrderItem model.

This script adds a price_list_id column to the order_item table
to fix a missing column issue.
"""
from app import app, db
from models import OrderItem
from sqlalchemy import Column, Integer, ForeignKey
import sqlalchemy as sa

def run_migration():
    """Add price_list_id field to OrderItem table"""
    with app.app_context():
        # Check if the column exists
        from sqlalchemy import inspect
        inspector = inspect(db.engine)
        columns = [col['name'] for col in inspector.get_columns('order_item')]
        
        if 'price_list_id' not in columns:
            print("Adding price_list_id column to order_item table...")
            # Add the column - using modern SQLAlchemy execution approach
            with db.engine.connect() as conn:
                conn.execute(sa.text('ALTER TABLE order_item ADD COLUMN price_list_id INTEGER REFERENCES price_list(id)'))
                conn.commit()
            print("Migration complete!")
        else:
            print("price_list_id column already exists in order_item table")

if __name__ == '__main__':
    run_migration()
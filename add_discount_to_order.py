"""
Migration script to add discount field to Order model.

This script adds discount fields to the order table to support 
order-level discounts on the total amount.
"""

import os
import sys
from datetime import datetime

# Add the current directory to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import app, db
from models import Order

def run_migration():
    """Add discount fields to Order table"""
    with app.app_context():
        try:
            # Check if discount_percentage column exists
            inspector = db.inspect(db.engine)
            columns = [col['name'] for col in inspector.get_columns('order')]
            
            if 'discount_percentage' not in columns:
                # Add discount_percentage column
                db.engine.execute(
                    'ALTER TABLE "order" ADD COLUMN discount_percentage REAL DEFAULT 0.0'
                )
                print("✅ Added discount_percentage column to order table")
            else:
                print("ℹ️  discount_percentage column already exists")
                
            if 'discount_amount' not in columns:
                # Add discount_amount column
                db.engine.execute(
                    'ALTER TABLE "order" ADD COLUMN discount_amount REAL DEFAULT 0.0'
                )
                print("✅ Added discount_amount column to order table")
            else:
                print("ℹ️  discount_amount column already exists")
                
            if 'discount_type' not in columns:
                # Add discount_type column (percentage or fixed)
                db.engine.execute(
                    'ALTER TABLE "order" ADD COLUMN discount_type VARCHAR(20) DEFAULT \'percentage\''
                )
                print("✅ Added discount_type column to order table")
            else:
                print("ℹ️  discount_type column already exists")
                
            # Commit the changes
            db.session.commit()
            print("✅ Migration completed successfully!")
            
        except Exception as e:
            print(f"❌ Migration failed: {e}")
            db.session.rollback()
            raise

if __name__ == '__main__':
    run_migration()
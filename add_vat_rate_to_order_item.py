"""
Migration script to add vat_rate field to OrderItem model.

This script adds a vat_rate column to the order_item table
to enable VAT calculations at different rates (e.g., 5%, 19%).
"""

from app import app, db
from sqlalchemy import Column, Float

def run_migration():
    """Add vat_rate field to OrderItem table"""
    with app.app_context():
        try:
            # Check if the column already exists
            query = "SELECT column_name FROM information_schema.columns WHERE table_name = 'order_item' AND column_name = 'vat_rate'"
            result = db.session.execute(query).fetchone()
            
            if result is None:
                # The column doesn't exist, add it
                print("Adding vat_rate column to order_item table...")
                db.session.execute("ALTER TABLE order_item ADD COLUMN vat_rate FLOAT NOT NULL DEFAULT 19.0")
                db.session.commit()
                print("Migration successful - added vat_rate column to order_item table")
                return True
            else:
                print("Column vat_rate already exists in order_item table. No changes made.")
                return True
                
        except Exception as e:
            db.session.rollback()
            print(f"Error during migration: {str(e)}")
            return False

if __name__ == '__main__':
    print("Starting OrderItem VAT Rate migration...")
    success = run_migration()
    print("Migration completed" if success else "Migration failed")
"""
Migration script to add pricing_status field to QuotationItem model.

This script adds a pricing_status column to the quotation_item table
to track items that need pricing from suppliers.
"""

import os
import sys
from sqlalchemy import text

# Add the project root to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import app, db

def run_migration():
    """Add pricing_status field to QuotationItem table"""
    
    with app.app_context():
        try:
            # Add the pricing_status column
            db.session.execute(text("""
                ALTER TABLE quotation_item 
                ADD COLUMN IF NOT EXISTS pricing_status VARCHAR(20) DEFAULT 'CONFIRMED'
            """))
            
            # Update existing items to have CONFIRMED status
            db.session.execute(text("""
                UPDATE quotation_item 
                SET pricing_status = 'CONFIRMED' 
                WHERE pricing_status IS NULL
            """))
            
            # Allow selling_price to be NULL for pending items
            db.session.execute(text("""
                ALTER TABLE quotation_item 
                ALTER COLUMN selling_price DROP NOT NULL
            """))
            
            db.session.commit()
            print("✅ Successfully added pricing_status field to QuotationItem table")
            return True
            
        except Exception as e:
            db.session.rollback()
            print(f"❌ Error adding pricing_status field: {str(e)}")
            return False

if __name__ == "__main__":
    success = run_migration()
    sys.exit(0 if success else 1)
"""
Migration script to add total_override_amount field to Order model.

This script adds a total_override_amount column to the order table
to support manual final total override for precise invoice totals.
"""

import os
import logging
from sqlalchemy import create_engine, text
from app import app

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def run_migration():
    """Add total_override_amount field to Order table"""
    
    # Get database URL from environment
    database_url = os.environ.get('DATABASE_URL')
    if not database_url:
        logger.error("DATABASE_URL environment variable not set")
        return False
    
    try:
        # Create engine
        engine = create_engine(database_url)
        
        # Add the new column
        logger.info("Adding total_override_amount column to order table...")
        with engine.connect() as conn:
            # Add the column
            conn.execute(text("""
                ALTER TABLE "order" 
                ADD COLUMN total_override_amount FLOAT;
            """))
            conn.commit()
            logger.info("✅ Successfully added total_override_amount column")
        
        return True
        
    except Exception as e:
        if "already exists" in str(e).lower():
            logger.info("✅ total_override_amount column already exists")
            return True
        else:
            logger.error(f"❌ Error adding total_override_amount column: {e}")
            return False

if __name__ == "__main__":
    with app.app_context():
        success = run_migration()
        if success:
            print("✅ Migration completed successfully")
        else:
            print("❌ Migration failed")
"""
Migration script to add quotation support to delivery adjustments.

This script adds the necessary columns to support delivery adjustments 
for both orders and quotations.
"""

import os
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def get_db_connection():
    """Get database connection from environment variables"""
    database_url = os.environ.get('DATABASE_URL')
    if not database_url:
        raise ValueError("DATABASE_URL environment variable not set")
    
    return psycopg2.connect(database_url)

def run_migration():
    """Add quotation support to delivery adjustments"""
    try:
        conn = get_db_connection()
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cursor = conn.cursor()
        
        logger.info("Starting delivery adjustments migration for quotations...")
        
        # Check if columns already exist
        cursor.execute("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name = 'delivery_adjustment' 
            AND column_name IN ('quotation_id');
        """)
        existing_columns = [row[0] for row in cursor.fetchall()]
        
        if 'quotation_id' not in existing_columns:
            logger.info("Adding quotation_id column to delivery_adjustment table...")
            cursor.execute("""
                ALTER TABLE delivery_adjustment 
                ADD COLUMN quotation_id INTEGER REFERENCES quotation(id);
            """)
            logger.info("✓ Added quotation_id column")
        else:
            logger.info("quotation_id column already exists")
        
        # Check if columns already exist for final_proforma_invoice
        cursor.execute("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name = 'final_proforma_invoice' 
            AND column_name IN ('quotation_id');
        """)
        existing_fpi_columns = [row[0] for row in cursor.fetchall()]
        
        if 'quotation_id' not in existing_fpi_columns:
            logger.info("Adding quotation_id column to final_proforma_invoice table...")
            cursor.execute("""
                ALTER TABLE final_proforma_invoice 
                ADD COLUMN quotation_id INTEGER REFERENCES quotation(id);
            """)
            logger.info("✓ Added quotation_id column to final_proforma_invoice")
        else:
            logger.info("quotation_id column already exists in final_proforma_invoice")
        
        # Make order_id nullable in delivery_adjustment table
        logger.info("Making order_id nullable in delivery_adjustment table...")
        cursor.execute("""
            ALTER TABLE delivery_adjustment 
            ALTER COLUMN order_id DROP NOT NULL;
        """)
        logger.info("✓ Made order_id nullable in delivery_adjustment")
        
        # Make order_id nullable in final_proforma_invoice table
        logger.info("Making order_id nullable in final_proforma_invoice table...")
        cursor.execute("""
            ALTER TABLE final_proforma_invoice 
            ALTER COLUMN order_id DROP NOT NULL;
        """)
        logger.info("✓ Made order_id nullable in final_proforma_invoice")
        
        # Add constraint to ensure either order_id or quotation_id is set (but not both)
        logger.info("Adding constraint to ensure either order_id or quotation_id is set...")
        cursor.execute("""
            ALTER TABLE delivery_adjustment 
            ADD CONSTRAINT check_delivery_adjustment_parent 
            CHECK (
                (order_id IS NOT NULL AND quotation_id IS NULL) OR 
                (order_id IS NULL AND quotation_id IS NOT NULL)
            );
        """)
        logger.info("✓ Added constraint for delivery_adjustment parent")
        
        cursor.execute("""
            ALTER TABLE final_proforma_invoice 
            ADD CONSTRAINT check_final_proforma_invoice_parent 
            CHECK (
                (order_id IS NOT NULL AND quotation_id IS NULL) OR 
                (order_id IS NULL AND quotation_id IS NOT NULL)
            );
        """)
        logger.info("✓ Added constraint for final_proforma_invoice parent")
        
        cursor.close()
        conn.close()
        
        logger.info("✅ Migration completed successfully!")
        return True
        
    except Exception as e:
        logger.error(f"❌ Migration failed: {e}")
        if 'cursor' in locals():
            cursor.close()
        if 'conn' in locals():
            conn.close()
        return False

if __name__ == "__main__":
    success = run_migration()
    if success:
        print("Migration completed successfully!")
    else:
        print("Migration failed!")
        exit(1)
#!/usr/bin/env python
"""
Migration script to add status workflow fields to Quotation model.

This script adds status fields to the quotation table
and sets the initial status values based on existing quotations.
"""

import sys
import os
import logging
from datetime import datetime, timedelta

# Set up logging
logging.basicConfig(level=logging.INFO, 
                   format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Add the application directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

# Import app and models
from app import app, db
from models import Quotation, QuotationStatus

def run_migration():
    """Add status fields to Quotation table and set initial values"""
    try:
        with app.app_context():
            # Check if the migration has already been applied
            # by checking if the 'status' column exists
            inspector = db.inspect(db.engine)
            columns = [column['name'] for column in inspector.get_columns('quotation')]
            
            if 'status' in columns:
                logger.info("Status column already exists. Migration already applied.")
                return True
                
            # Add the status and related columns to the quotation table
            logger.info("Adding status columns to quotation table...")
            
            # SQLAlchemy doesn't support adding multiple columns in a single ALTER TABLE statement
            # So we need to execute raw SQL for better performance
            
            # For SQLite (development environment)
            if db.engine.url.drivername == 'sqlite':
                # SQLite doesn't support ALTER TABLE ADD COLUMN with DEFAULT values
                # We'd need to create a new table and copy data, which is complex
                # For simplicity in development, we'll add columns one by one
                
                for column_def in [
                    "status VARCHAR(20) NOT NULL DEFAULT 'DRAFT'",
                    "valid_until DATE",
                    "viewed_at TIMESTAMP",
                    "accepted_at TIMESTAMP",
                    "rejected_at TIMESTAMP",
                    "order_id VARCHAR(50)"
                ]:
                    column_name = column_def.split()[0]
                    if column_name not in columns:
                        db.engine.execute(f"ALTER TABLE quotation ADD COLUMN {column_def}")
                        
            # For PostgreSQL (production environment)
            else:
                db.engine.execute("""
                    ALTER TABLE quotation 
                    ADD COLUMN status VARCHAR(20) NOT NULL DEFAULT 'DRAFT',
                    ADD COLUMN valid_until DATE,
                    ADD COLUMN viewed_at TIMESTAMP,
                    ADD COLUMN accepted_at TIMESTAMP,
                    ADD COLUMN rejected_at TIMESTAMP,
                    ADD COLUMN order_id VARCHAR(50)
                """)
                
            # Update all quotations to have valid_until date (30 days after quotation_date)
            logger.info("Setting valid_until dates for existing quotations...")
            quotations = Quotation.query.all()
            count = 0
            
            for quotation in quotations:
                # Set valid_until to 30 days after quotation_date
                if quotation.quotation_date:
                    quotation.valid_until = quotation.quotation_date + timedelta(days=30)
                    
                # If there's any existing status information, use it
                # Otherwise, keep the default DRAFT status
                
                count += 1
                
            db.session.commit()
            logger.info(f"Updated {count} quotations with valid_until dates")
            
            logger.info("Migration completed successfully")
            return True
            
    except Exception as e:
        logger.error(f"Error during migration: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())
        return False

if __name__ == "__main__":
    logger.info("Starting quotation status workflow migration...")
    if run_migration():
        logger.info("Migration completed successfully")
        sys.exit(0)
    else:
        logger.error("Migration failed")
        sys.exit(1)
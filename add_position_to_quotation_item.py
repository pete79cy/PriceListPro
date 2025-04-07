"""
Migration script to add position field to QuotationItem model.

This script adds a position column to the quotation_item table
and sets the initial position values based on item IDs for each quotation.
"""

from app import app, db
from models import Quotation, QuotationItem
import logging
from sqlalchemy import text

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def run_migration():
    """Add position field to QuotationItem table and set initial values"""
    logger.info("Starting migration: Adding position field to QuotationItem")
    
    with app.app_context():
        try:
            # Check if the column already exists to avoid errors
            column_exists = False
            
            try:
                # Try to query an item's position to see if the column exists
                QuotationItem.query.with_entities(QuotationItem.position).first()
                column_exists = True
                logger.info("Position column already exists, skipping column creation")
            except Exception:
                logger.info("Position column does not exist yet, will create it")
            
            if not column_exists:
                # Add the position column to the table
                db.session.execute(text(
                    "ALTER TABLE quotation_item ADD COLUMN position INTEGER DEFAULT 0"
                ))
                logger.info("Added position column to quotation_item table")
            
            # Update positions for existing quotation items
            quotations = Quotation.query.all()
            for quotation in quotations:
                # Get items ordered by ID (assumes this is the original order)
                items = QuotationItem.query.filter_by(quotation_id=quotation.id).order_by(QuotationItem.id).all()
                
                # Update positions
                for idx, item in enumerate(items):
                    item.position = idx
                
                logger.info(f"Updated positions for {len(items)} items in quotation {quotation.id}")
            
            # Commit the changes
            db.session.commit()
            logger.info("Migration completed successfully")
            return True
        except Exception as e:
            logger.error(f"Error during migration: {str(e)}")
            db.session.rollback()
            return False

if __name__ == "__main__":
    run_migration()
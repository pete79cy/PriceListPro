"""
Fix script for a specific quotation where item #14 is missing in the PDF output.
This script fixes the position values to ensure they are sequential and correct.
"""

import sys
import logging
from app import app, db
from models import Quotation, QuotationItem

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("quotation_fix")

def fix_quotation_positions(quotation_number):
    """
    Fix positions for items in a specific quotation.
    
    Args:
        quotation_number: The quotation number to fix
    """
    with app.app_context():
        try:
            # Find the quotation
            logger.info(f"Looking for quotation with number: {quotation_number}")
            quotation = Quotation.query.filter_by(quotation_number=quotation_number).first()
            
            if not quotation:
                logger.error(f"Quotation {quotation_number} not found")
                return False
            
            logger.info(f"Found quotation: ID={quotation.id}, Number={quotation.quotation_number}")
            
            # Get items sorted by ID (assuming this is the intended order)
            items = QuotationItem.query.filter_by(quotation_id=quotation.id).order_by(QuotationItem.id).all()
            
            logger.info(f"Found {len(items)} items for this quotation")
            
            # Print current positions
            logger.info("Current positions:")
            for idx, item in enumerate(items):
                logger.info(f"Item {idx+1}: ID={item.id}, Position={item.position}, Description={item.description[:30]}")
            
            # Update positions (starting from 1 to match display numbering)
            updated_count = 0
            for idx, item in enumerate(items):
                new_position = idx + 1
                if item.position != new_position:
                    logger.info(f"Updating item ID={item.id}: Position {item.position} -> {new_position}")
                    item.position = new_position
                    updated_count += 1
            
            # Commit changes if any were made
            if updated_count > 0:
                db.session.commit()
                logger.info(f"Updated {updated_count} item positions")
            else:
                logger.info("No position updates required")
            
            # Verify the fix
            fixed_items = QuotationItem.query.filter_by(quotation_id=quotation.id).order_by(QuotationItem.position).all()
            logger.info("Positions after fix:")
            for idx, item in enumerate(fixed_items):
                logger.info(f"Item {idx+1}: ID={item.id}, Position={item.position}, Description={item.description[:30]}")
            
            return True
                
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error fixing quotation positions: {str(e)}")
            return False

if __name__ == "__main__":
    if len(sys.argv) > 1:
        quotation_number = sys.argv[1]
    else:
        quotation_number = input("Enter the quotation number to fix: ")
    
    success = fix_quotation_positions(quotation_number)
    if success:
        logger.info(f"Successfully fixed positions for quotation {quotation_number}")
    else:
        logger.error(f"Failed to fix positions for quotation {quotation_number}")
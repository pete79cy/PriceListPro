"""
Fix script for quotation items positions.
This script addresses the issue where quotation line numbers in PDF output
are inconsistent due to items having incorrect positions.

This fix:
1. Updates all quotation items to have sequential positions based on their ID
2. Ensures PDF generation will use consistent ordering

Usage:
    python fix_quotation_item_positions.py [quotation_number]
"""

import sys
import logging
from app import app, db
from models import Quotation, QuotationItem

# Configure logging
logging.basicConfig(level=logging.INFO, 
                   format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def fix_quotation_positions(quotation_number=None):
    """
    Fix positions for all items in a quotation or all quotations.
    
    Args:
        quotation_number: Optional quotation number to fix a specific quotation,
                          or None to fix all quotations
    """
    try:
        with app.app_context():
            if quotation_number:
                # Fix a specific quotation
                quotation = Quotation.query.filter_by(quotation_number=quotation_number).first()
                if not quotation:
                    logger.error(f"Quotation not found: {quotation_number}")
                    return False
                
                logger.info(f"Fixing positions for quotation: {quotation.quotation_number}")
                _fix_positions_for_quotation(quotation)
                
            else:
                # Fix all quotations
                logger.info("Fixing positions for all quotations...")
                quotations = Quotation.query.all()
                for quotation in quotations:
                    logger.info(f"Processing quotation: {quotation.quotation_number}")
                    _fix_positions_for_quotation(quotation)
            
            # Commit all changes
            db.session.commit()
            logger.info("Position fixes have been applied successfully")
            return True
            
    except Exception as e:
        logger.error(f"Error fixing quotation positions: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())
        return False

def _fix_positions_for_quotation(quotation):
    """
    Fix positions for all items in a specific quotation.
    
    Args:
        quotation: The Quotation object whose items need position fixing
    """
    if not quotation.items:
        logger.warning(f"No items found in quotation {quotation.quotation_number}")
        return
    
    # Log the current state
    logger.info(f"Quotation {quotation.quotation_number} has {len(quotation.items)} items")
    
    # Sort items by ID for consistent ordering
    sorted_items = sorted(quotation.items, key=lambda x: x.id)
    
    # Update positions to be sequential
    for position, item in enumerate(sorted_items):
        old_position = item.position
        item.position = position
        logger.info(f"Item ID {item.id}: {old_position} -> {position}")
    
    logger.info(f"Updated {len(sorted_items)} item positions for quotation {quotation.quotation_number}")

def verify_quotation_positions(quotation_number):
    """
    Verify that positions are properly set for a specific quotation.
    
    Args:
        quotation_number: The quotation number to verify
    
    Returns:
        bool: True if positions are sequential, False otherwise
    """
    with app.app_context():
        quotation = Quotation.query.filter_by(quotation_number=quotation_number).first()
        if not quotation:
            logger.error(f"Quotation not found: {quotation_number}")
            return False
        
        if not quotation.items:
            logger.warning(f"No items found in quotation {quotation.quotation_number}")
            return True
        
        # Get sorted items
        sorted_items = sorted(quotation.items, key=lambda x: x.position)
        
        # Check if positions are sequential
        expected_position = 0
        for item in sorted_items:
            if item.position != expected_position:
                logger.error(f"Item ID {item.id} has position {item.position}, expected {expected_position}")
                return False
            expected_position += 1
        
        logger.info(f"Quotation {quotation.quotation_number} has correct sequential positions")
        return True

if __name__ == "__main__":
    if len(sys.argv) > 1:
        quotation_number = sys.argv[1]
        logger.info(f"Fixing positions for quotation {quotation_number}")
        if fix_quotation_positions(quotation_number):
            verify_result = verify_quotation_positions(quotation_number)
            if verify_result:
                logger.info(f"✅ Successfully fixed and verified positions for quotation {quotation_number}")
            else:
                logger.error(f"❌ Failed to verify positions for quotation {quotation_number} after fixing")
        else:
            logger.error(f"❌ Failed to fix positions for quotation {quotation_number}")
    else:
        logger.info("Fixing positions for all quotations")
        if fix_quotation_positions():
            logger.info(f"✅ Successfully fixed positions for all quotations")
        else:
            logger.error(f"❌ Failed to fix positions for all quotations")
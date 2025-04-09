"""
Fix script for all quotation items positions.
This script ensures that all quotation items have sequential positions (0, 1, 2, etc.)
which is critical for proper ordering and rendering in PDFs.

Running this once will fix position values for all existing quotations.
"""

import os
import sys
import logging
from datetime import datetime
from flask import Flask
from app import app, db
from models import Quotation, QuotationItem

# Configure logging
logging.basicConfig(level=logging.INFO,
                   format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("position_fix")

def fix_all_quotation_positions(quotation_number=None):
    """
    Fix positions for all items in all quotations, or a specific quotation.
    
    Args:
        quotation_number: Optional quotation number to fix a specific quotation,
                          or None to fix all quotations
    
    Returns:
        int: Number of quotations fixed
    """
    fixed_count = 0
    try:
        with app.app_context():
            # Get quotations to fix
            if quotation_number:
                quotations = Quotation.query.filter_by(quotation_number=quotation_number).all()
                if not quotations:
                    logger.error(f"Quotation not found: {quotation_number}")
                    return 0
            else:
                # Get all quotations
                quotations = Quotation.query.all()
                
            # Log summary
            logger.info(f"Fixing positions for {len(quotations)} quotation(s)")
            
            # Fix each quotation
            for quotation in quotations:
                logger.info(f"Processing quotation {quotation.quotation_number} with {len(quotation.items)} items")
                
                # Log current positions before fixing
                current_positions = [(item.id, item.position) for item in quotation.items]
                logger.info(f"Current positions (id, position): {current_positions}")
                
                # Sort items by ID to ensure consistent ordering
                sorted_items = sorted(quotation.items, key=lambda x: x.id)
                
                # Set sequential positions (0, 1, 2, ...)
                changes_made = False
                for i, item in enumerate(sorted_items):
                    if item.position != i:
                        item.position = i
                        changes_made = True
                        logger.info(f"Updated item ID {item.id}: position → {i}")
                
                # Commit changes if any positions were updated
                if changes_made:
                    db.session.commit()
                    fixed_count += 1
                    logger.info(f"✅ Fixed positions for quotation {quotation.quotation_number}")
                else:
                    logger.info(f"✓ No position changes needed for quotation {quotation.quotation_number}")
                    
                # Verify the fix
                positions = [item.position for item in 
                            QuotationItem.query.filter_by(quotation_id=quotation.id).order_by(QuotationItem.position).all()]
                expected = list(range(len(positions)))
                if positions != expected:
                    logger.warning(f"⚠️ Verification failed! Positions after fix: {positions}, Expected: {expected}")
                else:
                    logger.info(f"✓ Verification passed: positions are now sequential")
            
            logger.info(f"Fix complete! {fixed_count} quotation(s) were updated")
            return fixed_count
            
    except Exception as e:
        logger.error(f"Error fixing quotation positions: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())
        return 0

if __name__ == "__main__":
    # Get command line arguments
    quotation_number = sys.argv[1] if len(sys.argv) > 1 else None
    
    # Run the fix
    fixed = fix_all_quotation_positions(quotation_number)
    if fixed > 0:
        logger.info(f"✅ Successfully fixed {fixed} quotation(s)")
    else:
        logger.warning("⚠️ No quotations were fixed")
        sys.exit(1)
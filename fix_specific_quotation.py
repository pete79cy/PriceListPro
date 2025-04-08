"""
Fix script for a specific quotation where item #14 is missing in the PDF output.
This script fixes the position values to ensure they are sequential and correct.
"""

import sys
import logging
from app import app, db
from models import Quotation, QuotationItem

# Setup logging
logging.basicConfig(level=logging.INFO, 
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("quotation_fix")

def fix_quotation_positions(quotation_number):
    """
    Fix positions for items in a specific quotation.
    
    Args:
        quotation_number: The quotation number to fix
    """
    with app.app_context():
        # Find the quotation
        quotation = Quotation.query.filter_by(quotation_number=quotation_number).first()
        if not quotation:
            logger.error(f"No quotation found with number {quotation_number}")
            return False
        
        logger.info(f"Fixing quotation: {quotation.quotation_number} (ID: {quotation.id})")
        
        # Get items ordered by ID (assumes this is the intended order)
        items = QuotationItem.query.filter_by(quotation_id=quotation.id).order_by(QuotationItem.id).all()
        
        # Display original items
        logger.info(f"Found {len(items)} items to fix")
        logger.info("\nORIGINAL ITEM POSITIONS:")
        logger.info(f"{'ID':<6} {'Pos':<6} {'Description':<50}")
        logger.info("-" * 65)
        
        for item in items:
            logger.info(f"{item.id:<6} {item.position:<6} {item.description[:47] + '...' if len(item.description) > 50 else item.description:<50}")
        
        # Update positions to be sequential starting from 0
        updated_count = 0
        for idx, item in enumerate(items):
            # Only update if position is incorrect
            if item.position != idx:
                logger.info(f"Updating item ID {item.id}: position {item.position} → {idx}")
                item.position = idx
                updated_count += 1
        
        # Save changes if any updates were made
        if updated_count > 0:
            db.session.commit()
            logger.info(f"Updated {updated_count} items with sequential positions")
            
            # Display updated items
            logger.info("\nUPDATED ITEM POSITIONS:")
            logger.info(f"{'ID':<6} {'Pos':<6} {'Description':<50}")
            logger.info("-" * 65)
            
            items_after = QuotationItem.query.filter_by(quotation_id=quotation.id).order_by(QuotationItem.position).all()
            for item in items_after:
                logger.info(f"{item.id:<6} {item.position:<6} {item.description[:47] + '...' if len(item.description) > 50 else item.description:<50}")
            
            return True
        else:
            logger.info("No position updates needed - all items already have sequential positions")
            return True

if __name__ == "__main__":
    # Get quotation number from command line
    if len(sys.argv) > 1:
        quotation_number = sys.argv[1]
    else:
        print("Please provide a quotation number to fix, e.g.: python fix_specific_quotation.py PAK-2025-007")
        sys.exit(1)
    
    # Run the fix
    if fix_quotation_positions(quotation_number):
        print(f"\nSuccessfully fixed positions for quotation {quotation_number}")
        print("Next steps:")
        print("1. Try generating a PDF with the enhanced generator:")
        print(f"   python fix_missing_item14.py {quotation_number}")
        print("2. If all items appear correctly, apply the permanent fix to the template:")
        print("   python permanent_template_fix.py")
    else:
        print(f"\nFailed to fix positions for quotation {quotation_number}")
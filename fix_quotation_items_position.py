"""
Fix script for quotation items positions.
This script addresses the issue where quotation line numbers in PDF output
are inconsistent due to all items having position=0.

This fix:
1. Updates all quotation items to have sequential positions based on their ID
2. Ensures PDF generation will use consistent ordering

Usage:
    python fix_quotation_items_position.py [quotation_number]
"""

import sys
import logging
from app import app, db
from models import Quotation, QuotationItem

# Setup logging
logging.basicConfig(level=logging.INFO, 
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("quotation_fix")

def fix_quotation_positions(quotation_number=None):
    """
    Fix positions for all items in a quotation or all quotations.
    
    Args:
        quotation_number: Optional quotation number to fix a specific quotation,
                          or None to fix all quotations
    """
    with app.app_context():
        if quotation_number:
            # Find the specific quotation
            quotation = Quotation.query.filter_by(quotation_number=quotation_number).first()
            if not quotation:
                logger.error(f"No quotation found with number {quotation_number}")
                return False
            
            # Fix this specific quotation
            _fix_positions_for_quotation(quotation)
            
        else:
            # Get all quotations
            quotations = Quotation.query.all()
            logger.info(f"Found {len(quotations)} quotations to process")
            
            # Fix each quotation
            for quotation in quotations:
                _fix_positions_for_quotation(quotation)
        
        return True

def _fix_positions_for_quotation(quotation):
    """
    Fix positions for all items in a specific quotation.
    
    Args:
        quotation: The Quotation object whose items need position fixing
    """
    logger.info(f"Processing quotation: {quotation.quotation_number} (ID: {quotation.id})")
    
    # Get items ordered by ID (assumes this is the intended order)
    items = QuotationItem.query.filter_by(quotation_id=quotation.id).order_by(QuotationItem.id).all()
    
    # Display statistics
    if not items:
        logger.info(f"  No items found for quotation {quotation.quotation_number}")
        return
    
    logger.info(f"  Found {len(items)} items")
    
    # Check if any items have default position=0
    default_positions = sum(1 for item in items if item.position == 0)
    if default_positions > 1:
        logger.info(f"  Found {default_positions} items with default position=0")
    
    # Update positions to be sequential starting from 0
    updated_count = 0
    for idx, item in enumerate(items):
        # Only update if position is incorrect to minimize changes
        if item.position != idx:
            logger.info(f"  Item ID {item.id}: Updating position from {item.position} to {idx}")
            item.position = idx
            updated_count += 1
    
    # Save changes if any updates were made
    if updated_count > 0:
        db.session.commit()
        logger.info(f"  Updated {updated_count}/{len(items)} items with sequential positions")
    else:
        logger.info("  No position updates needed - all items already have sequential positions")

def update_quotation_model():
    """
    Print instructions for updating the Quotation model to properly order items by position
    """
    print("\nModel Update Recommendation:")
    print("To ensure items are always ordered by position in the Quotation model,")
    print("consider adding the following relationship definition to your Quotation model:")
    print("\nIn models.py, update the Quotation class:")
    print("```python")
    print("class Quotation(db.Model):")
    print("    # ... existing fields")
    print("    ")
    print("    # Update the items relationship to order by position")
    print("    items = db.relationship('QuotationItem', backref='quotation',")
    print("                           order_by='QuotationItem.position',")
    print("                           cascade='all, delete-orphan')")
    print("```")
    print("\nThis ensures that when you access quotation.items, they will be")
    print("returned in position order without needing to sort them in the template.")

if __name__ == "__main__":
    # Check for quotation number argument
    quotation_number = sys.argv[1] if len(sys.argv) > 1 else None
    
    # Run the fix
    mode = f"quotation {quotation_number}" if quotation_number else "all quotations"
    print(f"\nFixing item positions for {mode}...\n")
    
    if fix_quotation_positions(quotation_number):
        print(f"\n✅ Successfully fixed positions for {mode}")
        update_quotation_model()
    else:
        print(f"\n❌ Failed to fix positions for {mode}")
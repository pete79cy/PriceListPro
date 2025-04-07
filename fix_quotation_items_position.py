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

import os
import sys
import logging
from datetime import datetime

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("quotation_fix")

# Add the current directory to the path so we can import our app
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import our application
from app import app, db
from models import Quotation, QuotationItem

def fix_quotation_positions(quotation_number=None):
    """
    Fix positions for all items in a quotation or all quotations.
    
    Args:
        quotation_number: Optional quotation number to fix a specific quotation,
                          or None to fix all quotations
    """
    with app.app_context():
        try:
            if quotation_number:
                # Fix specific quotation
                logger.info(f"Fixing positions for quotation {quotation_number}")
                quotation = Quotation.query.filter_by(quotation_number=quotation_number).first()
                if not quotation:
                    logger.error(f"Quotation with number {quotation_number} not found")
                    return False
                
                # Fix positions for this quotation only
                _fix_positions_for_quotation(quotation)
            else:
                # Fix all quotations
                logger.info("Fixing positions for ALL quotations")
                quotations = Quotation.query.all()
                logger.info(f"Found {len(quotations)} quotations to process")
                
                for quotation in quotations:
                    _fix_positions_for_quotation(quotation)
            
            # Commit all changes
            db.session.commit()
            logger.info("All position fixes committed successfully")
            return True
            
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error fixing quotation positions: {str(e)}")
            return False

def _fix_positions_for_quotation(quotation):
    """
    Fix positions for all items in a specific quotation.
    
    Args:
        quotation: The Quotation object whose items need position fixing
    """
    # Get items ordered by ID (assumes this is the intended order)
    items = QuotationItem.query.filter_by(quotation_id=quotation.id).order_by(QuotationItem.id).all()
    
    # Update positions (starting from 1 to match display numbering)
    updated_count = 0
    for idx, item in enumerate(items):
        # Only update if different to minimize changes
        if item.position != idx + 1:
            item.position = idx + 1
            updated_count += 1
    
    logger.info(f"Updated {updated_count} positions for quotation {quotation.quotation_number} (ID: {quotation.id})")
    return updated_count

def update_quotation_model():
    """
    Print instructions for updating the Quotation model to properly order items by position
    """
    logger.info("\n===== NEXT STEPS =====")
    logger.info("To ensure permanent fix, update the Quotation model in models.py:")
    logger.info("""
    class Quotation(db.Model):
        # ... existing code ...
        
        # Update this line to add order_by parameter:
        items = db.relationship('QuotationItem', backref='quotation', 
                               lazy=True, cascade="all, delete-orphan",
                               order_by="QuotationItem.position")
    """)
    
    logger.info("\nTo verify PDF template uses correct ordering, check templates/pdf/quotation_template.html:")
    logger.info("""
    <!-- If directly iterating through items, add sorting: -->
    {% for item in items|sort(attribute='position') %}
    <!-- ... rest of loop ... -->
    {% endfor %}
    """)

if __name__ == "__main__":
    # Check the command-line arguments
    quotation_number = None
    if len(sys.argv) > 1:
        quotation_number = sys.argv[1]
    
    # Run the fix
    success = fix_quotation_positions(quotation_number)
    
    if success:
        update_quotation_model()
    else:
        logger.error("Fix operation failed. See error logs above.")
        sys.exit(1)
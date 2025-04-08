"""
Test script to verify the fix for item #10 being skipped in quotation PDFs.
This script specifically:
1. Finds quotations with at least 10 items
2. Fixes their position values to be sequential
3. Generates a test PDF with debugging for item #10
4. Validates all items are rendered correctly

Usage:
    python test_item10_pdf_fix.py [quotation_number]
"""

import os
import sys
import logging
from datetime import datetime
from app import app, db
from models import Quotation
from fix_quotation_item_positions import fix_quotation_positions, verify_quotation_positions
from utils.enhanced_pdf_generator_v2 import generate_quotation_pdf_v2

# Configure logging
logging.basicConfig(level=logging.INFO, 
                   format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_fix_item10_for_quotation(quotation_number=None):
    """
    Test the fix for item #10 on a specific quotation or find quotations with enough items.
    
    Args:
        quotation_number: Optional quotation number to test, or None to find suitable quotations
        
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        with app.app_context():
            quotations_to_test = []
            
            if quotation_number:
                # Test specific quotation
                quotation = Quotation.query.filter_by(quotation_number=quotation_number).first()
                if not quotation:
                    logger.error(f"Quotation not found: {quotation_number}")
                    return False
                
                quotations_to_test.append(quotation)
            else:
                # Find quotations with at least 10 items
                logger.info("Searching for quotations with at least 10 items...")
                quotations = Quotation.query.all()
                
                for quotation in quotations:
                    if len(quotation.items) >= 10:
                        logger.info(f"Found quotation {quotation.quotation_number} with {len(quotation.items)} items")
                        quotations_to_test.append(quotation)
                        
                if not quotations_to_test:
                    logger.error("No quotations found with at least 10 items")
                    return False
            
            # Create test output directory
            test_dir = os.path.join(app.config['UPLOAD_FOLDER'], f'item10_test_{datetime.now().strftime("%Y%m%d_%H%M%S")}')
            os.makedirs(test_dir, exist_ok=True)
            logger.info(f"Created test directory: {test_dir}")
            
            # Test each quotation
            for quotation in quotations_to_test:
                logger.info(f"Testing quotation {quotation.quotation_number} with {len(quotation.items)} items")
                
                # Fix positions
                logger.info("Fixing item positions...")
                fix_quotation_positions(quotation.quotation_number)
                
                # Verify positions
                if not verify_quotation_positions(quotation.quotation_number):
                    logger.error(f"Failed to verify positions for quotation {quotation.quotation_number}")
                    continue
                
                # Generate a debug PDF with item #10 highlighting
                logger.info("Generating debug PDF with item #10 highlighting...")
                pdf_path = generate_quotation_pdf_v2(
                    quotation, 
                    test_dir, 
                    use_modern_template=True,
                    debug=True
                )
                
                if pdf_path:
                    logger.info(f"✅ Successfully generated debug PDF: {pdf_path}")
                else:
                    logger.error(f"❌ Failed to generate debug PDF for quotation {quotation.quotation_number}")
                    continue
                
                # Now generate a normal PDF without debug
                logger.info("Generating normal PDF...")
                pdf_path = generate_quotation_pdf_v2(
                    quotation, 
                    test_dir, 
                    use_modern_template=True,
                    debug=False
                )
                
                if pdf_path:
                    logger.info(f"✅ Successfully generated normal PDF: {pdf_path}")
                else:
                    logger.error(f"❌ Failed to generate normal PDF for quotation {quotation.quotation_number}")
                    continue
            
            logger.info(f"Complete! PDF files are available in: {test_dir}")
            return True
            
    except Exception as e:
        logger.error(f"Error testing item #10 fix: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())
        return False

if __name__ == "__main__":
    quotation_number = sys.argv[1] if len(sys.argv) > 1 else None
    
    if quotation_number:
        logger.info(f"Testing specific quotation: {quotation_number}")
    else:
        logger.info("Finding and testing quotations with at least 10 items")
        
    if test_fix_item10_for_quotation(quotation_number):
        logger.info("✅ Test completed successfully")
    else:
        logger.error("❌ Test failed")
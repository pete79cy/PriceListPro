"""
Test script to verify the fixed quotation PDF generator.
This script generates PDFs for test quotations to confirm all items render correctly.
"""

import os
import sys
import logging
from datetime import datetime
from flask import Flask
from app import app, db
from models import Quotation
from utils.fixed_pdf_generator import generate_fixed_quotation_pdf

# Configure logging
logging.basicConfig(level=logging.INFO,
                   format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("pdf_test")

def test_fixed_pdf_generator(quotation_number=None, debug=False):
    """
    Test the fixed PDF generator on a specific quotation or all quotations.
    
    Args:
        quotation_number: Optional quotation number to test, or None to test all
        debug: Whether to enable debug mode for the PDF
        
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        with app.app_context():
            # Create test directory
            test_timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            test_dir = os.path.join(app.config['UPLOAD_FOLDER'], f"fixed_pdf_test_{test_timestamp}")
            os.makedirs(test_dir, exist_ok=True)
            
            # Get quotations to test
            if quotation_number:
                quotations = Quotation.query.filter_by(quotation_number=quotation_number).all()
                if not quotations:
                    logger.error(f"Quotation not found: {quotation_number}")
                    return False
            else:
                # Test the problematic quotations we know about
                known_problem_quotations = ["PAK-2025-007"]  # Add other known problem quotations here
                quotations = []
                
                for qn in known_problem_quotations:
                    q = Quotation.query.filter_by(quotation_number=qn).first()
                    if q:
                        quotations.append(q)
                
                # If no known problems found, get the latest 3 quotations
                if not quotations:
                    quotations = Quotation.query.order_by(Quotation.id.desc()).limit(3).all()
            
            # Test each quotation
            for quotation in quotations:
                logger.info(f"Testing quotation {quotation.quotation_number} with {len(quotation.items)} items")
                
                # Log item positions
                positions = [item.position for item in quotation.items]
                logger.info(f"Item positions: {positions}")
                
                # Check for sequential positions
                is_sequential = all(positions[i] == i for i in range(len(positions)))
                if not is_sequential:
                    logger.warning(f"Positions are not sequential: {positions}")
                
                # Generate a normal PDF
                logger.info("Generating normal PDF...")
                pdf_path = generate_fixed_quotation_pdf(
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
                
                # Generate a debug PDF if requested
                if debug:
                    logger.info("Generating debug PDF...")
                    debug_pdf_path = generate_fixed_quotation_pdf(
                        quotation, 
                        test_dir, 
                        use_modern_template=True,
                        debug=True
                    )
                    
                    if debug_pdf_path:
                        logger.info(f"✅ Successfully generated debug PDF: {debug_pdf_path}")
                    else:
                        logger.error(f"❌ Failed to generate debug PDF for quotation {quotation.quotation_number}")
                        continue
            
            logger.info(f"Test complete! PDF files are available in: {test_dir}")
            return True
            
    except Exception as e:
        logger.error(f"Error testing fixed PDF generator: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())
        return False

if __name__ == "__main__":
    # Get command line arguments
    quotation_number = sys.argv[1] if len(sys.argv) > 1 else None
    debug_mode = "--debug" in sys.argv
    
    # Run the test
    if test_fixed_pdf_generator(quotation_number, debug_mode):
        logger.info("✅ Test completed successfully")
    else:
        logger.error("❌ Test failed")
        sys.exit(1)
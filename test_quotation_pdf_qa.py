"""
QA Test script for PDF quotation generation.
This script tests multiple quotations with various scenarios to ensure PDFs are generated correctly.
"""

import os
import sys
import logging
from datetime import datetime
from app import app, db
from models import Quotation
from utils.enhanced_pdf_generator import generate_enhanced_pdf

# Configure logging
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("quotation_pdf_qa")

def test_quotation_pdf(quotation_number, use_debug=False, use_modern=True):
    """
    Test generating a PDF for a specific quotation and validate output.
    
    Args:
        quotation_number: The quotation number to test
        use_debug: Whether to enable debug mode for the PDF
        use_modern: Whether to use the modern template
        
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        with app.app_context():
            # Find the quotation
            quotation = Quotation.query.filter_by(quotation_number=quotation_number).first()
            if not quotation:
                logger.error(f"Quotation not found: {quotation_number}")
                return False
                
            # Generate test folder name
            test_timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            test_folder = os.path.join(app.config['UPLOAD_FOLDER'], f"qa_test_{test_timestamp}")
            os.makedirs(test_folder, exist_ok=True)
            
            # Log test details
            logger.info(f"Testing quotation {quotation_number} with {len(quotation.items)} items")
            logger.info(f"Item positions: {[item.position for item in quotation.items]}")
            
            # Generate the PDF
            pdf_path = generate_enhanced_pdf(
                quotation, 
                test_folder, 
                use_modern_template=use_modern,
                debug=use_debug
            )
            
            # Verify the file exists
            if not os.path.exists(pdf_path):
                logger.error(f"Generated PDF not found: {pdf_path}")
                return False
                
            logger.info(f"QA Test PASSED for quotation {quotation_number}")
            logger.info(f"PDF saved to: {pdf_path}")
            return True
            
    except Exception as e:
        logger.error(f"Error testing quotation {quotation_number}: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())
        return False

def run_batch_tests():
    """Run QA tests on a batch of quotations"""
    # List of problematic quotations to test
    test_quotations = [
        "PAK-2025-007",  # Our primary test case with item #14 issue
        "PAK-2025-003",  # Another quotation to test
    ]
    
    results = {}
    
    # Test each quotation in both normal and debug mode
    for quotation_number in test_quotations:
        # Test with standard PDF
        normal_result = test_quotation_pdf(quotation_number, use_debug=False)
        
        # Test with debug PDF
        debug_result = test_quotation_pdf(quotation_number, use_debug=True)
        
        results[quotation_number] = {
            "normal": normal_result,
            "debug": debug_result
        }
    
    # Print summary
    logger.info("\n--- QA TEST SUMMARY ---")
    all_passed = True
    for quotation_number, result in results.items():
        normal_status = "PASSED" if result["normal"] else "FAILED"
        debug_status = "PASSED" if result["debug"] else "FAILED"
        logger.info(f"Quotation {quotation_number}: Normal PDF: {normal_status}, Debug PDF: {debug_status}")
        if not (result["normal"] and result["debug"]):
            all_passed = False
            
    if all_passed:
        logger.info("✅ All tests PASSED!")
    else:
        logger.warning("❌ Some tests FAILED!")
        
    return all_passed

if __name__ == "__main__":
    print("Running QA tests for PDF quotation generation...")
    success = run_batch_tests()
    sys.exit(0 if success else 1)
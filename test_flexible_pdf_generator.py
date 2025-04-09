"""
Dedicated test script for the flexible PDF generator.
This script tests the core functionality without routing dependencies.
"""

import os
import sys
import logging
from datetime import datetime
import uuid
from app import app, db
from models import Quotation, QuotationItem
from utils.flexible_pdf_generator import generate_flexible_quotation_pdf

# Configure logging
logging.basicConfig(level=logging.INFO,
                   format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def create_test_folder():
    """Create a test folder for output files"""
    test_dir = os.path.join('uploads', 'flexible_pdf_test')
    os.makedirs(test_dir, exist_ok=True)
    return test_dir

def get_sample_quotation():
    """Get a sample quotation for testing"""
    with app.app_context():
        # First try to find an existing quotation with items
        quotations = Quotation.query.all()
        for quotation in quotations:
            if quotation.items and len(quotation.items) > 0:
                logger.info(f"Found existing quotation: {quotation.quotation_number} with {len(quotation.items)} items")
                return quotation
        
        # If no suitable quotation exists, return None
        logger.warning("No suitable quotation found for testing")
        return None

def generate_test_pdf(quotation, selected_fields=None, output_dir=None, debug=True):
    """Generate a test PDF with the flexible generator"""
    try:
        if not output_dir:
            output_dir = create_test_folder()
        
        if not selected_fields:
            # Use minimal default fields
            selected_fields = ['position', 'description', 'quantity', 'selling_price', 'total']
        
        logger.info(f"Generating PDF with fields: {', '.join(selected_fields)}")
        
        # Generate the PDF
        output_path = generate_flexible_quotation_pdf(
            quotation=quotation,
            selected_fields=selected_fields,
            upload_folder=output_dir,
            debug=debug
        )
        
        if output_path and os.path.exists(output_path):
            logger.info(f"✅ PDF generated successfully: {output_path}")
            
            # Get file size for verification
            file_size = os.path.getsize(output_path)
            logger.info(f"PDF file size: {file_size} bytes")
            
            return output_path
        else:
            logger.error("❌ PDF generation failed or file not created")
            return None
    
    except Exception as e:
        logger.error(f"Error generating PDF: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())
        return None

def test_all_field_combinations(quotation):
    """Test all possible field combinations for robustness"""
    output_dir = create_test_folder()
    
    # Test minimal fields
    logger.info("Test 1: Minimal fields")
    minimal_fields = ['position', 'description', 'quantity', 'selling_price', 'total']
    minimal_pdf = generate_test_pdf(quotation, minimal_fields, output_dir)
    
    # Test with scientific name and pot size
    logger.info("Test 2: With scientific name and pot size")
    scientific_fields = minimal_fields + ['scientific_name', 'pot_size']
    scientific_pdf = generate_test_pdf(quotation, scientific_fields, output_dir)
    
    # Test with supplier info
    logger.info("Test 3: With supplier information")
    supplier_fields = minimal_fields + ['supplier', 'notes']
    supplier_pdf = generate_test_pdf(quotation, supplier_fields, output_dir)
    
    # Return success status
    return all([minimal_pdf, scientific_pdf, supplier_pdf])

def main():
    """Main test function"""
    try:
        # Get sample quotation
        quotation = get_sample_quotation()
        if not quotation:
            logger.error("Cannot run tests without a valid quotation")
            return 1
        
        # Run basic test
        logger.info("Running basic PDF generation test...")
        basic_test = generate_test_pdf(quotation)
        
        if not basic_test:
            logger.error("Basic test failed, cannot continue")
            return 1
        
        # Run combination tests if requested
        if len(sys.argv) > 1 and sys.argv[1] == '--all':
            logger.info("Running comprehensive field combination tests...")
            test_all_field_combinations(quotation)
        
        logger.info("✅ All tests completed successfully")
        return 0
    
    except Exception as e:
        logger.error(f"Test error: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())
        return 1

if __name__ == "__main__":
    sys.exit(main())
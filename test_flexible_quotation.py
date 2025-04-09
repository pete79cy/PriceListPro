"""
Test script for the flexible quotation PDF generator.
This script demonstrates how to use the flexible PDF generator with different field configurations.
"""

import os
import sys
import logging
from datetime import datetime
from flask import Flask
from app import app, db
from models import Quotation
from utils.flexible_pdf_generator import (
    generate_flexible_quotation_pdf,
    DEFAULT_ITEM_FIELDS,
    AVAILABLE_ITEM_FIELDS
)

# Configure logging
logging.basicConfig(level=logging.INFO,
                   format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("pdf_test")

def list_available_fields():
    """List all available fields for user reference"""
    logger.info("Default fields:")
    for field in DEFAULT_ITEM_FIELDS:
        logger.info(f"  - {field['name']}: {field['label']}")
    
    logger.info("\nAdditional fields:")
    for field in AVAILABLE_ITEM_FIELDS:
        admin_note = " (Admin only)" if field.get('admin_only') else ""
        logger.info(f"  - {field['name']}: {field['label']}{admin_note}")

def test_flexible_pdf_generator(quotation_number=None, selected_fields=None, orientation=None):
    """
    Test the flexible PDF generator with different field configurations.
    
    Args:
        quotation_number: Optional quotation number to test, or None to use most recent
        selected_fields: List of field names to include, or None for defaults
        orientation: Page orientation ('portrait' or 'landscape'), or None for default
        
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        with app.app_context():
            # Create test directory
            test_timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            test_dir = os.path.join(app.config['UPLOAD_FOLDER'], f"flex_pdf_test_{test_timestamp}")
            os.makedirs(test_dir, exist_ok=True)
            
            # Get quotation to test
            if quotation_number:
                quotation = Quotation.query.filter_by(quotation_number=quotation_number).first()
                if not quotation:
                    logger.error(f"Quotation not found: {quotation_number}")
                    return False
            else:
                # Get the most recent quotation
                quotation = Quotation.query.order_by(Quotation.id.desc()).first()
                if not quotation:
                    logger.error("No quotations found in the database")
                    return False
                    
            logger.info(f"Using quotation: {quotation.quotation_number} with {len(quotation.items)} items")
            
            # If no fields specified, test multiple configurations
            if not selected_fields:
                # Test 1: Default fields
                logger.info("Test 1: Generating PDF with default fields")
                pdf_path_1 = generate_flexible_quotation_pdf(
                    quotation, 
                    selected_fields=None,
                    upload_folder=test_dir,
                    orientation=orientation or 'portrait',
                    debug=False
                )
                
                if pdf_path_1:
                    logger.info(f"✅ Successfully generated default PDF: {pdf_path_1}")
                else:
                    logger.error("❌ Failed to generate default PDF")
                
                # Test 2: Minimal fields
                logger.info("Test 2: Generating PDF with minimal fields")
                pdf_path_2 = generate_flexible_quotation_pdf(
                    quotation, 
                    selected_fields=['position', 'description', 'quantity', 'selling_price', 'total'],
                    upload_folder=test_dir,
                    orientation=orientation or 'portrait',
                    debug=False
                )
                
                if pdf_path_2:
                    logger.info(f"✅ Successfully generated minimal PDF: {pdf_path_2}")
                else:
                    logger.error("❌ Failed to generate minimal PDF")
                
                # Test 3: All available fields
                logger.info("Test 3: Generating PDF with all available fields")
                all_fields = [f['name'] for f in DEFAULT_ITEM_FIELDS + AVAILABLE_ITEM_FIELDS]
                pdf_path_3 = generate_flexible_quotation_pdf(
                    quotation, 
                    selected_fields=all_fields,
                    upload_folder=test_dir,
                    orientation=orientation or 'landscape',  # Use landscape for all fields
                    include_admin_fields=True,
                    debug=False
                )
                
                if pdf_path_3:
                    logger.info(f"✅ Successfully generated comprehensive PDF: {pdf_path_3}")
                else:
                    logger.error("❌ Failed to generate comprehensive PDF")
                    
                logger.info(f"All test files are available in: {test_dir}")
                return pdf_path_1 and pdf_path_2 and pdf_path_3
            else:
                # Generate PDF with specified fields
                logger.info(f"Generating PDF with specified fields: {selected_fields}")
                pdf_path = generate_flexible_quotation_pdf(
                    quotation, 
                    selected_fields=selected_fields,
                    upload_folder=test_dir,
                    orientation=orientation or 'portrait',
                    include_admin_fields=True,
                    debug=False
                )
                
                if pdf_path:
                    logger.info(f"✅ Successfully generated PDF: {pdf_path}")
                    return True
                else:
                    logger.error("❌ Failed to generate PDF")
                    return False
            
    except Exception as e:
        logger.error(f"Error testing flexible PDF generator: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())
        return False

if __name__ == "__main__":
    # Handle command line arguments
    if len(sys.argv) > 1 and sys.argv[1] == "--list-fields":
        # Just list available fields
        list_available_fields()
        sys.exit(0)
        
    quotation_number = None
    selected_fields = None
    orientation = None
    
    # Parse command line arguments
    for arg in sys.argv[1:]:
        if arg.startswith("--quotation="):
            quotation_number = arg.split("=")[1]
        elif arg.startswith("--fields="):
            selected_fields = arg.split("=")[1].split(",")
        elif arg.startswith("--orientation="):
            orientation = arg.split("=")[1]
            
    # Run the test
    if test_flexible_pdf_generator(quotation_number, selected_fields, orientation):
        logger.info("✅ Test completed successfully")
    else:
        logger.error("❌ Test failed")
        sys.exit(1)
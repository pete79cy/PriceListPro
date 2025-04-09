"""
Minimal test script for the flexible quotation PDF generator.
This script tests the basic functionality of generating a flexible PDF for a quotation.
"""

import os
import logging
from datetime import datetime
from flask import Flask
from app import app, db
from models import Quotation
from utils.flexible_pdf_generator import generate_flexible_quotation_pdf

# Configure logging
logging.basicConfig(level=logging.INFO, 
                   format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("test_pdf")

def test_minimal_pdf():
    """
    Generate a minimal PDF with only essential fields
    """
    try:
        with app.app_context():
            # Get the most recent quotation
            quotation = Quotation.query.order_by(Quotation.id.desc()).first()
            if not quotation:
                logger.error("No quotations found in the database")
                return False
                
            logger.info(f"Using quotation: {quotation.quotation_number} with {len(quotation.items)} items")
            
            # Create test directory
            test_dir = os.path.join(app.config.get('UPLOAD_FOLDER', './uploads'), "flex_test")
            os.makedirs(test_dir, exist_ok=True)
            
            # Define minimal fields
            minimal_fields = ['position', 'description', 'quantity', 'selling_price', 'total']
            
            # Generate PDF
            output_path = generate_flexible_quotation_pdf(
                quotation=quotation,
                selected_fields=minimal_fields,
                upload_folder=test_dir,
                debug=True
            )
            
            if output_path:
                logger.info(f"✅ Successfully generated PDF: {output_path}")
                return True
            else:
                logger.error("❌ Failed to generate PDF")
                return False
                
    except Exception as e:
        logger.error(f"Error testing PDF generator: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())
        return False

if __name__ == "__main__":
    if test_minimal_pdf():
        print("Test completed successfully!")
    else:
        print("Test failed.")
        exit(1)
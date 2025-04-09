"""
Manual test script for the flexible quotation PDF generator.
This script allows specifying a quotation ID and fields to test.
"""

import os
import sys
import logging
from datetime import datetime
from app import app, db
from models import Quotation
from utils.flexible_pdf_generator import generate_flexible_quotation_pdf

# Configure logging
logging.basicConfig(level=logging.INFO,
                   format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger("pdf_test")

def main():
    """
    Test generating a flexible PDF for a specific quotation.
    
    Usage:
      python manual_flexible_pdf_test.py <quotation_id>
    """
    try:
        # Get quotation ID from command line
        if len(sys.argv) < 2:
            quotation_id = 1  # Default to ID 1
            logger.info(f"No quotation ID provided, using default: {quotation_id}")
        else:
            try:
                quotation_id = int(sys.argv[1])
            except ValueError:
                logger.error(f"Invalid quotation ID: {sys.argv[1]}")
                return 1
        
        with app.app_context():
            # Get the quotation
            quotation = Quotation.query.get(quotation_id)
            if not quotation:
                logger.error(f"Quotation not found with ID: {quotation_id}")
                return 1
                
            logger.info(f"Using quotation: {quotation.quotation_number} with {len(quotation.items)} items")
            
            # Create test directory
            test_dir = os.path.join('uploads', 'manual_test')
            os.makedirs(test_dir, exist_ok=True)
            
            # Define fields
            fields = ['position', 'description', 'quantity', 'selling_price', 'total']
            
            # Generate PDF
            logger.info("Generating PDF with flexible generator...")
            output_path = generate_flexible_quotation_pdf(
                quotation=quotation,
                selected_fields=fields,
                upload_folder=test_dir,
                debug=True
            )
            
            if output_path:
                logger.info(f"✅ Successfully generated PDF: {output_path}")
                logger.info(f"View the PDF at: {output_path}")
                return 0
            else:
                logger.error("❌ Failed to generate PDF")
                return 1
                
    except Exception as e:
        logger.error(f"Error: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())
        return 1

if __name__ == "__main__":
    sys.exit(main())
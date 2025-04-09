"""
Standalone test script for generating a flexible PDF without routes integration.
This script tests the core flexible PDF generator functionality.
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
                   format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger("pdf_test")

def main():
    """Generate a test PDF using the flexible PDF generator"""
    try:
        with app.app_context():
            # Get all quotations
            quotations = Quotation.query.all()
            if not quotations:
                logger.error("No quotations found in the database")
                return 1
                
            # Use the first quotation with items
            test_quotation = None
            for quotation in quotations:
                if quotation.items and len(quotation.items) > 0:
                    test_quotation = quotation
                    break
                    
            if not test_quotation:
                logger.error("No quotations found with items")
                return 1
                
            logger.info(f"Using quotation: {test_quotation.quotation_number} with {len(test_quotation.items)} items")
            
            # Create test directory
            test_dir = os.path.join('uploads', 'test_pdf')
            os.makedirs(test_dir, exist_ok=True)
            
            # Generate PDF with minimal fields
            fields = ['position', 'description', 'quantity', 'selling_price', 'total']
            logger.info(f"Generating PDF with fields: {fields}")
            
            output_path = generate_flexible_quotation_pdf(
                quotation=test_quotation,
                selected_fields=fields,
                upload_folder=test_dir,
                debug=True
            )
            
            if output_path:
                logger.info(f"✅ Successfully generated PDF: {output_path}")
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
    exit(main())
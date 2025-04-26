"""
Test script for template-based Excel export functionality.
This script tests the template-based export of quotations to Excel files.
"""

import os
import logging
import shutil
from datetime import datetime
from app import app, db
from models import Quotation
from utils.template_excel_generator import generate_template_excel
from utils.bulk_excel_export import generate_bulk_quotation_excel

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_single_quotation_export():
    """Test exporting a single quotation using the template format"""
    with app.app_context():
        # Get a test quotation from the database
        quotation = Quotation.query.order_by(Quotation.id.desc()).first()
        
        if not quotation:
            logger.error("No quotations found in the database. Test cannot proceed.")
            return False
        
        logger.info(f"Testing export for quotation #{quotation.quotation_number}")
        
        # Create a test output folder
        output_folder = 'test_exports'
        os.makedirs(output_folder, exist_ok=True)
        
        # Get template path from attached_assets
        template_path = os.path.join('attached_assets', 'quotation_template(13).xlsx')
        if not os.path.exists(template_path):
            logger.warning("Template file not found, will generate based on structure")
            template_path = None
        
        # Generate Excel file using the template format
        excel_path = generate_template_excel(
            quotation=quotation,
            output_folder=output_folder,
            template_path=template_path
        )
        
        if excel_path and os.path.exists(excel_path):
            logger.info(f"✅ Successfully generated Excel file at: {excel_path}")
            return True
        else:
            logger.error("❌ Failed to generate Excel file")
            return False

def test_bulk_quotation_export():
    """Test exporting multiple quotations using the template format"""
    with app.app_context():
        # Get a few test quotations from the database
        quotations = Quotation.query.order_by(Quotation.id.desc()).limit(3).all()
        
        if not quotations:
            logger.error("No quotations found in the database. Test cannot proceed.")
            return False
        
        logger.info(f"Testing bulk export for {len(quotations)} quotations")
        
        # Create a test output folder
        output_folder = 'test_exports'
        os.makedirs(output_folder, exist_ok=True)
        
        # Get template path from attached_assets
        template_path = os.path.join('attached_assets', 'quotation_template(13).xlsx')
        if not os.path.exists(template_path):
            logger.warning("Template file not found, will generate based on structure")
            template_path = None
        
        # Generate zip file containing Excel files for all quotations
        zip_path = generate_bulk_quotation_excel(
            quotations=quotations,
            output_folder=output_folder,
            use_template=True,
            template_path=template_path
        )
        
        if zip_path and os.path.exists(zip_path):
            logger.info(f"✅ Successfully generated ZIP file at: {zip_path}")
            return True
        else:
            logger.error("❌ Failed to generate ZIP file")
            return False

if __name__ == '__main__':
    logger.info("===== Testing Template-Based Excel Export =====")
    
    # Test single quotation export
    single_result = test_single_quotation_export()
    logger.info(f"Single quotation export test: {'PASSED' if single_result else 'FAILED'}")
    
    # Test bulk quotation export
    bulk_result = test_bulk_quotation_export()
    logger.info(f"Bulk quotation export test: {'PASSED' if bulk_result else 'FAILED'}")
    
    # Overall result
    if single_result and bulk_result:
        logger.info("✅ All tests PASSED")
    else:
        logger.error("❌ Some tests FAILED")
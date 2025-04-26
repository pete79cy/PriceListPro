"""
Test script for template-based Excel export functionality.
This script tests the direct function calls for template-based exports.
"""

import os
import logging
import shutil
import zipfile
from datetime import datetime
from app import app, db
from models import Quotation
from utils.template_excel_generator import generate_template_excel
from utils.bulk_excel_export import generate_bulk_quotation_excel

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_functions():
    """Test the template-based export functions directly"""
    with app.app_context():
        try:
            # Get all quotations from the database
            quotations = Quotation.query.all()
            if not quotations:
                logger.error("No quotations found in the database. Test cannot proceed.")
                return False
                
            logger.info(f"Found {len(quotations)} quotations in the database")
            
            # Create test directories
            uploads_dir = os.path.join(os.getcwd(), 'uploads')
            test_dir = os.path.join(os.getcwd(), 'test_exports')
            os.makedirs(uploads_dir, exist_ok=True)
            os.makedirs(test_dir, exist_ok=True)
            
            # Copy template if available
            template_path = os.path.join('attached_assets', 'quotation_template(13).xlsx')
            if not os.path.exists(template_path):
                logger.warning("Template file not found, will generate based on structure")
                template_path = None
            else:
                logger.info(f"Using template from {template_path}")
            
            # Generate bulk export zip
            zip_path = generate_bulk_quotation_excel(
                quotations=quotations,
                output_folder=test_dir,
                use_template=True,
                template_path=template_path
            )
            
            if not zip_path or not os.path.exists(zip_path):
                logger.error("Failed to generate bulk export zip file")
                return False
                
            logger.info(f"Successfully generated zip file at {zip_path}")
            
            # Extract and validate zip contents
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                file_list = zip_ref.namelist()
                logger.info(f"Zip file contains {len(file_list)} files:")
                for file in file_list:
                    logger.info(f"  - {file}")
                
                # Extract to verify files
                extract_dir = os.path.join(test_dir, 'extracted')
                os.makedirs(extract_dir, exist_ok=True)
                zip_ref.extractall(extract_dir)
                
                # Verify extracted files
                extracted_files = os.listdir(extract_dir)
                logger.info(f"Successfully extracted {len(extracted_files)} files")
                
                # Check a sample file
                if len(extracted_files) > 0:
                    sample_file = os.path.join(extract_dir, extracted_files[0])
                    file_size = os.path.getsize(sample_file)
                    logger.info(f"Sample file {sample_file} (size: {file_size} bytes)")
                    
            return True
            
        except Exception as e:
            logger.error(f"Error during testing: {str(e)}")
            import traceback
            logger.error(traceback.format_exc())
            return False

if __name__ == '__main__':
    logger.info("===== Testing Template Functions =====")
    
    result = test_functions()
    
    if result:
        logger.info("✅ All tests PASSED")
    else:
        logger.error("❌ Test FAILED")
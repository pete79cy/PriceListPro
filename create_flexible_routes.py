"""
Create a new routes.py with flexible quotation routes added correctly.
This script will:
1. Backup the original routes.py
2. Create a new routes.py with minimal changes
3. Add a simple test for the PDF generation
"""

import os
import sys
import shutil
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, 
                   format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger("create_routes")

def backup_original_files():
    """Backup original routes.py"""
    try:
        if os.path.exists('routes.py'):
            shutil.copy2('routes.py', 'routes.py.original')
            logger.info("Created backup: routes.py.original")
        return True
    except Exception as e:
        logger.error(f"Failed to backup files: {str(e)}")
        return False

def remove_flexible_import_from_routes():
    """Remove flexible import from routes.py"""
    try:
        with open('routes.py', 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Remove the import line
        import_line = "from utils.flexible_pdf_generator import generate_flexible_quotation_pdf, DEFAULT_ITEM_FIELDS, AVAILABLE_ITEM_FIELDS"
        if import_line in content:
            content = content.replace(import_line, "# Import flexible PDF generator removed")
            
            with open('routes.py', 'w', encoding='utf-8') as f:
                f.write(content)
            
            logger.info("Removed flexible import from routes.py")
        return True
    except Exception as e:
        logger.error(f"Failed to remove import: {str(e)}")
        return False

def create_test_script():
    """Create a simple test script for PDF generation"""
    content = """
import os
import sys
from flask import Flask
from app import app, db
from models import Quotation

def main():
    with app.app_context():
        # Get a quotation to test
        quotation_id = 1
        quotation = Quotation.query.get(quotation_id)
        
        if not quotation:
            print(f"No quotation found with ID: {quotation_id}")
            return
        
        print(f"Using quotation: {quotation.quotation_number}")
        print(f"Number of items: {len(quotation.items)}")
        
        # Import the flexible PDF generator
        from utils.flexible_pdf_generator import generate_flexible_quotation_pdf
        
        # Generate a test PDF
        output_dir = os.path.join('uploads', 'test_pdf')
        os.makedirs(output_dir, exist_ok=True)
        
        output_path = generate_flexible_quotation_pdf(
            quotation=quotation,
            selected_fields=['position', 'description', 'quantity', 'selling_price', 'total'],
            upload_folder=output_dir,
            debug=True
        )
        
        if output_path:
            print(f"✅ PDF generated successfully: {output_path}")
        else:
            print("❌ Failed to generate PDF")

if __name__ == "__main__":
    main()
"""
    
    try:
        with open('test_flexible_pdf.py', 'w', encoding='utf-8') as f:
            f.write(content)
        logger.info("Created test script: test_flexible_pdf.py")
        return True
    except Exception as e:
        logger.error(f"Failed to create test script: {str(e)}")
        return False

def restore_original_files():
    """Restore the original files"""
    try:
        if os.path.exists('routes.py.original'):
            shutil.copy2('routes.py.original', 'routes.py')
            logger.info("Restored original routes.py")
        return True
    except Exception as e:
        logger.error(f"Failed to restore files: {str(e)}")
        return False

if __name__ == "__main__":
    if not backup_original_files():
        logger.error("❌ Failed to backup files")
        sys.exit(1)
        
    if not remove_flexible_import_from_routes():
        logger.error("❌ Failed to cleanup routes.py")
        restore_original_files()
        sys.exit(1)
        
    if not create_test_script():
        logger.error("❌ Failed to create test script")
        restore_original_files()
        sys.exit(1)
        
    logger.info("✅ All tasks completed successfully")
    logger.info("You can now run the test script: python test_flexible_pdf.py")
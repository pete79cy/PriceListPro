"""
Script to generate a debug PDF for a specific quotation using the debug PDF generator.
This helps diagnose PDF generation issues like missing items.
"""

import os
import sys
import logging
from app import app, db
from models import Quotation
from utils.debug_pdf_generator import debug_quotation_pdf

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("pdf_debug_runner")

def generate_debug_pdf(quotation_number):
    """
    Generate a debug PDF for a specific quotation
    """
    with app.app_context():
        # Find the quotation
        quotation = Quotation.query.filter_by(quotation_number=quotation_number).first()
        
        if not quotation:
            logger.error(f"Quotation {quotation_number} not found")
            return False
        
        logger.info(f"Generating debug PDF for quotation {quotation_number}")
        
        try:
            # Use upload folder from app config or default
            upload_folder = app.config.get('UPLOAD_FOLDER', 'uploads')
            
            # Make sure the upload folder exists
            if not os.path.exists(upload_folder):
                os.makedirs(upload_folder)
            
            # Generate the PDF with both templates for comparison
            modern_pdf_path = debug_quotation_pdf(quotation, upload_folder, use_modern_template=True)
            standard_pdf_path = debug_quotation_pdf(quotation, upload_folder, use_modern_template=False)
            
            logger.info(f"Debug PDFs generated:")
            logger.info(f"Modern template: {modern_pdf_path}")
            logger.info(f"Standard template: {standard_pdf_path}")
            
            # Also save the item data to CSV for further analysis
            csv_path = os.path.join(upload_folder, f"quotation_items_{quotation_number}.csv")
            with open(csv_path, 'w') as f:
                f.write("Index,ID,Position,Description,Scientific Name,Pot Size,Height,Quantity,Selling Price\n")
                for idx, item in enumerate(quotation.items, 1):
                    description = item.description.replace('"', '""') if item.description else ""
                    scientific_name = item.scientific_name.replace('"', '""') if item.scientific_name else ""
                    f.write(f'{idx},{item.id},{item.position},"{description}","{scientific_name}",' + 
                           f'"{item.pot_size or ""}","{item.height or ""}",' +
                           f'{item.quantity},{item.selling_price}\n')
            
            logger.info(f"Item data saved to CSV: {csv_path}")
            return True
            
        except Exception as e:
            logger.error(f"Error generating debug PDF: {str(e)}")
            import traceback
            logger.error(traceback.format_exc())
            return False

if __name__ == "__main__":
    if len(sys.argv) > 1:
        quotation_number = sys.argv[1]
    else:
        quotation_number = input("Enter the quotation number to debug: ")
    
    success = generate_debug_pdf(quotation_number)
    
    if success:
        logger.info("Debug PDF generation completed successfully")
    else:
        logger.error("Debug PDF generation failed")
        sys.exit(1)
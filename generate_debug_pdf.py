"""
Script to generate a debug PDF for a specific quotation using the debug PDF generator.
This helps diagnose PDF generation issues like missing items.
"""

import os
import sys
import logging
from app import app
from models import Quotation
from utils.enhanced_pdf_generator import generate_enhanced_pdf

# Configure logging
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("debug_pdf")

def generate_debug_pdf(quotation_number):
    """
    Generate a debug PDF for a specific quotation
    """
    try:
        with app.app_context():
            # Find the quotation
            quotation = Quotation.query.filter_by(quotation_number=quotation_number).first()
            
            if not quotation:
                logger.error(f"No quotation found with number {quotation_number}")
                return None
            
            logger.info(f"Generating debug PDF for quotation {quotation_number} (ID: {quotation.id})")
            
            # Set up upload folder
            upload_folder = app.config.get('UPLOAD_FOLDER', 'uploads')
            if not os.path.exists(upload_folder):
                os.makedirs(upload_folder)
            
            # Generate debug PDF
            pdf_path = generate_enhanced_pdf(
                quotation, 
                upload_folder,
                use_modern_template=True,
                debug=True
            )
            
            logger.info(f"Debug PDF generated successfully: {pdf_path}")
            return pdf_path
            
    except Exception as e:
        logger.error(f"Error generating debug PDF: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())
        return None

if __name__ == "__main__":
    # Check arguments
    if len(sys.argv) != 2:
        print("Usage: python generate_debug_pdf.py <quotation_number>")
        sys.exit(1)
    
    quotation_number = sys.argv[1]
    
    # Generate debug PDF
    pdf_path = generate_debug_pdf(quotation_number)
    
    if pdf_path:
        print(f"\n✅ Debug PDF generated successfully: {pdf_path}")
        print("\nThis debug PDF includes:")
        print("- Highlighted table rows with borders for easier identification")
        print("- Special highlighting for items #13, #14, and #15")
        print("- Fixed CSS to prevent page breaks within rows")
        print("- Explicit styling to ensure all items are visible")
        print("\nUse this PDF to identify which items are missing or have rendering issues.")
    else:
        print(f"\n❌ Failed to generate debug PDF for quotation {quotation_number}")
        print("Check the log for detailed error information.")
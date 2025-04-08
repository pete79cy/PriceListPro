"""
Script to fix the missing item #14 issue in PDF quotations.

This script:
1. Checks the positions of items to ensure they're sequential
2. Generates an enhanced PDF with special CSS handling for all rows
3. Creates a debug version with highlighted rows to identify issues

Usage:
    python fix_missing_item14.py <quotation_number> [--debug]
"""

import os
import sys
import argparse
import logging
from app import app, db
from models import Quotation, QuotationItem
from utils.enhanced_pdf_generator import generate_enhanced_pdf

# Setup logging
logging.basicConfig(level=logging.INFO, 
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("missing_item_fix")

def fix_item_positions(quotation):
    """
    Fix positions for all items in a quotation to ensure they're sequential.
    This helps with consistent rendering in the PDF.
    
    Args:
        quotation: The Quotation object to fix
        
    Returns:
        bool: True if changes were made, False otherwise
    """
    # Get items ordered by ID (assumes this is the intended order)
    items = QuotationItem.query.filter_by(quotation_id=quotation.id).order_by(QuotationItem.id).all()
    
    # Update positions (starting from 0 to match potential index logic)
    updated_count = 0
    for idx, item in enumerate(items):
        # Only update if position is incorrect to minimize changes
        if item.position != idx:
            logger.info(f"Item ID {item.id}: Updating position from {item.position} to {idx}")
            item.position = idx
            updated_count += 1
    
    if updated_count > 0:
        db.session.commit()
        logger.info(f"Updated {updated_count} positions to be sequential")
        return True
    else:
        logger.info("All positions are already sequential - no updates needed")
        return False

def generate_fixed_pdf(quotation_number, debug=False):
    """
    Generate a fixed PDF that properly shows all items, including item #14.
    
    Args:
        quotation_number: The quotation number to process
        debug: Whether to enable debugging features
        
    Returns:
        str: Path to the generated PDF file, or None if failed
    """
    try:
        with app.app_context():
            # Find the quotation
            quotation = Quotation.query.filter_by(quotation_number=quotation_number).first()
            
            if not quotation:
                logger.error(f"Quotation {quotation_number} not found")
                return None
            
            logger.info(f"Processing quotation {quotation_number} (ID: {quotation.id})")
            
            # Fix positions if needed
            fix_item_positions(quotation)
            
            # Verify the item count
            item_count = len(quotation.items) if quotation.items else 0
            logger.info(f"Quotation has {item_count} items total")
            
            # Set up upload folder
            upload_folder = app.config.get('UPLOAD_FOLDER', 'uploads')
            if not os.path.exists(upload_folder):
                os.makedirs(upload_folder)
            
            # Generate the enhanced PDF with fixes for missing rows
            pdf_path = generate_enhanced_pdf(
                quotation, 
                upload_folder,
                use_modern_template=True,
                debug=debug
            )
            
            logger.info(f"Fixed PDF generated successfully: {pdf_path}")
            return pdf_path
            
    except Exception as e:
        logger.error(f"Error fixing PDF: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())
        return None

if __name__ == "__main__":
    # Set up argument parsing
    parser = argparse.ArgumentParser(description='Fix missing item #14 in quotation PDFs')
    parser.add_argument('quotation_number', help='The quotation number to process')
    parser.add_argument('--debug', action='store_true', help='Enable debugging mode with highlighted rows')
    
    # Parse arguments
    args = parser.parse_args()
    
    # Generate the fixed PDF
    pdf_path = generate_fixed_pdf(args.quotation_number, args.debug)
    
    if pdf_path:
        print(f"\nSuccess! Fixed PDF saved to: {pdf_path}")
        print("\nRecommendations:")
        print("1. If the fixed PDF shows all items correctly, update your template with these CSS fixes:")
        print("   - Add 'page-break-inside: avoid !important' to table rows")
        print("   - Change table 'overflow: hidden' to 'overflow: visible'")
        print("   - Add 'word-break: break-word' to table cells")
        print("2. To debug future PDF issues, use the '--debug' flag for visible row borders")
    else:
        print("\nFailed to generate a fixed PDF. Check the log for details.")
        print("Try running with '--debug' for more diagnostic information.")
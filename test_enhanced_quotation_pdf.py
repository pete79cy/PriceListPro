"""
Test script for the enhanced WeasyPrint PDF generator.

This script tests the new enhanced WeasyPrint PDF generator with a specific quotation
to ensure it properly renders all items without any missing rows.

Usage:
    python test_enhanced_quotation_pdf.py [quotation_number] [--debug] [--no-paginate]
"""

import os
import sys
import argparse
import logging
from datetime import datetime
from flask import Flask
from app import db, app
from models import Quotation
from utils.enhanced_weasprint_pdf_generator import (
    generate_enhanced_quotation_pdf,
    fix_item_positions
)

# Configure logging
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_enhanced_pdf_generator(quotation_number=None, debug=False, paginate=True):
    """
    Test the enhanced PDF generator on a specific quotation or all quotations.
    
    Args:
        quotation_number: Optional quotation number to test, or None to test all
        debug: Whether to enable debug mode with visual indicators
        paginate: Whether to use pagination technique
        
    Returns:
        dict: Results of the test
    """
    with app.app_context():
        # Get the quotation(s) to test
        if quotation_number:
            quotations = Quotation.query.filter_by(quotation_number=quotation_number).all()
            if not quotations:
                logger.error(f"No quotation found with number {quotation_number}")
                return {"success": False, "error": f"No quotation found with number {quotation_number}"}
        else:
            # Get problematic quotations first
            test_quotations = ["PAK-2025-007", "PAK-2025-010", "PAK-2025-012"]
            quotations = []
            
            # Find the known problematic quotations
            for test_num in test_quotations:
                q = Quotation.query.filter_by(quotation_number=test_num).first()
                if q:
                    quotations.append(q)
            
            # If none were found, get the 3 most recent quotations
            if not quotations:
                quotations = Quotation.query.order_by(Quotation.created_at.desc()).limit(3).all()
            
            if not quotations:
                logger.error("No quotations found in the database")
                return {"success": False, "error": "No quotations found in the database"}

        results = []
        
        # Create output directory
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        output_dir = os.path.join(os.getcwd(), 'static', 'test_output', f'test_{timestamp}')
        os.makedirs(output_dir, exist_ok=True)
        
        # Test each quotation
        for quotation in quotations:
            logger.info(f"Testing quotation {quotation.quotation_number} with {len(quotation.items)} items")
            
            # Fix item positions if needed
            positions_fixed = fix_item_positions(quotation)
            if positions_fixed:
                logger.info(f"Fixed positions for quotation {quotation.quotation_number}")
                db.session.commit()
            
            # Log all items for verification
            for i, item in enumerate(sorted(quotation.items, key=lambda x: x.position if hasattr(x, 'position') and x.position is not None else 0)):
                logger.info(f"Item #{i+1}: Position={getattr(item, 'position', 'unknown')}, "
                           f"Description={getattr(item, 'description', 'unknown')[:30]}")
            
            try:
                # Generate PDF with enhanced generator
                pagination_text = "with pagination" if paginate else "without pagination"
                logger.info(f"Generating enhanced PDF {pagination_text} for {quotation.quotation_number}")
                
                pdf_path = generate_enhanced_quotation_pdf(
                    quotation=quotation,
                    upload_folder=output_dir,
                    use_modern_template=True,
                    debug=debug,
                    paginate=paginate
                )
                
                if pdf_path:
                    logger.info(f"✅ Successfully generated enhanced PDF: {os.path.basename(pdf_path)}")
                    results.append({
                        "quotation_number": quotation.quotation_number,
                        "items_count": len(quotation.items),
                        "pdf_path": pdf_path,
                        "success": True
                    })
                else:
                    logger.error(f"❌ Failed to generate enhanced PDF for {quotation.quotation_number}")
                    results.append({
                        "quotation_number": quotation.quotation_number,
                        "items_count": len(quotation.items),
                        "success": False,
                        "error": "PDF generation failed"
                    })
                    
            except Exception as e:
                import traceback
                logger.error(f"❌ Error generating enhanced PDF for {quotation.quotation_number}: {str(e)}")
                logger.error(traceback.format_exc())
                results.append({
                    "quotation_number": quotation.quotation_number,
                    "items_count": len(quotation.items),
                    "success": False,
                    "error": str(e)
                })
        
        # Summarize results
        successful = [r for r in results if r["success"]]
        failed = [r for r in results if not r["success"]]
        
        logger.info(f"Test Results Summary:")
        logger.info(f"- Total quotations tested: {len(results)}")
        logger.info(f"- Successful: {len(successful)}")
        logger.info(f"- Failed: {len(failed)}")
        logger.info(f"- Output directory: {output_dir}")
        
        for result in successful:
            logger.info(f"✅ {result['quotation_number']} ({result['items_count']} items): {os.path.basename(result['pdf_path'])}")
        
        for result in failed:
            logger.info(f"❌ {result['quotation_number']} ({result['items_count']} items): {result['error']}")
        
        return {
            "success": len(failed) == 0,
            "total": len(results),
            "successful": len(successful),
            "failed": len(failed),
            "output_dir": output_dir,
            "results": results
        }

def main():
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='Test the enhanced WeasyPrint PDF generator')
    parser.add_argument('quotation_number', nargs='?', default=None,
                        help='Quotation number to test (optional)')
    parser.add_argument('--debug', action='store_true',
                        help='Enable debug mode with visual indicators')
    parser.add_argument('--no-paginate', action='store_true',
                        help='Disable pagination technique')
    
    args = parser.parse_args()
    
    # Run the test
    results = test_enhanced_pdf_generator(
        quotation_number=args.quotation_number,
        debug=args.debug,
        paginate=not args.no_paginate
    )
    
    # Exit with appropriate status code
    sys.exit(0 if results["success"] else 1)

if __name__ == '__main__':
    main()
"""
Diagnostic script to investigate quotation items ordering issue.
This script will:
1. Find the quotation with ID PAK-2025-007 mentioned in the investigation plan
2. Check all items for this quotation, their positions, and ordering
3. Verify if any items are missing or have position issues
"""

import sys
import argparse
import logging
from app import app, db
from models import Quotation, QuotationItem

# Setup logging
logging.basicConfig(level=logging.INFO, 
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("diagnostics")

def inspect_quotation_by_number(quotation_number):
    """
    Examine a specific quotation and its items by quotation number
    """
    with app.app_context():
        # Find the quotation
        quotation = Quotation.query.filter_by(quotation_number=quotation_number).first()
        if not quotation:
            logger.error(f"No quotation found with number {quotation_number}")
            return False
        
        logger.info(f"QUOTATION: {quotation.quotation_number} (ID: {quotation.id})")
        logger.info(f"Date: {quotation.date}")
        logger.info(f"Customer: {quotation.customer.name if quotation.customer else 'N/A'}")
        
        # Get items by ID order (presumably the order they were added)
        items_by_id = QuotationItem.query.filter_by(quotation_id=quotation.id).order_by(QuotationItem.id).all()
        
        # Get items by position order (how they should appear in the PDF)
        items_by_position = QuotationItem.query.filter_by(quotation_id=quotation.id).order_by(QuotationItem.position).all()
        
        # Display item counts
        logger.info(f"Total items: {len(items_by_id)}")
        logger.info(f"Items by ID count: {len(items_by_id)}")
        logger.info(f"Items by position count: {len(items_by_position)}")
        
        # Check for any position issues
        position_counts = {}
        for item in items_by_position:
            pos = item.position
            if pos in position_counts:
                position_counts[pos] += 1
            else:
                position_counts[pos] = 1
        
        # Log duplicate positions
        duplicate_positions = [pos for pos, count in position_counts.items() if count > 1]
        if duplicate_positions:
            logger.warning(f"Found duplicate positions: {duplicate_positions}")
        
        # Display items detail table
        logger.info("\nITEM DETAILS:")
        logger.info(f"{'ID':<6} {'Pos':<6} {'Description':<50} {'Qty':<5} {'Price':<10}")
        logger.info("-" * 80)
        
        # Track positions to identify gaps
        all_positions = set()
        
        for item in items_by_id:
            logger.info(f"{item.id:<6} {item.position:<6} {item.description[:47] + '...' if len(item.description) > 50 else item.description:<50} {item.quantity:<5} {item.selling_price:<10}")
            all_positions.add(item.position)
        
        # Check for gaps in positions
        if all_positions:
            expected_positions = set(range(min(all_positions), max(all_positions) + 1))
            missing_positions = expected_positions - all_positions
            if missing_positions:
                logger.warning(f"Missing positions in sequence: {sorted(missing_positions)}")
            else:
                logger.info("No gaps in position sequence.")
        
        # Detect items that might be using default position=0
        default_position_count = sum(1 for item in items_by_id if item.position == 0)
        if default_position_count > 1:
            logger.warning(f"Multiple items ({default_position_count}) have the default position=0")
        
        return True

def suggest_fix():
    """
    Suggest fixes for the issue
    """
    logger.info("\nPOTENTIAL FIXES:")
    logger.info("1. Ensure all items have unique, sequential positions starting from 0 or 1")
    logger.info("2. Fix the template CSS to prevent page breaks within table rows")
    logger.info("3. Adjust the template to handle overflow content properly")
    logger.info("4. Use the fix_missing_item14.py script to generate a fixed PDF")
    logger.info("5. Apply the permanent_template_fix.py to update templates with CSS fixes")

if __name__ == "__main__":
    # Set up argument parsing
    parser = argparse.ArgumentParser(description='Diagnose quotation items and positions')
    parser.add_argument('quotation_number', nargs='?', default='PAK-2025-007',
                        help='The quotation number to inspect (default: PAK-2025-007)')
    
    # Parse arguments
    args = parser.parse_args()
    
    # Run the inspection
    if inspect_quotation_by_number(args.quotation_number):
        suggest_fix()
    else:
        print(f"Failed to inspect quotation {args.quotation_number}. Specify a valid quotation number.")
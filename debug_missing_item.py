"""
Debug script to investigate the missing item #14 issue in quotation PDFs.
This script examines quotation items and their data to identify potential issues.
"""

import sys
import logging
from app import app, db
from models import Quotation, QuotationItem
from sqlalchemy import text

# Setup logging
logging.basicConfig(level=logging.INFO, 
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("debug_missing_item")

def inspect_quotation_by_number(quotation_number):
    """
    Examine the items in a specific quotation, focusing on potential rendering issues.
    """
    with app.app_context():
        # Find the quotation
        quotation = Quotation.query.filter_by(quotation_number=quotation_number).first()
        if not quotation:
            logger.error(f"Quotation with number {quotation_number} not found")
            return False
        
        logger.info(f"Inspecting quotation {quotation_number} (ID: {quotation.id})")
        
        # Get items by ID
        items_by_id = QuotationItem.query.filter_by(quotation_id=quotation.id).order_by(QuotationItem.id).all()
        
        # Get items by position
        items_by_position = QuotationItem.query.filter_by(quotation_id=quotation.id).order_by(QuotationItem.position).all()
        
        # Display item count
        logger.info(f"Total items: {len(items_by_id)}")
        
        # Analyze positions
        positions = [item.position for item in items_by_id]
        has_consecutive_positions = all(p2 - p1 == 1 for p1, p2 in zip(positions, positions[1:]))
        
        logger.info(f"All positions are consecutive: {has_consecutive_positions}")
        
        if not has_consecutive_positions:
            logger.info("List of non-consecutive positions:")
            for i in range(len(positions) - 1):
                if positions[i+1] - positions[i] != 1:
                    logger.info(f"  Gap between position {positions[i]} and {positions[i+1]}")
        
        # Find items with duplicate positions
        duplicate_positions = {}
        for item in items_by_id:
            pos = item.position
            if pos in duplicate_positions:
                duplicate_positions[pos].append(item.id)
            else:
                duplicate_positions[pos] = [item.id]
        
        # Log duplicates
        for pos, item_ids in duplicate_positions.items():
            if len(item_ids) > 1:
                logger.warning(f"Position {pos} is used by multiple items: {item_ids}")
        
        # Display detailed item information
        logger.info("\nDETAILED ITEM ANALYSIS:")
        logger.info(f"{'ID':<6} {'Pos':<6} {'Description (truncated)':<50} {'Special Notes':<25}")
        logger.info("-" * 90)
        
        # Track specific positions for the problematic area (around #14)
        problem_range = list(range(12, 16))  # Items with positions 12, 13, 14, 15
        items_in_problem_range = []
        
        for i, item in enumerate(items_by_id, 1):
            special_notes = []
            
            # Check for potential rendering issues
            if item.position in problem_range:
                items_in_problem_range.append(item)
                special_notes.append("In problem range")
            
            if item.position == 0 and i != 1:
                special_notes.append("Default position")
            
            if len(item.description) > 100:
                special_notes.append("Long description")
            
            # Log item details
            logger.info(f"{item.id:<6} {item.position:<6} {item.description[:47] + '...' if len(item.description) > 50 else item.description:<50} {', '.join(special_notes):<25}")
        
        # Detailed analysis of items in the problem range
        if items_in_problem_range:
            logger.info("\nDETAILED ANALYSIS OF PROBLEM RANGE (positions 12-15):")
            logger.info(f"{'ID':<6} {'Pos':<6} {'Expected Position':<18} {'Description Length':<18}")
            logger.info("-" * 60)
            
            for i, item in enumerate(items_in_problem_range):
                expected_pos = problem_range[i] if i < len(problem_range) else "Out of range"
                logger.info(f"{item.id:<6} {item.position:<6} {expected_pos:<18} {len(item.description):<18}")
        
        # Look for content issues
        logger.info("\nCONTENT ANALYSIS (looking for special characters, length issues):")
        for i, item in enumerate(items_by_id, 1):
            # Check if description contains potential problem characters
            problem_chars = ['&', '<', '>', '"', "'", '%', '\\', '/', '\n', '\r', '\t']
            found_chars = [c for c in problem_chars if c in item.description]
            
            if found_chars or len(item.description) > 100:
                logger.info(f"Item #{i} (ID: {item.id}, Pos: {item.position}):")
                if found_chars:
                    logger.info(f"  Contains special characters: {found_chars}")
                if len(item.description) > 100:
                    logger.info(f"  Long description ({len(item.description)} chars)")
        
        return True

def apply_quick_fix(quotation_number):
    """
    Apply a quick fix to the positions for a problematic quotation.
    """
    with app.app_context():
        # Find the quotation
        quotation = Quotation.query.filter_by(quotation_number=quotation_number).first()
        if not quotation:
            logger.error(f"Quotation with number {quotation_number} not found")
            return False
        
        logger.info(f"Applying quick fix to quotation {quotation_number} (ID: {quotation.id})")
        
        # Get items by ID
        items = QuotationItem.query.filter_by(quotation_id=quotation.id).order_by(QuotationItem.id).all()
        
        # Update positions to be sequential starting from 0
        for i, item in enumerate(items):
            # Log the position change
            if item.position != i:
                logger.info(f"Item ID {item.id}: Changing position from {item.position} to {i}")
                item.position = i
        
        # Save changes
        db.session.commit()
        logger.info(f"Fixed positions for {len(items)} items in quotation {quotation_number}")
        
        return True

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python debug_missing_item.py <quotation_number> [--fix]")
        sys.exit(1)
    
    quotation_number = sys.argv[1]
    fix_mode = len(sys.argv) > 2 and sys.argv[2] == "--fix"
    
    if fix_mode:
        success = apply_quick_fix(quotation_number)
        if success:
            print(f"\n✅ Successfully applied quick fix to quotation {quotation_number}")
            print("\nNext steps:")
            print("1. Generate a PDF to test if the fix worked:")
            print(f"   python fix_missing_item14.py {quotation_number}")
        else:
            print(f"\n❌ Failed to apply quick fix to quotation {quotation_number}")
    else:
        success = inspect_quotation_by_number(quotation_number)
        if success:
            print(f"\n✅ Inspection complete for quotation {quotation_number}")
            print("\nTo fix position issues, run:")
            print(f"python debug_missing_item.py {quotation_number} --fix")
        else:
            print(f"\n❌ Failed to inspect quotation {quotation_number}")
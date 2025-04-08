"""
Debug script to investigate the missing item #14 issue in quotation PDFs.
This script examines quotation items and their data to identify potential issues.
"""

import sys
import logging
from app import app, db
from models import Quotation, QuotationItem

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("missing_item_debug")

def inspect_quotation_by_number(quotation_number):
    """
    Examine the items in a specific quotation, focusing on potential rendering issues.
    """
    with app.app_context():
        # Find the quotation
        quotation = Quotation.query.filter_by(quotation_number=quotation_number).first()
        
        if not quotation:
            logger.error(f"Quotation {quotation_number} not found")
            return
        
        logger.info(f"Examining quotation {quotation_number} (ID: {quotation.id})")
        
        # Get items through query and relationship to compare
        query_items = QuotationItem.query.filter_by(quotation_id=quotation.id).order_by(QuotationItem.id).all()
        relationship_items = quotation.items
        
        logger.info(f"Total items (via query): {len(query_items)}")
        logger.info(f"Total items (via relationship): {len(relationship_items)}")
        
        # Check for content issues in all items
        logger.info("\nItem Details (checking for unusual content):")
        logger.info(f"{'Index':^5} | {'ID':^5} | {'Position':^8} | {'Description Length':^17} | {'Description':^30}")
        logger.info("-" * 75)
        
        for idx, item in enumerate(query_items, 1):
            desc_len = len(item.description) if item.description else 0
            desc_preview = (item.description[:27] + "...") if desc_len > 30 else item.description
            logger.info(f"{idx:^5} | {item.id:^5} | {item.position:^8} | {desc_len:^17} | {desc_preview}")
            
            # Check for potential rendering issues
            if desc_len > 100:
                logger.warning(f"Item #{idx} (ID: {item.id}) has a very long description ({desc_len} chars)")
            
            if idx == 14 or idx == 13 or idx == 15:  # Examine items around the problematic index
                logger.info(f"Details for item #{idx} (ID: {item.id}):")
                logger.info(f"  Description: {item.description}")
                logger.info(f"  Scientific Name: {item.scientific_name}")
                logger.info(f"  Pot Size: {item.pot_size}")
                logger.info(f"  Height: {item.height}")
                logger.info(f"  Quantity: {item.quantity}")
                logger.info(f"  Selling Price: {item.selling_price}")
                
                # Check for unusual character content
                unusual_chars = [ch for ch in (item.description or '') if ord(ch) > 127]
                if unusual_chars:
                    logger.warning(f"  Item #{idx} contains unusual characters: {unusual_chars}")
        
        # Check if positions are consecutive
        positions = [item.position for item in query_items]
        if positions != list(range(1, len(positions) + 1)):
            logger.warning(f"Positions are not consecutive: {positions}")
            
            # Identify gaps
            expected_positions = set(range(1, len(positions) + 1))
            actual_positions = set(positions)
            missing = expected_positions - actual_positions
            duplicates = [p for p in positions if positions.count(p) > 1]
            
            if missing:
                logger.warning(f"Missing positions: {missing}")
            if duplicates:
                logger.warning(f"Duplicate positions: {duplicates}")

def apply_quick_fix(quotation_number):
    """
    Apply a quick fix to the positions for a problematic quotation.
    """
    with app.app_context():
        quotation = Quotation.query.filter_by(quotation_number=quotation_number).first()
        if not quotation:
            logger.error(f"Quotation {quotation_number} not found")
            return False
            
        # Get items sorted by ID
        items = QuotationItem.query.filter_by(quotation_id=quotation.id).order_by(QuotationItem.id).all()
        
        # Reset positions to be consecutive starting from 1
        for idx, item in enumerate(items, 1):
            if item.position != idx:
                logger.info(f"Fixing position for item ID {item.id}: {item.position} -> {idx}")
                item.position = idx
        
        db.session.commit()
        logger.info("Fixed positions for all items")
        return True

if __name__ == "__main__":
    if len(sys.argv) > 1:
        quotation_number = sys.argv[1]
    else:
        quotation_number = input("Enter the quotation number to debug: ")
    
    # Inspect the quotation first
    inspect_quotation_by_number(quotation_number)
    
    # Ask if fix should be applied
    if input("\nApply position fix? (y/n): ").lower().strip() == 'y':
        apply_quick_fix(quotation_number)
        logger.info("\nAfter fix:")
        inspect_quotation_by_number(quotation_number)
"""
Quick test script to verify the position fix for quotation items.
This specifically targets quotation PAK-2025-007 where item #14 was missing.
"""

import os
import logging
from datetime import datetime
from app import app, db
from models import Quotation

# Configure logging
logging.basicConfig(level=logging.INFO, 
                    format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_position_fix(quotation_number="PAK-2025-007"):
    """Test that positions are sequential for quotation items"""
    with app.app_context():
        quotation = Quotation.query.filter_by(quotation_number=quotation_number).first()
        if not quotation:
            logger.error(f"Quotation not found: {quotation_number}")
            return False
            
        # Get all items and sort by position
        items = sorted(quotation.items, key=lambda x: x.position)
        
        logger.info(f"Found quotation {quotation_number} with {len(items)} items")
        
        # Check sequential positions
        for i, item in enumerate(items):
            if item.position != i:
                logger.error(f"Position mismatch: Item {i+1} has position {item.position}")
                return False
                
        # Specifically check item #14 (position 13)
        item_14 = next((item for item in items if item.position == 13), None)
        if not item_14:
            logger.error("Item #14 (position 13) not found!")
            return False
            
        logger.info(f"✓ Item #14 found correctly at position 13: {item_14.description}")
        
        # Validate surrounding items
        if len(items) >= 15:
            item_13 = next((item for item in items if item.position == 12), None)
            item_15 = next((item for item in items if item.position == 14), None)
            
            if item_13:
                logger.info(f"✓ Item #13 found at position 12: {item_13.description}")
            if item_15:
                logger.info(f"✓ Item #15 found at position 14: {item_15.description}")
        
        logger.info(f"✓ All {len(items)} items have correct sequential positions")
        return True

if __name__ == "__main__":
    print("Testing quotation position fix...")
    result = test_position_fix()
    if result:
        print("TEST PASSED: All positions are correct")
    else:
        print("TEST FAILED: Position issues detected")
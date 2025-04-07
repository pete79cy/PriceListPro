"""
Diagnostic script to investigate quotation items ordering issue.
This script will:
1. Find the quotation with ID PAK-2025-007 mentioned in the investigation plan
2. Check all items for this quotation, their positions, and ordering
3. Verify if any items are missing or have position issues
"""

import os
import sys
import logging
from datetime import datetime

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("quotation_diagnostic")

# Add the current directory to the path so we can import our app
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import our application
from app import app, db
from models import Quotation, QuotationItem

def inspect_quotation_by_number(quotation_number):
    """
    Examine a specific quotation and its items by quotation number
    """
    logger.info(f"Looking for quotation with number: {quotation_number}")
    
    with app.app_context():
        # Find the quotation
        quotation = Quotation.query.filter_by(quotation_number=quotation_number).first()
        
        if not quotation:
            logger.error(f"Quotation {quotation_number} not found")
            # Try to find alternative quotations to examine
            recent_quotations = Quotation.query.order_by(Quotation.created_at.desc()).limit(5).all()
            if recent_quotations:
                logger.info("Recent quotations that could be examined instead:")
                for q in recent_quotations:
                    logger.info(f"  - ID: {q.id}, Number: {q.quotation_number}, Date: {q.quotation_date}")
            return
        
        logger.info(f"Found quotation: ID={quotation.id}, Number={quotation.quotation_number}, Date={quotation.quotation_date}")
        
        # Get all items for this quotation
        items = QuotationItem.query.filter_by(quotation_id=quotation.id).order_by(QuotationItem.position).all()
        
        logger.info(f"Found {len(items)} items for this quotation")
        
        # Log the query without actually executing it
        logger.info("SQL query equivalent:")
        logger.info("""
            SELECT id, description, position, quantity, selling_price
            FROM quotation_item
            WHERE quotation_id = %s
            ORDER BY position;
        """, quotation.id)
        
        # Analyze items and their positions
        positions = []
        for idx, item in enumerate(items):
            positions.append(item.position)
            logger.info(f"Item {idx+1}: ID={item.id}, Position={item.position}, Description={item.description[:30]}{'...' if len(item.description) > 30 else ''}")
        
        # Check if positions are sequential
        missing_positions = []
        if positions:
            min_pos = min(positions)
            max_pos = max(positions)
            expected_positions = list(range(min_pos, max_pos + 1))
            
            missing_positions = [p for p in expected_positions if p not in positions]
            duplicate_positions = [p for p in set(positions) if positions.count(p) > 1]
            
            if missing_positions:
                logger.warning(f"Missing positions detected: {missing_positions}")
            else:
                logger.info("All positions are sequential with no gaps")
                
            if duplicate_positions:
                logger.warning(f"Duplicate positions detected: {duplicate_positions}")
            else:
                logger.info("No duplicate positions detected")
        
        # Check relationship definition in model
        logger.info("Checking relationship definition in Quotation model...")
        relationship_def = getattr(Quotation, 'items')
        logger.info(f"Relationship definition: {relationship_def}")
        
        # Also check items using the relationship
        related_items = quotation.items
        logger.info(f"Items retrieved via relationship: {len(related_items)}")
        
        # Check if any sorting is applied in the relationship or query
        logger.info("Items accessed via relationship will be sorted: %s", "Yes" if hasattr(relationship_def, "order_by") else "No")
        
        # Compare items count from both methods
        if len(items) != len(related_items):
            logger.warning(f"Discrepancy in items count: Query returned {len(items)}, Relationship returned {len(related_items)}")
        
        # Print items retrieved via relationship and their order
        logger.info("Items order when accessed via relationship:")
        for idx, item in enumerate(related_items):
            logger.info(f"Relationship Item {idx+1}: ID={item.id}, Position={item.position}, Description={item.description[:30]}{'...' if len(item.description) > 30 else ''}")

def suggest_fix():
    """
    Suggest fixes for the issue
    """
    logger.info("\nPossible fixes:")
    logger.info("1. Update the Quotation model to explicitly order items by position:")
    logger.info("""
        class Quotation(db.Model):
            # ... existing code ...
            items = db.relationship('QuotationItem', backref='quotation', 
                                    lazy=True, cascade="all, delete-orphan",
                                    order_by="QuotationItem.position")
    """)
    
    logger.info("\n2. Fix potentially incorrect positions with SQL:")
    logger.info("""
        UPDATE quotation_item
        SET position = row_number() OVER (PARTITION BY quotation_id ORDER BY id)
        WHERE quotation_id = (SELECT id FROM quotation WHERE quotation_number = 'PAK-2025-007');
    """)
    
    logger.info("\n3. Or in Python:")
    logger.info("""
        with app.app_context():
            quotation = Quotation.query.filter_by(quotation_number='PAK-2025-007').first()
            if quotation:
                items = QuotationItem.query.filter_by(quotation_id=quotation.id).order_by(QuotationItem.id).all()
                for idx, item in enumerate(items):
                    item.position = idx + 1
                db.session.commit()
    """)
    
    logger.info("\n4. In the template, ensure items are sorted by position:")
    logger.info("""
        {% for item in quotation.items|sort(attribute='position') %}
            <!-- Item rendering -->
        {% endfor %}
    """)

if __name__ == "__main__":
    # Check the command-line arguments
    if len(sys.argv) > 1:
        quotation_number = sys.argv[1]
    else:
        # Default to the quotation number mentioned in the investigation plan
        quotation_number = "PAK-2025-007"
    
    inspect_quotation_by_number(quotation_number)
    suggest_fix()
"""Script to diagnose quotation item positions"""
from app import db
from models import Quotation, QuotationItem

def inspect_quotation_by_number(quotation_number):
    """Inspect quotation items and their positions"""
    print(f"\nInspecting Quotation {quotation_number}")
    
    quotation = Quotation.query.filter_by(quotation_number=quotation_number).first()
    if not quotation:
        print(f"Quotation {quotation_number} not found")
        return
        
    # Get all items and sort by position
    items = QuotationItem.query.filter_by(quotation_id=quotation.id).order_by(QuotationItem.position).all()
    
    print(f"\nFound {len(items)} items:")
    print("-" * 80)
    print(f"{'Position':^8} | {'Index':^5} | {'Description':<50}")
    print("-" * 80)
    
    for i, item in enumerate(items, 1):
        print(f"{item.position:^8} | {i:^5} | {item.description:<50}")
        
    # Check for gaps or duplicates in position values
    positions = [item.position for item in items]
    expected = list(range(len(items)))
    
    if positions != expected:
        print("\n⚠️ Position sequence is not consecutive!")
        print(f"Expected: {expected}")
        print(f"Actual:   {positions}")
        
def fix_positions(quotation_number):
    """Fix item positions to be consecutive starting from 0"""
    quotation = Quotation.query.filter_by(quotation_number=quotation_number).first()
    if not quotation:
        return False
        
    items = QuotationItem.query.filter_by(quotation_id=quotation.id).order_by(QuotationItem.position).all()
    
    # Reset positions to be consecutive
    for i, item in enumerate(items):
        item.position = i
        
    db.session.commit()
    return True

if __name__ == "__main__":
    quotation_number = "PAK-2025-007"
    inspect_quotation_by_number(quotation_number)
    fix_positions(quotation_number)
    print("\nAfter fixing:")
    inspect_quotation_by_number(quotation_number)

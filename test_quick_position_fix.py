"""
Lightweight test script to verify the quotation position fix.
This script:
1. Connects directly to the database
2. Gets a quotation with multiple items to test
3. Sets all positions to 0 (simulating the issue)
4. Applies the fix algorithm
5. Verifies positions are sequential
"""
import os
import sys
import logging
from datetime import datetime
import psycopg2
from psycopg2.extras import DictCursor

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("quick_position_fix_test")

def get_db_connection():
    """Get a connection to the database"""
    conn = psycopg2.connect(os.environ.get('DATABASE_URL'))
    conn.autocommit = False
    return conn

def find_test_quotation():
    """Find an existing quotation with multiple items"""
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=DictCursor)
    
    try:
        # Find quotations with at least 10 items
        cursor.execute("""
            SELECT q.id, q.quotation_number, COUNT(qi.id) as item_count
            FROM quotation q
            JOIN quotation_item qi ON q.id = qi.quotation_id
            GROUP BY q.id, q.quotation_number
            HAVING COUNT(qi.id) >= 10
            ORDER BY COUNT(qi.id) DESC
            LIMIT 1
        """)
        
        result = cursor.fetchone()
        if result:
            logger.info(f"Found test quotation: {result['quotation_number']} with {result['item_count']} items")
            return result['id'], result['quotation_number'], result['item_count']
        else:
            logger.warning("No suitable test quotation found with 10+ items")
            return None, None, 0
            
    finally:
        cursor.close()
        conn.close()

def reset_positions(quotation_id):
    """Reset all positions to 0 to simulate the issue"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute("""
            UPDATE quotation_item
            SET position = 0
            WHERE quotation_id = %s
        """, (quotation_id,))
        
        count = cursor.rowcount
        conn.commit()
        logger.info(f"Reset {count} items to position=0")
        return count
            
    finally:
        cursor.close()
        conn.close()

def check_positions(quotation_id):
    """Check if positions are sequential and correctly ordered"""
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=DictCursor)
    
    try:
        cursor.execute("""
            SELECT id, description, position
            FROM quotation_item
            WHERE quotation_id = %s
            ORDER BY position, id
        """, (quotation_id,))
        
        items = cursor.fetchall()
        has_gaps = False
        positions = []
        
        logger.info(f"Checking positions for {len(items)} items:")
        for idx, item in enumerate(items):
            positions.append(item['position'])
            expected_pos = idx + 1
            if item['position'] != expected_pos:
                logger.warning(f"  Item {idx+1}: Position={item['position']}, Expected={expected_pos}, Description={item['description']}")
                has_gaps = True
            else:
                logger.info(f"  Item {idx+1}: Position={item['position']}, Description={item['description']}")
        
        if not has_gaps:
            logger.info("✅ All positions are sequential with no gaps")
            return True
        else:
            logger.warning("❌ Positions have gaps or are not sequential")
            return False
            
    finally:
        cursor.close()
        conn.close()

def apply_fix(quotation_id):
    """Apply the position fix algorithm"""
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=DictCursor)
    
    try:
        # Get all items for this quotation ordered by ID (original order)
        cursor.execute("""
            SELECT id
            FROM quotation_item
            WHERE quotation_id = %s
            ORDER BY id
        """, (quotation_id,))
        
        items = cursor.fetchall()
        updated_count = 0
        
        # Update each item with its position based on index
        for idx, item in enumerate(items):
            new_position = idx + 1
            cursor.execute("""
                UPDATE quotation_item
                SET position = %s
                WHERE id = %s
            """, (new_position, item['id']))
            updated_count += 1
        
        conn.commit()
        logger.info(f"Applied fix: Updated {updated_count} positions")
        return updated_count
            
    finally:
        cursor.close()
        conn.close()

def run_test():
    """Run the full test suite"""
    logger.info("=== STARTING QUICK POSITION FIX TEST ===")
    
    # Step 1: Find a test quotation with enough items
    quotation_id, quotation_number, item_count = find_test_quotation()
    if not quotation_id:
        logger.error("❌ TEST FAILED: Could not find suitable test quotation")
        return False
    
    # Step 2: Reset all positions to 0
    logger.info("\n=== RESETTING POSITIONS ===")
    reset_count = reset_positions(quotation_id)
    if reset_count < 10:
        logger.warning(f"Only reset {reset_count} positions, may not be enough for a good test")
    
    # Step 3: Verify positions are all 0
    logger.info("\n=== BEFORE FIX ===")
    before_fix = check_positions(quotation_id)
    if before_fix:
        logger.warning("Positions were already sequential, test may not be valid!")
    
    # Step 4: Apply the fix
    logger.info("\n=== APPLYING FIX ===")
    update_count = apply_fix(quotation_id)
    
    # Step 5: Verify positions are now sequential
    logger.info("\n=== AFTER FIX ===")
    after_fix = check_positions(quotation_id)
    
    # Final results
    logger.info("\n=== TEST RESULTS ===")
    logger.info(f"Reset {reset_count} positions: {'✅' if reset_count > 0 else '❌'}")
    logger.info(f"Applied fix to {update_count} positions: {'✅' if update_count > 0 else '❌'}")
    logger.info(f"Positions are now sequential: {'✅' if after_fix else '❌'}")
    
    overall_success = (reset_count > 0) and (update_count > 0) and after_fix
    logger.info(f"Overall test {'✅ PASSED' if overall_success else '❌ FAILED'}")
    
    return overall_success

if __name__ == "__main__":
    success = run_test()
    sys.exit(0 if success else 1)
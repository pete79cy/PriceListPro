"""
Test script to verify the fix for quotation item positions.
This script:
1. Creates a test quotation with 15 items (more than the 14 where issues were observed)
2. Intentionally sets all positions to 0 (simulating the original issue)
3. Runs the fix script
4. Verifies that positions are sequential
5. Generates a PDF report to confirm the fix visually
"""
import os
import sys
import logging
from datetime import datetime
from flask import Flask

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("quotation_fix_test")

# Import our application and models
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from app import db
from models import Quotation, QuotationItem, Customer
from utils.pdf_generator import generate_quotation_pdf

# Create a test Flask app for isolation
app = Flask(__name__)
app.config['TESTING'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL')  # Use real database
db.init_app(app)

def create_test_quotation():
    """
    Create a test quotation with 15 items, all with position=0
    to simulate the original issue
    """
    # Create a test customer or use an existing one
    customer = Customer.query.first()
    if not customer:
        customer = Customer(name="Test Customer", email="test@example.com")
        db.session.add(customer)
        db.session.commit()
        logger.info(f"Created test customer: {customer.name}")
    
    # Create a test quotation
    quotation_number = f"TEST-POS-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
    quotation = Quotation(
        quotation_number=quotation_number,
        quotation_date=datetime.now().date(),
        customer_id=customer.id,
        currency="€",
        notes="Test quotation for position fix verification"
    )
    db.session.add(quotation)
    db.session.commit()
    logger.info(f"Created test quotation: {quotation.quotation_number}")
    
    # Add 15 items with position=0 (simulating the issue)
    for i in range(1, 16):
        item = QuotationItem(
            quotation_id=quotation.id,
            description=f"Test Item {i}",
            scientific_name=f"Testus itemus {i}",
            pot_size=f"{10+i}cm",
            height=f"{50+i*10}cm",
            quantity=i,
            selling_price=10.00 + i,
            vat_rate=19.0,
            supplier=f"Test Supplier {(i % 3) + 1}",
            position=0  # All positions set to 0 to simulate the issue
        )
        db.session.add(item)
    
    db.session.commit()
    logger.info(f"Added 15 items to quotation, all with position=0")
    
    return quotation

def check_positions(quotation_id):
    """
    Check if positions for the given quotation are sequential
    """
    quotation = Quotation.query.get(quotation_id)
    items = sorted(quotation.items, key=lambda x: x.position)
    
    logger.info(f"Positions for quotation {quotation.quotation_number}:")
    
    has_gaps = False
    prev_pos = 0
    positions = []
    for idx, item in enumerate(items):
        positions.append(item.position)
        expected_pos = idx + 1
        if item.position != expected_pos:
            logger.warning(f"  Item {idx+1}: Position={item.position}, Expected={expected_pos}, Description={item.description}")
            has_gaps = True
        else:
            logger.info(f"  Item {idx+1}: Position={item.position}, Description={item.description}")
        prev_pos = item.position
    
    if not has_gaps:
        logger.info("✅ All positions are sequential with no gaps")
        return True
    else:
        logger.warning("❌ Positions have gaps or are not sequential")
        return False

def fix_positions(quotation_id):
    """
    Fix positions for items in the given quotation
    """
    from fix_quotation_items_position import _fix_positions_for_quotation
    
    quotation = Quotation.query.get(quotation_id)
    logger.info(f"Fixing positions for quotation: {quotation.quotation_number}")
    
    updated_count = _fix_positions_for_quotation(quotation)
    db.session.commit()
    
    logger.info(f"Updated {updated_count} positions")
    return updated_count > 0

def generate_test_pdf(quotation_id):
    """
    Generate a PDF for the quotation to visually verify fix
    """
    quotation = Quotation.query.get(quotation_id)
    logger.info(f"Generating PDF for quotation: {quotation.quotation_number}")
    
    try:
        pdf_data, filename = generate_quotation_pdf(quotation.id)
        
        # Save the PDF to verify it
        output_path = f"test_fixed_quotation_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        with open(output_path, "wb") as f:
            f.write(pdf_data)
        
        logger.info(f"✅ PDF generated successfully and saved to: {output_path}")
        logger.info(f"File size: {os.path.getsize(output_path)} bytes")
        return True
        
    except Exception as e:
        logger.error(f"❌ Error generating PDF: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())
        return False

def run_test():
    """
    Run the full test suite
    """
    logger.info("=== STARTING QUOTATION POSITION FIX TEST ===")
    
    # Step 1: Create test quotation with position=0 for all items
    with app.app_context():
        quotation = create_test_quotation()
        quotation_id = quotation.id
    
        # Step 2: Verify positions are all 0 (or otherwise problematic)
        logger.info("\n=== BEFORE FIX ===")
        check_positions(quotation_id)
        
        # Step 3: Apply the fix
        logger.info("\n=== APPLYING FIX ===")
        success = fix_positions(quotation_id)
        
        # Step 4: Verify positions are now sequential
        logger.info("\n=== AFTER FIX ===")
        positions_ok = check_positions(quotation_id)
        
        # Final results
        logger.info("\n=== TEST RESULTS ===")
        logger.info(f"Fix applied successfully: {'✅' if success else '❌'}")
        logger.info(f"Positions are sequential: {'✅' if positions_ok else '❌'}")
        
        overall_success = success and positions_ok
        logger.info(f"Overall test {'✅ PASSED' if overall_success else '❌ FAILED'}")
        
        return overall_success

if __name__ == "__main__":
    success = run_test()
    sys.exit(0 if success else 1)
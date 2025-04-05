"""
Test script to fix products created with incorrect names from "New arrival" format messages.
This script updates the product name for any product with a single character name and 
also includes a direct test of the message parsing function.
"""

import logging
import re
from app import app, db
from models import Supplier, SupplierProduct
from viber_integration import extract_product_info

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def fix_product_name(supplier_id, product_id, new_name):
    """Update a product's name."""
    with app.app_context():
        try:
            product = SupplierProduct.query.get(product_id)
            if not product:
                logger.error(f"Product with ID {product_id} not found")
                return False
                
            if product.supplier_id != supplier_id:
                logger.error(f"Product with ID {product_id} belongs to supplier {product.supplier_id}, not {supplier_id}")
                return False
                
            old_name = product.product_name
            product.product_name = new_name
            db.session.commit()
            logger.info(f"Updated product name from '{old_name}' to '{new_name}'")
            return True
                
        except Exception as e:
            logger.error(f"Error updating product name: {str(e)}")
            db.session.rollback()
            return False
            
def find_single_character_products(supplier_id):
    """Find products with a single character name."""
    with app.app_context():
        try:
            products = SupplierProduct.query.filter_by(supplier_id=supplier_id).all()
            single_char_products = [p for p in products if len(p.product_name.strip()) <= 1]
            
            if single_char_products:
                logger.info(f"Found {len(single_char_products)} products with single-character names:")
                for p in single_char_products:
                    logger.info(f"  ID: {p.id}, Name: '{p.product_name}', Scientific Name: {p.scientific_name}")
            else:
                logger.info("No products with single-character names found")
                
            return single_char_products
                
        except Exception as e:
            logger.error(f"Error finding products: {str(e)}")
            return []

def test_message_parsing():
    """Test the message parsing function directly with the problematic message format."""
    logger.info("Testing message parsing with the problematic format...")
    
    # A test message with the "New arrival:" prefix
    test_message = "Νέα παραλαβή: ΦΙΚΟΣ ΕΛΑΣΤΙΚΑ ΤΡΙΧΡΩΜΟΣ (Ficus elastica) ύψος 45-50cm σε γλάστρα 17cm, κόστος €12,90"
    
    # Try our own custom parsing for this specific format
    logger.info(f"Message: {test_message}")
    
    # Try a custom pattern for this specific format
    pattern = r'Νέα\s+παραλαβή:\s+(.*?)\s+\('
    match = re.search(pattern, test_message)
    if match:
        product_name = match.group(1).strip()
        logger.info(f"Extracted product name directly: {product_name}")
        
        # Also test with the standard function
        parsed_info = extract_product_info(test_message)
        logger.info(f"Standard function result: {parsed_info}")
        
        if parsed_info and parsed_info.get('product_name') != product_name:
            logger.warning(f"Mismatch between direct parsing ({product_name}) and function parsing ({parsed_info.get('product_name')})")
    else:
        logger.warning("Could not extract product name with custom pattern")
    
    # Test a very simple pattern to ensure regex is working properly
    simple_match = re.search(r'ΦΙΚΟΣ\s+ΕΛΑΣΤΙΚΑ', test_message)
    if simple_match:
        logger.info(f"Simple pattern match: {simple_match.group(0)}")
    else:
        logger.warning("Simple pattern failed to match")
            
def main():
    """Main function to fix products with incorrect names."""
    logger.info("Starting to fix products with incorrect names...")
    
    # First, test direct message parsing
    test_message_parsing()
    
    # Find products with single-character names
    supplier_id = 5  # Moesis
    single_char_products = find_single_character_products(supplier_id)
    
    # For our specific case, we know product with scientific name Ficus elastica should be ΦΙΚΟΣ ΕΛΑΣΤΙΚΑ
    for product in single_char_products:
        if product.scientific_name == "Ficus elastica":
            if fix_product_name(supplier_id, product.id, "ΦΙΚΟΣ ΕΛΑΣΤΙΚΑ ΤΡΙΧΡΩΜΟΣ"):
                logger.info(f"Successfully fixed product ID {product.id} name to 'ΦΙΚΟΣ ΕΛΑΣΤΙΚΑ ΤΡΙΧΡΩΜΟΣ'")
            else:
                logger.error(f"Failed to fix product ID {product.id}")
                
    logger.info("Finished fixing products with incorrect names")
    
if __name__ == "__main__":
    main()
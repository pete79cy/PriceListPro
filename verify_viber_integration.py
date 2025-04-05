"""
Test the Viber integration by parsing a message and looking up the result in the database.
This script:
1. Loads the application context
2. Runs the message parser to extract info from a test message
3. Queries the database to see if the product exists
4. Creates or updates the product using the extracted information
"""

import logging
from app import app, db
from models import Supplier, SupplierProduct
from viber_integration import extract_product_info

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Test messages
test_messages = [
    # Different formats of messages
    {
        "description": "Structured format with all fields",
        "message": "Product: ΛΑΝΤΑΝΑ, Scientific name: Lantana camara, Size: 30cm, Pot: 17cm, Price: €4.50", 
        "supplier_id": 5  # Moesis
    },
    {
        "description": "Semi-structured format with parentheses",
        "message": "ΚΥΚΑΣ ΡΕΒΟΛΟΥΤΑ (Cycas revoluta) 100-120cm pot 25cm, price €65.00",
        "supplier_id": 5  # Moesis
    },
    {
        "description": "Unstructured format with Greek text",
        "message": "Νέα παραλαβή: ΦΙΚΟΣ ΕΛΑΣΤΙΚΑ (Ficus elastica) ύψος 45-50cm σε γλάστρα 17cm, κόστος €12,90",
        "supplier_id": 5  # Moesis
    }
]

def update_product(supplier_id, product_info):
    """Update or create a supplier product in the database."""
    try:
        # Validate required fields
        if not product_info or 'product_name' not in product_info or 'price' not in product_info:
            logger.error("Required product information missing")
            return False
        
        # Try to find an existing product by name for this supplier
        existing_product = SupplierProduct.query.filter_by(
            supplier_id=supplier_id,
            product_name=product_info['product_name']
        ).first()
        
        if existing_product:
            # Update existing product
            logger.info(f"Found existing product: {existing_product.product_name}")
            logger.info(f"Current price: {existing_product.price}, New price: {product_info['price']}")
            
            if 'scientific_name' in product_info:
                existing_product.scientific_name = product_info['scientific_name']
            if 'height' in product_info:
                existing_product.height = product_info['height']
            if 'pot_size' in product_info:
                existing_product.pot_size = product_info['pot_size']
            
            # Always update the price
            existing_product.price = float(product_info['price'])
            
            # Set the cost price the same as the price if it doesn't exist
            if not existing_product.cost_price:
                existing_product.cost_price = float(product_info['price'])
                
            db.session.commit()
            logger.info(f"Updated existing product: {product_info['product_name']} for supplier ID {supplier_id}")
            return existing_product
        else:
            # Create new product
            logger.info(f"Creating new product: {product_info['product_name']}")
            new_product = SupplierProduct(
                supplier_id=supplier_id,
                product_name=product_info['product_name'],
                price=float(product_info['price']),
                cost_price=float(product_info['price']),
                scientific_name=product_info.get('scientific_name', ''),
                height=product_info.get('height', ''),
                pot_size=product_info.get('pot_size', '')
            )
            
            db.session.add(new_product)
            db.session.commit()
            logger.info(f"Created new product: {product_info['product_name']} for supplier ID {supplier_id}")
            return new_product
            
    except Exception as e:
        logger.error(f"Error updating supplier product: {str(e)}")
        db.session.rollback()
        return None

def verify_supplier_exists(supplier_id):
    """Verify that the supplier exists in the database."""
    supplier = Supplier.query.get(supplier_id)
    if supplier:
        logger.info(f"Found supplier: {supplier.name} (ID: {supplier.id})")
        return supplier
    else:
        logger.error(f"Supplier with ID {supplier_id} not found")
        return None

def main():
    """Main function to test the Viber integration."""
    # Initialize the app context
    with app.app_context():
        logger.info("Starting Viber integration verification...")
        
        for idx, test in enumerate(test_messages):
            logger.info(f"\n----- Test {idx+1}: {test['description']} -----")
            logger.info(f"Message: {test['message']}")
            
            # Extract product info
            product_info = extract_product_info(test['message'])
            
            if product_info:
                logger.info(f"Extracted product info: {product_info}")
                
                # Verify supplier exists
                supplier = verify_supplier_exists(test['supplier_id'])
                if supplier:
                    # Update or create the product
                    result = update_product(test['supplier_id'], product_info)
                    
                    if result:
                        logger.info(f"Success: Product ID {result.id} - {result.product_name} with price €{result.price}")
                    else:
                        logger.error("Failed to update or create product")
            else:
                logger.error(f"Failed to extract product info from: {test['message']}")
            
            logger.info("-" * 50)
        
        logger.info("Viber integration verification completed.")

if __name__ == "__main__":
    main()
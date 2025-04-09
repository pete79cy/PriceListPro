"""
Test script for supplier duplicates detection flow.
This script tests the complete flow from database to session handling.
"""

import os
import sys
import logging
import json
from datetime import datetime
from app import app, db
from models import Supplier, Product

# Configure logging
logging.basicConfig(level=logging.INFO,
                   format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Dummy Flask session for testing
class DummySession(dict):
    """Simulate Flask session for testing"""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
    def modified(self):
        """Simulate session modification flag"""
        logger.info("Session was modified")

# Function to convert SQLAlchemy objects to dictionaries
def serialize_supplier(supplier):
    """Convert a Supplier SQLAlchemy object to a dictionary"""
    return {
        'id': supplier.id,
        'name': supplier.name,
        'email': supplier.email,
        'phone': supplier.phone,
        'products_count': len(supplier.products)
    }

def serialize_product(product):
    """Convert a Product SQLAlchemy object to a dictionary"""
    return {
        'id': product.id,
        'name': product.name,
        'description': product.description or '',
        'price': float(product.price) if product.price else 0.0,
        'category': product.category,
        'supplier_id': product.supplier_id
    }

def test_supplier_duplicate_flow(supplier_id=None):
    """Test the complete supplier duplicate detection flow"""
    logger.info("Testing supplier duplicate detection flow")
    
    with app.app_context():
        # Find a supplier with products if not specified
        if not supplier_id:
            supplier = Supplier.query.filter(Supplier.products.any()).first()
            if not supplier:
                logger.error("No suppliers with products found in database")
                return False
            supplier_id = supplier.id
            
        # Get the supplier and their products
        supplier = Supplier.query.get(supplier_id)
        if not supplier:
            logger.error(f"Supplier with ID {supplier_id} not found")
            return False
            
        logger.info(f"Testing with supplier: {supplier.name} (ID: {supplier_id})")
        logger.info(f"Supplier has {len(supplier.products)} products")
        
        # Convert supplier's products to serializable format
        products = [serialize_product(p) for p in supplier.products]
        
        # Convert supplier to serializable format
        supplier_dict = serialize_supplier(supplier)
        
        # Create a mock session
        session = DummySession()
        session['analysis_supplier'] = supplier_dict
        session['analysis_products'] = products
        
        # Verify the session contains proper JSON-serializable data
        try:
            # Try to JSON serialize the data (this would fail with SQLAlchemy objects)
            supplier_json = json.dumps(session['analysis_supplier'])
            products_json = json.dumps(session['analysis_products'])
            
            logger.info(f"✅ Successfully serialized supplier data: {len(supplier_json)} bytes")
            logger.info(f"✅ Successfully serialized products data: {len(products_json)} bytes")
            
            # Verify we can reconstruct the objects
            supplier_from_json = json.loads(supplier_json)
            products_from_json = json.loads(products_json)
            
            logger.info(f"✅ Successfully reconstructed data from JSON")
            logger.info(f"Supplier name: {supplier_from_json['name']}")
            logger.info(f"First product name: {products_from_json[0]['name'] if products_from_json else 'No products'}")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Serialization error: {str(e)}")
            import traceback
            logger.error(traceback.format_exc())
            return False

def main():
    """Main test function"""
    logger.info("Starting supplier duplicates flow test")
    
    # Get supplier ID from command line if provided
    supplier_id = int(sys.argv[1]) if len(sys.argv) > 1 else None
    
    # Run the test
    success = test_supplier_duplicate_flow(supplier_id)
    
    if success:
        logger.info("✅ Supplier duplicates flow test passed successfully!")
        return 0
    else:
        logger.error("❌ Supplier duplicates flow test failed")
        return 1

if __name__ == "__main__":
    sys.exit(main())
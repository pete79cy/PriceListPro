#!/usr/bin/env python
"""
Quotation Import Script

This script imports quotations from JSON files exported by the export_quotations_direct.py script.
It can be used to migrate quotation data to a new system.
"""
import os
import sys
import json
import logging
import argparse
import datetime
from pathlib import Path

from app import app, db
from models import (
    Quotation, QuotationItem, Customer, Product, Supplier,
    CustomerCategory, SupplierCategory
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('quotation_import.log')
    ]
)
logger = logging.getLogger('quotation_import')

def load_export_file(file_path):
    """
    Load exported quotation data from a JSON file.
    
    Args:
        file_path: Path to the JSON export file
        
    Returns:
        dict: The loaded quotation data, or None if loading failed
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Validate the structure of the export file
        if 'metadata' not in data or 'quotations' not in data:
            logger.error(f"Invalid export file format: {file_path}")
            return None
        
        logger.info(f"Loaded export file: {file_path}")
        logger.info(f"Contains {len(data['quotations'])} quotations")
        return data
        
    except Exception as e:
        logger.error(f"Error loading export file {file_path}: {str(e)}")
        return None

def get_or_create_customer(customer_data):
    """
    Find an existing customer or create a new one.
    
    Args:
        customer_data: Dictionary with customer information
        
    Returns:
        Customer: The existing or new customer object
    """
    try:
        # Try to find by ID first
        if 'id' in customer_data and customer_data['id']:
            customer = Customer.query.get(customer_data['id'])
            if customer:
                return customer
        
        # Try to find by name if ID not found or not provided
        if 'name' in customer_data and customer_data['name']:
            customer = Customer.query.filter_by(name=customer_data['name']).first()
            if customer:
                return customer
        
        # Create a new customer if not found
        if 'name' in customer_data and customer_data['name']:
            # Create default category if needed
            default_category = CustomerCategory.query.filter_by(name='General').first()
            if not default_category:
                default_category = CustomerCategory(name='General', description='Default category for imported customers')
                db.session.add(default_category)
                db.session.flush()
            
            # Create new customer
            customer = Customer(
                name=customer_data.get('name', ''),
                email=customer_data.get('email', ''),
                phone=customer_data.get('phone', ''),
                category_id=default_category.id
            )
            db.session.add(customer)
            db.session.flush()
            logger.info(f"Created new customer: {customer.name} (ID: {customer.id})")
            return customer
        
        logger.error(f"Invalid customer data, could not create customer: {customer_data}")
        return None
        
    except Exception as e:
        logger.error(f"Error getting or creating customer: {str(e)}")
        return None

def get_or_create_supplier(supplier_data):
    """
    Find an existing supplier or create a new one.
    
    Args:
        supplier_data: Dictionary with supplier information
        
    Returns:
        Supplier: The existing or new supplier object
    """
    try:
        # Try to find by ID first
        if 'id' in supplier_data and supplier_data['id']:
            supplier = Supplier.query.get(supplier_data['id'])
            if supplier:
                return supplier
        
        # Try to find by name if ID not found or not provided
        if 'name' in supplier_data and supplier_data['name']:
            supplier = Supplier.query.filter_by(name=supplier_data['name']).first()
            if supplier:
                return supplier
        
        # Create a new supplier if not found
        if 'name' in supplier_data and supplier_data['name']:
            # Create default category if needed
            default_category = SupplierCategory.query.filter_by(name='General').first()
            if not default_category:
                default_category = SupplierCategory(name='General', description='Default category for imported suppliers')
                db.session.add(default_category)
                db.session.flush()
            
            # Create new supplier
            supplier = Supplier(
                name=supplier_data.get('name', ''),
                email=supplier_data.get('email', ''),
                phone='',  # No phone in export
                category_id=default_category.id
            )
            db.session.add(supplier)
            db.session.flush()
            logger.info(f"Created new supplier: {supplier.name} (ID: {supplier.id})")
            return supplier
        
        logger.error(f"Invalid supplier data, could not create supplier: {supplier_data}")
        return None
        
    except Exception as e:
        logger.error(f"Error getting or creating supplier: {str(e)}")
        return None

def get_or_create_product(product_data):
    """
    Find an existing product or create a new one.
    
    Args:
        product_data: Dictionary with product information
        
    Returns:
        Product: The existing or new product object
    """
    try:
        # Try to find by ID first
        if 'id' in product_data and product_data['id']:
            product = Product.query.get(product_data['id'])
            if product:
                return product
        
        # Try to find by name if ID not found or not provided
        if 'name' in product_data and product_data['name']:
            product = Product.query.filter_by(name=product_data['name']).first()
            if product:
                return product
        
        # Create a new product if not found
        if 'name' in product_data and product_data['name']:
            # Create new product
            product = Product(
                name=product_data.get('name', ''),
                scientific_name=product_data.get('scientific_name', '')
            )
            db.session.add(product)
            db.session.flush()
            logger.info(f"Created new product: {product.name} (ID: {product.id})")
            return product
        
        logger.error(f"Invalid product data, could not create product: {product_data}")
        return None
        
    except Exception as e:
        logger.error(f"Error getting or creating product: {str(e)}")
        return None

def import_quotation(quotation_data, skip_existing=True):
    """
    Import a single quotation.
    
    Args:
        quotation_data: Dictionary with quotation information
        skip_existing: Whether to skip quotations that already exist
        
    Returns:
        Quotation: The imported quotation object, or None if import failed
    """
    try:
        # Check if quotation already exists
        existing = Quotation.query.filter_by(quotation_number=quotation_data.get('quotation_number')).first()
        if existing and skip_existing:
            logger.info(f"Skipping existing quotation: {existing.quotation_number} (ID: {existing.id})")
            return existing
        
        # Get or create customer
        customer = get_or_create_customer(quotation_data.get('customer', {}))
        if not customer:
            logger.error(f"Could not get or create customer for quotation {quotation_data.get('quotation_number')}")
            return None
        
        # Parse date
        quotation_date = None
        if 'quotation_date' in quotation_data and quotation_data['quotation_date']:
            try:
                if isinstance(quotation_data['quotation_date'], str):
                    # Try ISO format first
                    try:
                        quotation_date = datetime.datetime.fromisoformat(quotation_data['quotation_date'])
                    except ValueError:
                        # Try other formats
                        formats = ['%Y-%m-%d', '%d/%m/%Y', '%m/%d/%Y']
                        for fmt in formats:
                            try:
                                quotation_date = datetime.datetime.strptime(quotation_data['quotation_date'], fmt)
                                break
                            except ValueError:
                                continue
            except Exception as e:
                logger.warning(f"Could not parse quotation date: {quotation_data['quotation_date']} - {str(e)}")
        
        # Create new quotation or update existing
        if existing and not skip_existing:
            # Update existing quotation
            quotation = existing
            quotation.customer_id = customer.id
            quotation.quotation_date = quotation_date
            quotation.total_amount = quotation_data.get('total_amount', 0)
            quotation.currency = quotation_data.get('currency', '€')
            quotation.notes = quotation_data.get('notes', '')
            quotation.status = quotation_data.get('status', 'COMPLETED')
            quotation.updated_at = datetime.datetime.now()
            logger.info(f"Updating existing quotation: {quotation.quotation_number} (ID: {quotation.id})")
        else:
            # Create new quotation
            quotation = Quotation(
                customer_id=customer.id,
                quotation_number=quotation_data.get('quotation_number', ''),
                quotation_date=quotation_date,
                total_amount=quotation_data.get('total_amount', 0),
                currency=quotation_data.get('currency', '€'),
                notes=quotation_data.get('notes', ''),
                status=quotation_data.get('status', 'COMPLETED'),
                created_at=datetime.datetime.now(),
                updated_at=datetime.datetime.now()
            )
            db.session.add(quotation)
            db.session.flush()
            logger.info(f"Created new quotation: {quotation.quotation_number} (ID: {quotation.id})")
        
        # Clear existing items if updating
        if existing and not skip_existing:
            for item in existing.items:
                db.session.delete(item)
            db.session.flush()
        
        # Import items
        if 'items' in quotation_data and quotation_data['items']:
            for position, item_data in enumerate(quotation_data['items']):
                # Get or create supplier
                supplier = None
                if 'supplier_data' in item_data and item_data['supplier_data']:
                    supplier = get_or_create_supplier(item_data['supplier_data'])
                
                # Get or create product
                product = None
                if 'product_data' in item_data and item_data['product_data']:
                    product = get_or_create_product(item_data['product_data'])
                
                # Create item
                item = QuotationItem(
                    quotation_id=quotation.id,
                    description=item_data.get('description', ''),
                    quantity=item_data.get('quantity', 0),
                    unit_price=item_data.get('unit_price', 0),
                    unit=item_data.get('unit', ''),
                    position=position,  # Set position based on order in list
                    product_id=product.id if product else None,
                    supplier_id=supplier.id if supplier else None
                )
                db.session.add(item)
            
            db.session.flush()
            logger.info(f"Added {len(quotation_data['items'])} items to quotation {quotation.quotation_number}")
        
        return quotation
        
    except Exception as e:
        logger.error(f"Error importing quotation: {str(e)}")
        return None

def import_quotations(export_data, skip_existing=True):
    """
    Import quotations from export data.
    
    Args:
        export_data: Dictionary with exported quotation data
        skip_existing: Whether to skip quotations that already exist
        
    Returns:
        int: Number of quotations successfully imported
    """
    try:
        if 'quotations' not in export_data or not export_data['quotations']:
            logger.error("No quotations found in export data")
            return 0
        
        with app.app_context():
            # Begin transaction
            successful_imports = 0
            
            for quotation_data in export_data['quotations']:
                quotation = import_quotation(quotation_data, skip_existing)
                if quotation:
                    successful_imports += 1
            
            # Commit if successful
            if successful_imports > 0:
                db.session.commit()
                logger.info(f"Successfully imported {successful_imports} quotations")
            else:
                db.session.rollback()
                logger.warning("No quotations were imported, rolling back transaction")
            
            return successful_imports
        
    except Exception as e:
        logger.error(f"Error importing quotations: {str(e)}")
        with app.app_context():
            db.session.rollback()
        return 0

def main():
    """Main function for command-line usage."""
    parser = argparse.ArgumentParser(description='Import quotations from JSON export file')
    parser.add_argument('file', help='Path to the JSON export file')
    parser.add_argument('--force', action='store_true', help='Update existing quotations instead of skipping them')
    
    args = parser.parse_args()
    
    try:
        # Load the export file
        export_data = load_export_file(args.file)
        if not export_data:
            print(f"Error: Could not load export file: {args.file}")
            return 1
        
        # Import quotations
        imported = import_quotations(export_data, skip_existing=not args.force)
        
        if imported > 0:
            print(f"Successfully imported {imported} quotations")
            return 0
        else:
            print("No quotations were imported")
            return 1
        
    except Exception as e:
        logger.error(f"Error during import: {str(e)}")
        print(f"Error: {str(e)}")
        return 1

if __name__ == '__main__':
    sys.exit(main())
#!/usr/bin/env python
"""
Standalone Quotation Export Script

This script exports quotations from the database to JSON format for migration
to a newer version of the application.

Usage:
    python standalone_export.py [--all] [--customer-id ID] [--quotation-id ID] [--output-dir DIR]
"""
import os
import sys
import json
import logging
import argparse
import datetime
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('quotation_export.log')
    ]
)
logger = logging.getLogger('quotation_export')

# Import Flask app and models
from app import app, db
from models import Quotation, QuotationItem, Customer, Supplier, Product

def serialize_quotation(quotation):
    """
    Serialize a quotation object to a dictionary for JSON export.
    
    Args:
        quotation: The Quotation object to serialize
        
    Returns:
        dict: Serialized quotation data
    """
    # Basic quotation data
    quotation_data = {
        'id': quotation.id,
        'quotation_number': quotation.quotation_number,
        'quotation_date': quotation.quotation_date.isoformat() if quotation.quotation_date else None,
        'total_amount': quotation.total_amount,
        'currency': quotation.currency,
        'notes': quotation.notes,
        'created_at': quotation.created_at.isoformat() if quotation.created_at else None,
        'updated_at': quotation.updated_at.isoformat() if quotation.updated_at else None,
        'file_path': quotation.file_path,
        'customer': {
            'id': quotation.customer.id,
            'name': quotation.customer.name,
            'email': quotation.customer.email,
            'phone': quotation.customer.phone,
            # Add more customer fields as needed
        },
        'items': []
    }
    
    # Serialize each quotation item
    for item in quotation.items:
        item_data = {
            'id': item.id,
            'description': item.description,
            'scientific_name': item.scientific_name,
            'pot_size': item.pot_size,
            'height': item.height,
            'quantity': item.quantity,
            'selling_price': item.selling_price,
            'vat_rate': item.vat_rate,
            'supplier': item.supplier,
            'cost_price': item.cost_price,
            'total': item.total,
            'position': item.position,
            'product_id': item.product_id
        }
        
        # Add supplier data if available
        if item.supplier_ref:
            item_data['supplier_data'] = {
                'id': item.supplier_ref.id,
                'name': item.supplier_ref.name,
                'email': item.supplier_ref.email
                # Add more supplier fields as needed
            }
        
        # Add product data if available
        if item.product:
            item_data['product_data'] = {
                'id': item.product.id,
                'name': item.product.name,
                'scientific_name': item.product.scientific_name if hasattr(item.product, 'scientific_name') else None
                # Add more product fields as needed
            }
        
        quotation_data['items'].append(item_data)
    
    return quotation_data

def export_all_quotations(output_dir=None):
    """
    Export all quotations to a JSON file.
    
    Args:
        output_dir: Directory to save the export file
        
    Returns:
        str: Path to the export file
    """
    with app.app_context():
        # Get all quotations
        quotations = Quotation.query.all()
        logger.info(f"Found {len(quotations)} quotations to export")
        
        # Initialize the export data structure
        export_data = {
            'metadata': {
                'export_date': datetime.datetime.now().isoformat(),
                'quotation_count': len(quotations),
                'version': '1.0',
                'description': 'Quotation data export for migration'
            },
            'quotations': []
        }
        
        # Process each quotation
        for quotation in quotations:
            # Add the serialized quotation to the export data
            quotation_data = serialize_quotation(quotation)
            export_data['quotations'].append(quotation_data)
        
        # Generate export filename with timestamp
        timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
        export_filename = f"quotations_export_{timestamp}.json"
        
        # Ensure export directory exists
        if output_dir:
            export_dir = Path(output_dir)
        else:
            export_dir = Path(os.getcwd()) / 'exports'
        
        os.makedirs(export_dir, exist_ok=True)
        export_path = export_dir / export_filename
        
        # Write export data to JSON file
        with open(export_path, 'w', encoding='utf-8') as f:
            json.dump(export_data, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Successfully exported {len(quotations)} quotations to {export_path}")
        return str(export_path)

def export_customer_quotations(customer_id, output_dir=None):
    """
    Export all quotations for a specific customer.
    
    Args:
        customer_id: ID of the customer
        output_dir: Directory to save the export file
        
    Returns:
        str: Path to the export file
    """
    with app.app_context():
        # Get the customer
        customer = Customer.query.get(customer_id)
        if not customer:
            logger.error(f"Customer with ID {customer_id} not found")
            return None
        
        # Get all quotations for this customer
        quotations = Quotation.query.filter_by(customer_id=customer_id).all()
        logger.info(f"Found {len(quotations)} quotations for customer {customer.name}")
        
        # Initialize the export data structure
        export_data = {
            'metadata': {
                'export_date': datetime.datetime.now().isoformat(),
                'quotation_count': len(quotations),
                'version': '1.0',
                'description': f'Quotation export for customer {customer.name}'
            },
            'quotations': []
        }
        
        # Process each quotation
        for quotation in quotations:
            # Add the serialized quotation to the export data
            quotation_data = serialize_quotation(quotation)
            export_data['quotations'].append(quotation_data)
        
        # Generate export filename with customer name and timestamp
        timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
        safe_customer_name = customer.name.replace(' ', '_').replace('/', '_')[:30]
        export_filename = f"quotations_{safe_customer_name}_{timestamp}.json"
        
        # Ensure export directory exists
        if output_dir:
            export_dir = Path(output_dir)
        else:
            export_dir = Path(os.getcwd()) / 'exports'
        
        os.makedirs(export_dir, exist_ok=True)
        export_path = export_dir / export_filename
        
        # Write export data to JSON file
        with open(export_path, 'w', encoding='utf-8') as f:
            json.dump(export_data, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Successfully exported {len(quotations)} quotations for customer {customer.name} to {export_path}")
        return str(export_path)

def export_single_quotation(quotation_id, output_dir=None):
    """
    Export a specific quotation.
    
    Args:
        quotation_id: ID of the quotation
        output_dir: Directory to save the export file
        
    Returns:
        str: Path to the export file
    """
    with app.app_context():
        # Get the quotation
        quotation = Quotation.query.get(quotation_id)
        if not quotation:
            logger.error(f"Quotation with ID {quotation_id} not found")
            return None
        
        # Initialize the export data structure
        export_data = {
            'metadata': {
                'export_date': datetime.datetime.now().isoformat(),
                'quotation_count': 1,
                'version': '1.0',
                'description': f'Single quotation export for quotation {quotation.quotation_number}'
            },
            'quotations': [serialize_quotation(quotation)]
        }
        
        # Generate export filename with quotation number and timestamp
        timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
        safe_quotation_number = quotation.quotation_number.replace('/', '_')
        export_filename = f"quotation_{safe_quotation_number}_{timestamp}.json"
        
        # Ensure export directory exists
        if output_dir:
            export_dir = Path(output_dir)
        else:
            export_dir = Path(os.getcwd()) / 'exports'
        
        os.makedirs(export_dir, exist_ok=True)
        export_path = export_dir / export_filename
        
        # Write export data to JSON file
        with open(export_path, 'w', encoding='utf-8') as f:
            json.dump(export_data, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Successfully exported quotation {quotation.quotation_number} to {export_path}")
        return str(export_path)

def main():
    """Main function for command-line usage."""
    parser = argparse.ArgumentParser(description='Export quotations to JSON for migration')
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('--all', action='store_true', help='Export all quotations')
    group.add_argument('--customer-id', type=int, help='Export quotations for a specific customer')
    group.add_argument('--quotation-id', type=int, help='Export a specific quotation')
    
    parser.add_argument('--output-dir', help='Directory to save export files')
    
    args = parser.parse_args()
    
    try:
        if args.all:
            export_path = export_all_quotations(args.output_dir)
            if export_path:
                print(f"Successfully exported all quotations to: {export_path}")
                return 0
            else:
                print("Failed to export quotations")
                return 1
        
        elif args.customer_id:
            export_path = export_customer_quotations(args.customer_id, args.output_dir)
            if export_path:
                print(f"Successfully exported customer quotations to: {export_path}")
                return 0
            else:
                print(f"Failed to export quotations for customer ID {args.customer_id}")
                return 1
        
        elif args.quotation_id:
            export_path = export_single_quotation(args.quotation_id, args.output_dir)
            if export_path:
                print(f"Successfully exported quotation to: {export_path}")
                return 0
            else:
                print(f"Failed to export quotation ID {args.quotation_id}")
                return 1
    
    except Exception as e:
        logger.error(f"Error during export: {str(e)}")
        print(f"Error: {str(e)}")
        return 1

if __name__ == '__main__':
    sys.exit(main())
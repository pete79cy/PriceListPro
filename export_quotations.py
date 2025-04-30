#!/usr/bin/env python
"""
Quotation Export Tool

This script exports all quotations and their related data from the database to a JSON file.
The exported data can be used to migrate quotations to a new version of the application.

Usage:
    python export_quotations.py [--output-dir DIRECTORY]
"""
import os
import sys
import json
import logging
import argparse
import datetime
from pathlib import Path
from flask import Flask

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

# Import application modules
from app import db, app
from models import Quotation, QuotationItem, Customer, Supplier, Product

class QuotationExporter:
    """Tool for exporting quotations to JSON format for migration."""
    
    def __init__(self, output_dir=None):
        """
        Initialize the exporter tool.
        
        Args:
            output_dir: Directory to store the exported JSON files
        """
        # Set export directory
        if output_dir:
            self.export_dir = Path(output_dir)
        else:
            self.export_dir = Path(os.getcwd()) / 'exports'
        
        # Create export directory if it doesn't exist
        os.makedirs(self.export_dir, exist_ok=True)
        
        logger.info(f"Exporter initialized. Export directory: {self.export_dir}")
    
    def export_all_quotations(self):
        """
        Export all quotations to a JSON file.
        
        Returns:
            str: Path to the exported JSON file
        """
        with app.app_context():
            # Get all quotations with their relationships
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
                # Serialize the quotation and its items
                quotation_data = self._serialize_quotation(quotation)
                export_data['quotations'].append(quotation_data)
            
            # Generate export filename with timestamp
            timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
            export_filename = f"quotations_export_{timestamp}.json"
            export_path = self.export_dir / export_filename
            
            # Write export data to JSON file
            try:
                with open(export_path, 'w', encoding='utf-8') as f:
                    json.dump(export_data, f, indent=2, ensure_ascii=False)
                
                logger.info(f"Successfully exported {len(quotations)} quotations to {export_path}")
                return export_path
            except Exception as e:
                logger.error(f"Failed to write export file: {str(e)}")
                return None
    
    def export_quotation_by_id(self, quotation_id):
        """
        Export a specific quotation by ID.
        
        Args:
            quotation_id: The ID of the quotation to export
            
        Returns:
            str: Path to the exported JSON file
        """
        with app.app_context():
            # Get the quotation with its relationships
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
                'quotations': [self._serialize_quotation(quotation)]
            }
            
            # Generate export filename with quotation number and timestamp
            timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
            export_filename = f"quotation_{quotation.quotation_number.replace('/', '_')}_{timestamp}.json"
            export_path = self.export_dir / export_filename
            
            # Write export data to JSON file
            try:
                with open(export_path, 'w', encoding='utf-8') as f:
                    json.dump(export_data, f, indent=2, ensure_ascii=False)
                
                logger.info(f"Successfully exported quotation {quotation.quotation_number} to {export_path}")
                return export_path
            except Exception as e:
                logger.error(f"Failed to write export file: {str(e)}")
                return None
    
    def export_quotations_by_customer(self, customer_id):
        """
        Export all quotations for a specific customer.
        
        Args:
            customer_id: The ID of the customer whose quotations to export
            
        Returns:
            str: Path to the exported JSON file
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
                # Serialize the quotation and its items
                quotation_data = self._serialize_quotation(quotation)
                export_data['quotations'].append(quotation_data)
            
            # Generate export filename with customer name and timestamp
            timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
            safe_customer_name = customer.name.replace(' ', '_').replace('/', '_')[:30]
            export_filename = f"quotations_{safe_customer_name}_{timestamp}.json"
            export_path = self.export_dir / export_filename
            
            # Write export data to JSON file
            try:
                with open(export_path, 'w', encoding='utf-8') as f:
                    json.dump(export_data, f, indent=2, ensure_ascii=False)
                
                logger.info(f"Successfully exported {len(quotations)} quotations for customer {customer.name} to {export_path}")
                return export_path
            except Exception as e:
                logger.error(f"Failed to write export file: {str(e)}")
                return None
    
    def _serialize_quotation(self, quotation):
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

def main():
    """Command-line interface for the quotation exporter."""
    parser = argparse.ArgumentParser(description='Quotation Export Tool')
    parser.add_argument('--output-dir', help='Directory to store the exported JSON files')
    parser.add_argument('--customer-id', type=int, help='Export quotations for a specific customer')
    parser.add_argument('--quotation-id', type=int, help='Export a specific quotation')
    
    args = parser.parse_args()
    
    # Create exporter instance
    exporter = QuotationExporter(output_dir=args.output_dir)
    
    if args.quotation_id:
        # Export a specific quotation
        export_path = exporter.export_quotation_by_id(args.quotation_id)
        if export_path:
            print(f"Quotation exported to {export_path}")
            return 0
        else:
            print("Failed to export quotation")
            return 1
    
    elif args.customer_id:
        # Export quotations for a specific customer
        export_path = exporter.export_quotations_by_customer(args.customer_id)
        if export_path:
            print(f"Customer quotations exported to {export_path}")
            return 0
        else:
            print("Failed to export customer quotations")
            return 1
    
    else:
        # Export all quotations
        export_path = exporter.export_all_quotations()
        if export_path:
            print(f"All quotations exported to {export_path}")
            return 0
        else:
            print("Failed to export quotations")
            return 1

if __name__ == '__main__':
    sys.exit(main())
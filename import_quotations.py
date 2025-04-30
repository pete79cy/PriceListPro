#!/usr/bin/env python
"""
Quotation Import Tool

This script imports quotations from a JSON file exported by the export_quotations.py tool.
It's designed to migrate quotations to a new version of the application.

Usage:
    python import_quotations.py --file EXPORT_FILE.json [--dry-run]
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
        logging.FileHandler('quotation_import.log')
    ]
)
logger = logging.getLogger('quotation_import')

# Import application modules
from app import db, app
from models import Quotation, QuotationItem, Customer, Supplier, Product

class QuotationImporter:
    """Tool for importing quotations from JSON format (exported by export_quotations.py)."""
    
    def __init__(self, dry_run=False):
        """
        Initialize the importer tool.
        
        Args:
            dry_run: If True, no changes will be saved to the database
        """
        self.dry_run = dry_run
        if dry_run:
            logger.info("DRY RUN MODE: No changes will be saved to the database")
        
        # Statistics
        self.stats = {
            'quotations_found': 0,
            'quotations_imported': 0,
            'quotations_skipped': 0,
            'items_imported': 0,
            'items_skipped': 0,
            'errors': 0
        }
        
        # Store mapping of old IDs to new IDs for reference
        self.id_mapping = {
            'quotations': {},
            'items': {}
        }
    
    def import_from_file(self, file_path):
        """
        Import quotations from an export file.
        
        Args:
            file_path: Path to the JSON export file
            
        Returns:
            dict: Import statistics
        """
        logger.info(f"Importing quotations from {file_path}")
        
        # Load the export file
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                export_data = json.load(f)
        except Exception as e:
            logger.error(f"Failed to load export file: {str(e)}")
            return self.stats
        
        # Extract metadata
        metadata = export_data.get('metadata', {})
        quotation_count = metadata.get('quotation_count', 0)
        logger.info(f"Found {quotation_count} quotations in export file")
        self.stats['quotations_found'] = quotation_count
        
        # Process each quotation
        quotations = export_data.get('quotations', [])
        with app.app_context():
            for quotation_data in quotations:
                try:
                    self._import_quotation(quotation_data)
                except Exception as e:
                    logger.error(f"Error importing quotation: {str(e)}")
                    self.stats['errors'] += 1
            
            # Commit changes if not in dry run mode
            if not self.dry_run:
                try:
                    db.session.commit()
                    logger.info("Committed all changes to database")
                except Exception as e:
                    logger.error(f"Failed to commit changes: {str(e)}")
                    db.session.rollback()
                    self.stats['errors'] += 1
            else:
                logger.info("Dry run - rolling back all changes")
                db.session.rollback()
        
        # Log import statistics
        self._log_import_stats()
        
        return self.stats
    
    def _import_quotation(self, quotation_data):
        """
        Import a single quotation and its items.
        
        Args:
            quotation_data: Dictionary containing quotation data
        """
        # Extract quotation details
        quotation_number = quotation_data.get('quotation_number')
        customer_data = quotation_data.get('customer', {})
        items_data = quotation_data.get('items', [])
        
        logger.info(f"Processing quotation {quotation_number}")
        
        # Check if quotation already exists
        existing_quotation = Quotation.query.filter_by(quotation_number=quotation_number).first()
        if existing_quotation:
            logger.info(f"Quotation {quotation_number} already exists, skipping")
            self.stats['quotations_skipped'] += 1
            return
        
        # Find or create customer
        customer_id = customer_data.get('id')
        customer_name = customer_data.get('name')
        customer = Customer.query.filter_by(name=customer_name).first()
        
        if not customer:
            logger.warning(f"Customer {customer_name} not found, trying to find by ID")
            customer = Customer.query.get(customer_id)
            
        if not customer:
            logger.warning(f"Customer {customer_name} (ID: {customer_id}) not found in the system")
            logger.warning("Quotation can't be imported without a valid customer, skipping")
            self.stats['quotations_skipped'] += 1
            return
        
        # Create new quotation object
        new_quotation = Quotation(
            customer_id=customer.id,
            quotation_number=quotation_number,
            total_amount=quotation_data.get('total_amount'),
            currency=quotation_data.get('currency', '€'),
            notes=quotation_data.get('notes')
        )
        
        # Set dates
        if quotation_data.get('quotation_date'):
            new_quotation.quotation_date = datetime.datetime.fromisoformat(
                quotation_data.get('quotation_date')).date()
        
        # Add to session
        db.session.add(new_quotation)
        db.session.flush()  # Get ID without committing
        
        # Store ID mapping
        self.id_mapping['quotations'][quotation_data.get('id')] = new_quotation.id
        
        # Import items
        imported_items = 0
        for item_data in items_data:
            try:
                self._import_quotation_item(new_quotation, item_data)
                imported_items += 1
            except Exception as e:
                logger.error(f"Error importing item {item_data.get('description')}: {str(e)}")
                self.stats['errors'] += 1
                self.stats['items_skipped'] += 1
        
        logger.info(f"Imported {imported_items} items for quotation {quotation_number}")
        self.stats['items_imported'] += imported_items
        self.stats['quotations_imported'] += 1
    
    def _import_quotation_item(self, quotation, item_data):
        """
        Import a single quotation item.
        
        Args:
            quotation: The parent Quotation object
            item_data: Dictionary containing item data
        """
        # Find product if it exists
        product_id = item_data.get('product_id')
        product = None
        if product_id:
            product = Product.query.get(product_id)
            if not product and 'product_data' in item_data:
                # Try to find by name
                product_name = item_data.get('product_data', {}).get('name')
                if product_name:
                    product = Product.query.filter_by(name=product_name).first()
        
        # Find supplier if it exists
        supplier_id = item_data.get('supplier_id')
        supplier = None
        if supplier_id:
            supplier = Supplier.query.get(supplier_id)
            if not supplier and 'supplier_data' in item_data:
                # Try to find by name
                supplier_name = item_data.get('supplier_data', {}).get('name')
                if supplier_name:
                    supplier = Supplier.query.filter_by(name=supplier_name).first()
        
        # Create new quotation item
        new_item = QuotationItem(
            quotation_id=quotation.id,
            product_id=product.id if product else None,
            supplier_id=supplier.id if supplier else None,
            description=item_data.get('description', ''),
            scientific_name=item_data.get('scientific_name'),
            pot_size=item_data.get('pot_size'),
            height=item_data.get('height'),
            quantity=item_data.get('quantity', 1),
            selling_price=item_data.get('selling_price', 0),
            vat_rate=item_data.get('vat_rate', 19.0),
            supplier=item_data.get('supplier'),
            cost_price=item_data.get('cost_price'),
            total=item_data.get('total'),
            position=item_data.get('position', 0)
        )
        
        # Add to session
        db.session.add(new_item)
        db.session.flush()  # Get ID without committing
        
        # Store ID mapping
        self.id_mapping['items'][item_data.get('id')] = new_item.id
    
    def _log_import_stats(self):
        """Log import statistics."""
        logger.info("=" * 50)
        logger.info("Import Statistics:")
        logger.info(f"- Quotations found in export: {self.stats['quotations_found']}")
        logger.info(f"- Quotations imported: {self.stats['quotations_imported']}")
        logger.info(f"- Quotations skipped: {self.stats['quotations_skipped']}")
        logger.info(f"- Items imported: {self.stats['items_imported']}")
        logger.info(f"- Items skipped: {self.stats['items_skipped']}")
        logger.info(f"- Errors encountered: {self.stats['errors']}")
        logger.info("=" * 50)
    
    def get_import_report(self):
        """
        Generate a detailed import report.
        
        Returns:
            str: Report text
        """
        report = [
            "===== Quotation Import Report =====",
            f"Date: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            f"Mode: {'DRY RUN (no changes saved)' if self.dry_run else 'LIVE RUN'}",
            "",
            "Import Statistics:",
            f"- Quotations found in export: {self.stats['quotations_found']}",
            f"- Quotations imported: {self.stats['quotations_imported']}",
            f"- Quotations skipped: {self.stats['quotations_skipped']}",
            f"- Items imported: {self.stats['items_imported']}",
            f"- Items skipped: {self.stats['items_skipped']}",
            f"- Errors encountered: {self.stats['errors']}",
            "",
            "ID Mapping (Old ID → New ID):",
            "Quotations:"
        ]
        
        # Add quotation ID mapping
        for old_id, new_id in self.id_mapping['quotations'].items():
            report.append(f"- {old_id} → {new_id}")
        
        report.append("")
        report.append("===== End of Report =====")
        
        return "\n".join(report)

def main():
    """Command-line interface for the quotation importer."""
    parser = argparse.ArgumentParser(description='Quotation Import Tool')
    parser.add_argument('--file', required=True, help='Path to the JSON export file')
    parser.add_argument('--dry-run', action='store_true', help='Test import without saving changes')
    parser.add_argument('--report', help='Path to save the import report')
    
    args = parser.parse_args()
    
    # Check if export file exists
    if not os.path.exists(args.file):
        logger.error(f"Export file not found: {args.file}")
        return 1
    
    # Create importer instance
    importer = QuotationImporter(dry_run=args.dry_run)
    
    # Run import
    importer.import_from_file(args.file)
    
    # Generate report
    report = importer.get_import_report()
    print(report)
    
    # Save report if requested
    if args.report:
        try:
            with open(args.report, 'w') as f:
                f.write(report)
            logger.info(f"Import report saved to {args.report}")
        except Exception as e:
            logger.error(f"Failed to save report: {str(e)}")
    
    # Return success if no errors
    return 0 if importer.stats['errors'] == 0 else 1

if __name__ == '__main__':
    sys.exit(main())
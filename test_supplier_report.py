"""
Test script to generate a supplier report using the enhanced FPDF implementation.
"""

import os
import sys
from datetime import datetime
from flask import Flask
from app import db
from models import Quotation, QuotationItem, CompanySettings
from utils.pdf_generator import generate_custom_supplier_report

# Create a test Flask app and context
app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL")
db.init_app(app)

def test_supplier_report_generation():
    """Generate a test supplier report in PDF format using both implementations."""
    
    with app.app_context():
        # Find a quotation with items from multiple suppliers
        quotation = Quotation.query.filter(Quotation.items.any()).first()
        
        if not quotation:
            print("No quotation with items found in the database.")
            return
        
        print(f"Using quotation: {quotation.quotation_number} with {len(quotation.items)} items")
        
        # Get unique suppliers from the quotation
        suppliers = sorted(list(set(item.supplier for item in quotation.items if item.supplier)))
        if not suppliers:
            print("No suppliers found in the quotation items.")
            return
            
        print(f"Found suppliers: {', '.join(suppliers)}")
        
        # Generate report using WeasyPrint (default)
        print("Generating report using WeasyPrint...")
        try:
            pdf_content, filename = generate_custom_supplier_report(
                quotation=quotation,
                selected_suppliers=suppliers[:2],  # Use first two suppliers
                selected_fields=['description', 'quantity', 'supplier', 'unit', 'height'],
                include_prices=True,
                notes="This is a test report generated using WeasyPrint.",
                use_fpdf=False  # Use WeasyPrint
            )
            
            # Save the file
            with open(filename, 'wb') as f:
                f.write(pdf_content)
            print(f"WeasyPrint report saved as: {filename}")
            
        except Exception as e:
            print(f"Error generating WeasyPrint report: {str(e)}")
            
        # Generate report using FPDF
        print("\nGenerating report using FPDF...")
        try:
            pdf_content, filename = generate_custom_supplier_report(
                quotation=quotation,
                selected_suppliers=suppliers[:2],  # Use first two suppliers
                selected_fields=['description', 'quantity', 'part_number', 'reference', 'height'],
                include_prices=True,
                notes="This is a test report generated using FPDF with supplier summary.",
                use_fpdf=True  # Use FPDF
            )
            
            # Save the file
            with open(filename, 'wb') as f:
                f.write(pdf_content)
            print(f"FPDF report saved as: {filename}")
            
        except Exception as e:
            print(f"Error generating FPDF report: {str(e)}")

if __name__ == "__main__":
    test_supplier_report_generation()
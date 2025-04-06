"""
Test script for generating a custom supplier PDF report using Ubuntu font
"""
import os
import sys
from datetime import datetime
from flask import Flask
from app import db
from models import Quotation, QuotationItem, CompanySettings, Customer

# Create a simple test application context
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
db.init_app(app)

def test_ubuntu_font_report():
    """Test the Ubuntu font version of the supplier report"""
    from utils.pdf_generator import generate_custom_supplier_report
    
    with app.app_context():
        # Create tables
        db.create_all()
        
        # Create a test customer
        customer = Customer(name="Test Customer")
        db.session.add(customer)
        db.session.commit()
        
        # Create company settings
        company = CompanySettings(
            name="Test Company",
            address_line1="123 Test Street",
            address_line2="Test City, 12345",
            email="test@example.com",
            phone="+49 987 654321"
        )
        db.session.add(company)
        db.session.commit()
        
        # Create a test quotation
        quotation = Quotation(
            quotation_number="TEST-2025-001",
            quotation_date=datetime.now(),
            customer_id=customer.id,
            currency="€",
            notes="Test quotation"
        )
        db.session.add(quotation)
        db.session.commit()
        
        # Add some items with different suppliers and various special characters
        suppliers = ["Supplier Αβγ", "Supplier 你好", "Supplier Café"]
        
        items = [
            # Greek characters
            QuotationItem(
                quotation_id=quotation.id,
                description="Plant Ελληνικά",
                scientific_name="Scientific Αβγδεζ",
                pot_size="20",
                height="150-170",
                quantity=10,
                selling_price=25.0,
                cost_price=15.0,
                supplier=suppliers[0]
            ),
            # Chinese characters
            QuotationItem(
                quotation_id=quotation.id,
                description="Plant 中文",
                scientific_name="Scientific 你好世界",
                pot_size="25",
                height="180-200",
                quantity=5,
                selling_price=35.0,
                cost_price=22.0,
                supplier=suppliers[1]
            ),
            # Accented characters
            QuotationItem(
                quotation_id=quotation.id,
                description="Plant Café",
                scientific_name="Scientific résumé",
                pot_size="30",
                height="210-230",
                quantity=8,
                selling_price=40.0,
                cost_price=28.0,
                supplier=suppliers[2]
            )
        ]
        
        for item in items:
            db.session.add(item)
        db.session.commit()
        
        # Test the three versions of PDF generation
        pdf_versions = [
            {"name": "WeasyPrint (Default)", "use_fpdf": False, "use_dejavu": False},
            {"name": "FPDF (Basic)", "use_fpdf": True, "use_dejavu": False},
            {"name": "FPDF with Ubuntu Font", "use_fpdf": True, "use_dejavu": True}
        ]
        
        for version in pdf_versions:
            print(f"Testing {version['name']} implementation...")
            try:
                pdf_content, filename = generate_custom_supplier_report(
                    quotation, 
                    suppliers, 
                    ["description", "scientific_name", "pot_size", "height"],
                    include_prices=True,
                    include_company_header=True,
                    include_terms=True,
                    group_by_supplier=True,
                    notes="Test notes with special characters: Ελληνικά 你好 Café",
                    use_fpdf=version["use_fpdf"],
                    use_dejavu=version["use_dejavu"]
                )
                
                output_file = f"test_report_{version['name'].replace(' ', '_').lower()}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
                with open(output_file, "wb") as f:
                    f.write(pdf_content)
                print(f"✓ PDF saved to {output_file}")
            except Exception as e:
                print(f"✗ Error generating {version['name']} PDF: {str(e)}")
                import traceback
                print(traceback.format_exc())
        
        print("Test completed.")

if __name__ == "__main__":
    test_ubuntu_font_report()
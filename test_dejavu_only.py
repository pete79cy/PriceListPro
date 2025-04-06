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

def test_dejavu_only():
    """Test the DejaVu Sans font version of the supplier report"""
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
        
        # Test only the DejaVu implementation
        print("Testing DejaVu font implementation...")
        pdf_content, filename = generate_custom_supplier_report(
            quotation, 
            suppliers, 
            ["description", "scientific_name", "pot_size", "height"],
            include_prices=True,
            include_company_header=True,
            include_terms=True,
            group_by_supplier=True,
            notes="Test notes with special characters: Ελληνικά 你好 Café",
            use_fpdf=True,
            use_dejavu=True
        )
        
        output_file = f"supplier_report_dejavu_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        with open(output_file, "wb") as f:
            f.write(pdf_content)
        print(f"DejaVu PDF saved to {output_file}")
        
        print("Test completed successfully.")

if __name__ == "__main__":
    test_dejavu_only()
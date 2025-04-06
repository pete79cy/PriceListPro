"""
Test the Ubuntu font PDF implementation
"""
import os
from datetime import datetime, timedelta
from flask import Flask
from app import db
from models import Quotation, QuotationItem, CompanySettings, Customer
from utils.pdf_generator_update import generate_custom_supplier_report_with_ubuntu

# Create a test Flask app
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
db.init_app(app)

def create_test_data():
    """Create test data for the PDF report"""
    # Create a customer
    customer = Customer(name="Test Customer")
    db.session.add(customer)
    db.session.commit()
    
    # Create company settings
    company = CompanySettings(
        name="Pakkoutis Enterprise Ltd.",
        address_line1="123 Test Street",
        address_line2="Test City, 12345",
        email="test@example.com",
        phone="+1 234 567890"
    )
    db.session.add(company)
    db.session.commit()
    
    # Create a quotation
    quotation_date = datetime.now().date()
    quotation = Quotation(
        quotation_number="PAK-2025-TEST",
        quotation_date=quotation_date,
        customer_id=customer.id,
        currency="€",
        notes="Test quotation with special characters: Ελληνικά 你好 Café"
    )
    db.session.add(quotation)
    db.session.commit()
    
    # Add items with different suppliers and Unicode characters
    items = [
        # Greek characters
        QuotationItem(
            quotation_id=quotation.id,
            description="Ελληνικό φυτό (Greek Plant)",
            scientific_name="Αβγδεζ ελληνικός",
            pot_size="20cm",
            height="180-200cm",
            quantity=5,
            cost_price=18.50,
            selling_price=29.95,
            supplier="Supplier Αβγ"
        ),
        # Chinese characters
        QuotationItem(
            quotation_id=quotation.id,
            description="中文植物 (Chinese Plant)",
            scientific_name="你好世界 scientificus",
            pot_size="25cm",
            height="120-150cm",
            quantity=3,
            cost_price=22.00,
            selling_price=42.50,
            supplier="Supplier 你好"
        ),
        # European accented characters
        QuotationItem(
            quotation_id=quotation.id,
            description="Café Plante (French Plant)",
            scientific_name="Résumé européenne",
            pot_size="15cm",
            height="50-60cm",
            quantity=8,
            cost_price=9.75,
            selling_price=19.95,
            supplier="Supplier Café"
        )
    ]
    
    for item in items:
        db.session.add(item)
    db.session.commit()
    
    return quotation

def test_unicode_pdf():
    """Generate and test the Unicode PDF report"""
    with app.app_context():
        # Create database tables
        print("Creating database tables...")
        db.create_all()
        
        # Create test data
        print("Creating test data...")
        quotation = create_test_data()
        print(f"Created quotation: {quotation.quotation_number}")
        
        # Get all unique suppliers
        suppliers = list(set(item.supplier for item in quotation.items))
        print(f"Found suppliers: {suppliers}")
        
        # Fields to include in the report
        fields = ["description", "scientific_name", "height", "pot_size"]
        print(f"Using fields: {fields}")
        
        try:
            # Generate PDF with Ubuntu font
            print("Generating PDF with Ubuntu font...")
            print(f"Current directory: {os.getcwd()}")
            print(f"Checking if font files exist:")
            font_path = os.path.join(os.getcwd(), 'static/fonts/DejaVuSans.ttf')
            print(f"Font path: {font_path}, exists: {os.path.exists(font_path)}")
            
            pdf_content, filename = generate_custom_supplier_report_with_ubuntu(
                quotation,
                suppliers,
                fields,
                include_prices=True,
                include_company_header=True,
                include_terms=True,
                group_by_supplier=True,
                notes="This is a test report with Unicode characters: Ελληνικά 你好 Café"
            )
            
            print(f"PDF generation complete. Got {len(pdf_content) if pdf_content else 0} bytes and filename: {filename}")
            
            # Save the PDF to a file
            output_path = f"test_ubuntu_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
            with open(output_path, "wb") as f:
                f.write(pdf_content)
            
            print(f"PDF report generated successfully and saved to: {output_path}")
            print(f"File size: {os.path.getsize(output_path)} bytes")
            return True
            
        except Exception as e:
            print(f"Error generating PDF: {str(e)}")
            import traceback
            print(traceback.format_exc())
            return False

if __name__ == "__main__":
    success = test_unicode_pdf()
    print(f"Test {'succeeded' if success else 'failed'}")
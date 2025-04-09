
import os
import sys
from flask import Flask
from app import app, db
from models import Quotation

def main():
    with app.app_context():
        # Get a quotation to test
        quotation_id = 1
        quotation = Quotation.query.get(quotation_id)
        
        if not quotation:
            print(f"No quotation found with ID: {quotation_id}")
            return
        
        print(f"Using quotation: {quotation.quotation_number}")
        print(f"Number of items: {len(quotation.items)}")
        
        # Import the flexible PDF generator
        from utils.flexible_pdf_generator import generate_flexible_quotation_pdf
        
        # Generate a test PDF
        output_dir = os.path.join('uploads', 'test_pdf')
        os.makedirs(output_dir, exist_ok=True)
        
        output_path = generate_flexible_quotation_pdf(
            quotation=quotation,
            selected_fields=['position', 'description', 'quantity', 'selling_price', 'total'],
            upload_folder=output_dir,
            debug=True
        )
        
        if output_path:
            print(f"✅ PDF generated successfully: {output_path}")
        else:
            print("❌ Failed to generate PDF")

if __name__ == "__main__":
    main()

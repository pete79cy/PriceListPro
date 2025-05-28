
#!/usr/bin/env python3
"""
Script to update invoice addendum number from 1741 to 1742
"""

from app import app, db
from models import InvoiceAddendum

def update_invoice_number():
    with app.app_context():
        # Find the addendum with invoice number 1741
        addendum = InvoiceAddendum.query.filter_by(invoice_number='1741').first()
        
        if addendum:
            print(f"Found addendum: {addendum.invoice_number} - {addendum.customer.name}")
            
            # Update the invoice number
            addendum.invoice_number = '1742'
            
            try:
                db.session.commit()
                print(f"✅ Successfully updated invoice number to 1742")
                print(f"Customer: {addendum.customer.name}")
                print(f"Period: {addendum.period_from} to {addendum.period_to}")
            except Exception as e:
                db.session.rollback()
                print(f"❌ Error updating invoice number: {str(e)}")
        else:
            print("❌ No addendum found with invoice number 1741")

if __name__ == '__main__':
    update_invoice_number()

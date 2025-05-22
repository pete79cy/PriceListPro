"""
Test script to generate a sample Initial Charge Sheet with the new design.
This will create a sample order with items similar to the attached image and generate the charge sheet.
"""
from app import app, db
from models import Order, OrderItem, Customer
from utils.pdf_generator import generate_charge_sheet_pdf
from datetime import datetime, date
import os

def create_sample_data():
    """Create sample data for testing the charge sheet"""
    with app.app_context():
        # Create a test customer if none exists
        customer = Customer.query.filter_by(name="Test Customer").first()
        if not customer:
            customer = Customer(name="Test Customer", email="test@example.com", phone="+357 99 123456")
            db.session.add(customer)
            db.session.commit()
        
        # Create a test order
        order = Order(
            customer_id=customer.id,
            order_number="ORD-2025-TEST",
            status="new",
            delivery_date=date.today(),
            notes="Sample order for testing the charge sheet design"
        )
        db.session.add(order)
        db.session.commit()
        
        # Add sample items based on the attached image
        items = [
            OrderItem(
                order_id=order.id,
                plant_name="Στρελίτσια Nicolai",
                size="10L",
                quantity=10,
                price=10.00,
                vat_rate=19.0
            ),
            OrderItem(
                order_id=order.id,
                plant_name="Ευγενία Etna Fire",
                size="5L",
                quantity=5,
                price=26.00,
                vat_rate=19.0
            )
        ]
        
        for item in items:
            db.session.add(item)
        
        db.session.commit()
        
        return order.id

def generate_and_save_pdf(order_id):
    """Generate the charge sheet PDF and save it to a file"""
    with app.app_context():
        order = Order.query.get(order_id)
        if not order:
            print("Order not found!")
            return None
        
        # Generate PDF
        pdf_data = generate_charge_sheet_pdf(order)
        
        # Create output directory if it doesn't exist
        os.makedirs("output", exist_ok=True)
        
        # Save to file
        output_path = f"output/charge_sheet_{order.order_number}.pdf"
        with open(output_path, "wb") as f:
            f.write(pdf_data)
        
        print(f"Charge sheet saved to: {output_path}")
        return output_path

if __name__ == "__main__":
    print("Creating sample order data...")
    order_id = create_sample_data()
    
    print("Generating charge sheet PDF...")
    pdf_path = generate_and_save_pdf(order_id)
    
    if pdf_path:
        print("\nSuccess! The redesigned charge sheet has been generated.")
        print(f"PDF saved to: {pdf_path}")
        print("View this file to see all the design improvements.")
    else:
        print("Failed to generate the charge sheet.")
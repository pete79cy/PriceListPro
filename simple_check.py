#!/usr/bin/env python
"""
Simple script to check if the database has quotations
"""
import sys
from app import app, db
from models import Quotation

def check_quotations():
    """Check if there are any quotations in the database."""
    with app.app_context():
        count = Quotation.query.count()
        print(f"Found {count} quotations in the database.")
        
        if count > 0:
            first = Quotation.query.first()
            print(f"First quotation: {first.quotation_number}")
            print(f"Customer: {first.customer.name if first.customer else 'Unknown'}")
            print(f"Items: {len(first.items)}")
        
        return count > 0

if __name__ == "__main__":
    check_quotations()
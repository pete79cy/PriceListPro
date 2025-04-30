#!/usr/bin/env python
from app import app, db
from models import Quotation

def main():
    with app.app_context():
        q = Quotation.query.first()
        if q:
            print(f"Found quotation: {q.quotation_number}")
            print(f"Customer: {q.customer.name if q.customer else 'Unknown'}")
            print(f"Items: {len(q.items)}")
        else:
            print("No quotations found in the database")

if __name__ == "__main__":
    main()
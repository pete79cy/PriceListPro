#!/usr/bin/env python
"""
List Quotations Script

This script lists all quotations in the system to help with migration planning.
"""
import os
import sys
from app import app, db
from models import Quotation

def list_quotations():
    """List all quotations in the system with basic information."""
    with app.app_context():
        quotations = Quotation.query.all()
        print(f'Found {len(quotations)} quotations:')
        print('-' * 80)
        print(f'{"ID":<5} {"Number":<15} {"Date":<12} {"Customer":<30} {"Items":<5} {"Total":<10}')
        print('-' * 80)
        
        for q in quotations:
            # Format the date if it exists
            date_str = q.quotation_date.strftime('%Y-%m-%d') if q.quotation_date else 'N/A'
            
            # Get customer name safely
            customer_name = q.customer.name if q.customer else 'Unknown'
            
            # Format the total amount
            total = f'{q.currency}{q.total_amount:.2f}' if q.total_amount else 'N/A'
            
            print(f'{q.id:<5} {q.quotation_number:<15} {date_str:<12} {customer_name[:30]:<30} {len(q.items):<5} {total:<10}')
            
        print('-' * 80)
        print(f'Total quotations: {len(quotations)}')

if __name__ == '__main__':
    list_quotations()
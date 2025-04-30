#!/usr/bin/env python
"""
List Quotations Script

This script lists all quotations in the system to help with migration planning.
"""
import os
import sys
from app import app, db
from models import Quotation, Customer

def list_all_quotations():
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

def list_customers():
    """List all customers that have quotations."""
    with app.app_context():
        # Find customers with quotations
        customers = Customer.query.join(Customer.quotations).distinct().all()
        
        print(f'Found {len(customers)} customers with quotations:')
        print('-' * 80)
        print(f'{"ID":<5} {"Name":<30} {"Email":<30} {"Quotations":<5}')
        print('-' * 80)
        
        for c in customers:
            print(f'{c.id:<5} {c.name[:30]:<30} {c.email[:30] if c.email else "N/A":<30} {len(c.quotations):<5}')
            
        print('-' * 80)
        print(f'Total customers with quotations: {len(customers)}')

def list_customer_quotations(customer_id):
    """List all quotations for a specific customer."""
    with app.app_context():
        customer = Customer.query.get(customer_id)
        if not customer:
            print(f"Customer with ID {customer_id} not found.")
            return False
        
        quotations = Quotation.query.filter_by(customer_id=customer_id).all()
        
        print(f'Quotations for customer: {customer.name} (ID: {customer.id})')
        print('-' * 80)
        print(f'{"ID":<5} {"Number":<15} {"Date":<12} {"Items":<5} {"Total":<10}')
        print('-' * 80)
        
        for q in quotations:
            # Format the date if it exists
            date_str = q.quotation_date.strftime('%Y-%m-%d') if q.quotation_date else 'N/A'
            
            # Format the total amount
            total = f'{q.currency}{q.total_amount:.2f}' if q.total_amount else 'N/A'
            
            print(f'{q.id:<5} {q.quotation_number:<15} {date_str:<12} {len(q.items):<5} {total:<10}')
            
        print('-' * 80)
        print(f'Total quotations: {len(quotations)}')
        return True

def main():
    """Main function for command-line operation."""
    import argparse
    
    parser = argparse.ArgumentParser(description='List quotations for migration planning')
    group = parser.add_mutually_exclusive_group()
    group.add_argument('--all', action='store_true', help='List all quotations')
    group.add_argument('--customers', action='store_true', help='List customers with quotations')
    group.add_argument('--customer-id', type=int, help='List quotations for a specific customer')
    
    args = parser.parse_args()
    
    try:
        if args.customers:
            list_customers()
        elif args.customer_id:
            list_customer_quotations(args.customer_id)
        else:
            # Default behavior: list all quotations
            list_all_quotations()
    except Exception as e:
        print(f"Error: {str(e)}")
        return 1
    
    return 0

if __name__ == '__main__':
    sys.exit(main())
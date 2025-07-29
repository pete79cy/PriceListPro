"""
Customer statistics utility functions.
This module provides functions to calculate statistics for customers.
"""
import logging
from datetime import datetime
from sqlalchemy import func

logger = logging.getLogger(__name__)

def get_customer_stats(customer_id, db):
    """
    Get statistics for a specific customer.
    
    Args:
        customer_id (int): The ID of the customer
        db: SQLAlchemy database instance
        
    Returns:
        dict: A dictionary containing customer statistics
    """
    from models import Customer, Invoice, PriceList
    
    customer = Customer.query.get(customer_id)
    if not customer:
        logger.warning(f"Customer ID {customer_id} not found when calculating statistics")
        return {
            'total_invoices': 0,
            'total_price_lists': 0,
            'last_order_date': None,
            'average_order_value': 0,
            'total_spent': 0
        }
    
    # Get customer invoices
    invoices = customer.invoices
    
    # Calculate statistics
    total_invoices = len(invoices)
    total_price_lists = len(customer.price_lists)
    
    # Calculate last order date
    last_order_date = None
    if invoices:
        invoice_dates = [i.invoice_date for i in invoices if i.invoice_date]
        if invoice_dates:
            last_order_date = max(invoice_dates)
    
    # Calculate average order value and total spent
    total_spent = sum(i.total_amount or 0 for i in invoices)
    average_order_value = total_spent / total_invoices if total_invoices > 0 else 0
    
    return {
        'total_invoices': total_invoices,
        'total_price_lists': total_price_lists,
        'last_order_date': last_order_date,
        'average_order_value': average_order_value,
        'total_spent': total_spent
    }

def get_all_customer_stats(db):
    """
    Get statistics for all customers.
    
    Args:
        db: SQLAlchemy database instance
        
    Returns:
        dict: A dictionary containing overall statistics
    """
    from models import Customer, Invoice, PriceList
    
    # Get all customers
    customers = Customer.query.order_by(Customer.name).all()
    
    # Calculate overall statistics
    total_customers = len(customers)
    total_invoices = 0
    total_order_value = 0
    
    customer_stats = []
    
    for customer in customers:
        stats = get_customer_stats(customer.id, db)
        
        total_invoices += stats['total_invoices']
        total_order_value += stats['total_spent']
        
        customer_stats.append({
            'id': customer.id,
            'name': customer.name,
            'email': customer.email,
            'category': customer.category.name if customer.category else None,
            'total_invoices': stats['total_invoices'],
            'total_price_lists': stats['total_price_lists'],
            'last_order_date': stats['last_order_date'],
            'average_order_value': stats['average_order_value'],
            'total_spent': stats['total_spent']
        })
    
    # Calculate overall average
    average_per_customer = total_order_value / total_customers if total_customers > 0 else 0
    
    return {
        'customer_stats': customer_stats,
        'total_customers': total_customers,
        'total_invoices': total_invoices,
        'total_order_value': total_order_value,
        'average_per_customer': average_per_customer
    }
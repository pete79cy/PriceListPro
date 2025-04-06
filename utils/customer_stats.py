from models import Customer, Invoice, PriceList
from sqlalchemy import func
from datetime import datetime

def get_customer_stats(customer_id):
    """
    Get statistics for a specific customer.
    
    Args:
        customer_id: The ID of the customer to get statistics for
        
    Returns:
        A dictionary containing various statistics about the customer:
        - total_invoices: The total number of invoices for the customer
        - last_invoice_date: The date of the customer's most recent invoice
        - total_spent: The total amount spent by the customer across all invoices
        - product_count: The number of unique products the customer has purchased
        - avg_order_value: The average value of the customer's orders
    """
    # Get customer object
    customer = Customer.query.get(customer_id)
    if not customer:
        return None
    
    # Get invoice statistics
    invoice_stats = {}
    invoice_stats['total_invoices'] = Invoice.query.filter_by(customer_id=customer_id).count()
    
    # Get the last invoice date
    last_invoice = Invoice.query.filter_by(customer_id=customer_id).order_by(Invoice.invoice_date.desc()).first()
    invoice_stats['last_invoice_date'] = last_invoice.invoice_date if last_invoice else None
    
    # Calculate total spent
    invoice_stats['total_spent'] = Invoice.query.with_entities(
        func.sum(Invoice.total_amount)
    ).filter_by(customer_id=customer_id).scalar() or 0
    
    # Get price list statistics
    price_list_stats = {}
    price_list_stats['product_count'] = PriceList.query.filter_by(customer_id=customer_id).count()
    
    # Average order value
    if invoice_stats['total_invoices'] > 0:
        invoice_stats['avg_order_value'] = invoice_stats['total_spent'] / invoice_stats['total_invoices']
    else:
        invoice_stats['avg_order_value'] = 0
    
    # Combine stats
    stats = {
        **invoice_stats,
        **price_list_stats,
        'contact_info': {
            'email': customer.email,
            'phone': customer.phone,
            'address': customer.address
        },
        'updated_at': datetime.utcnow()
    }
    
    return stats


def get_latest_customer_contact(customer_id):
    """
    Get the latest contact record for a customer.
    
    Args:
        customer_id: The ID of the customer
        
    Returns:
        The most recent CustomerContact object for the customer, or None if no contacts exist
    """
    customer = Customer.query.get(customer_id)
    if not customer or not customer.contacts:
        return None
    
    # Contacts are sorted by contact_date in descending order
    return sorted(customer.contacts, key=lambda c: c.contact_date, reverse=True)[0]
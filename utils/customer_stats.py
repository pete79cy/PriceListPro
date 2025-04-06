from datetime import datetime
from models import Customer, Invoice, PriceList

def get_customer_stats(customer_id):
    """
    Get statistics about a customer's interactions and orders.
    
    Args:
        customer_id (int): The ID of the customer to get stats for
        
    Returns:
        dict: A dictionary containing various statistics about the customer
    """
    customer = Customer.query.get(customer_id)
    if not customer:
        return {}

    invoices = customer.invoices
    price_lists = customer.price_lists
    
    # Calculate last order date
    last_order_date = None
    if invoices:
        last_order_date = max([i.invoice_date for i in invoices])
    
    # Calculate average order value
    average_order_value = 0
    if invoices and len(invoices) > 0:
        total_value = sum([i.total_amount for i in invoices if i.total_amount is not None])
        valid_invoices = sum(1 for i in invoices if i.total_amount is not None)
        if valid_invoices > 0:
            average_order_value = total_value / valid_invoices
    
    # Get contact history
    contacts = customer.contacts
    last_contact = None
    if contacts:
        last_contact = max([c.contact_date for c in contacts])
    
    return {
        'total_invoices': len(invoices),
        'total_price_lists': len(price_lists),
        'last_order_date': last_order_date,
        'average_order_value': average_order_value,
        'last_contact_date': last_contact,
        'contact_count': len(contacts) if contacts else 0,
        'category': customer.category.name if customer.category else None,
    }
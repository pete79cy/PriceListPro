"""
Daily Orders Helper Utilities

This module provides helper functions for the Daily Orders feature to ensure
proper data handling, validation, and error management.
"""

from decimal import Decimal, ROUND_HALF_UP
from functools import wraps
from flask import current_app
from app import db
from models import OrderStatusEnum


def to_decimal(value):
    """
    Convert a value to Decimal for precise money calculations.
    
    Args:
        value: The value to convert (float, int, string, or None)
        
    Returns:
        Decimal: The value as a Decimal, or None if input is None
    """
    if value is None:
        return None
    return Decimal(str(value)).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)


def validate_order_item_data(item_data):
    """
    Validate order item data for proper types and values.
    
    Args:
        item_data: Dictionary containing item data
        
    Returns:
        tuple: (is_valid, error_message, cleaned_data)
    """
    try:
        # Extract and validate required fields
        plant_name = item_data.get('plant_name', '').strip()
        if not plant_name:
            return False, "Plant name is required", None
            
        # Validate quantity
        quantity = item_data.get('quantity')
        if quantity is None:
            return False, "Quantity is required", None
        try:
            quantity = int(quantity)
            if quantity <= 0:
                return False, "Quantity must be greater than 0", None
        except (ValueError, TypeError):
            return False, "Invalid quantity format", None
            
        # Validate price
        price = item_data.get('price')
        if price is None:
            return False, "Price is required", None
        try:
            price = to_decimal(price)
            if price < 0:
                return False, "Price cannot be negative", None
        except (ValueError, TypeError):
            return False, "Invalid price format", None
            
        # Validate VAT rate
        vat_rate = item_data.get('vat_rate', 19.0)
        try:
            vat_rate = to_decimal(vat_rate)
            if vat_rate < 0 or vat_rate > 100:
                return False, "VAT rate must be between 0 and 100", None
        except (ValueError, TypeError):
            return False, "Invalid VAT rate format", None
            
        # Return cleaned data
        cleaned_data = {
            'plant_name': plant_name,
            'size': item_data.get('size', '').strip(),
            'quantity': quantity,
            'price': price,
            'vat_rate': vat_rate,
            'notes': item_data.get('notes', '').strip(),
            'product_id': item_data.get('product_id'),
            'price_list_id': item_data.get('price_list_id')
        }
        
        return True, None, cleaned_data
        
    except Exception as e:
        current_app.logger.error(f"Error validating order item data: {str(e)}")
        return False, "Invalid data format", None


def validate_status_transition(current_status, new_status):
    """
    Validate if a status transition is allowed.
    
    Args:
        current_status: Current order status string
        new_status: Desired new status string
        
    Returns:
        tuple: (is_valid, error_message)
    """
    try:
        # Convert strings to enums
        current_enum = OrderStatusEnum(current_status)
        new_enum = OrderStatusEnum(new_status)
        
        # Allow staying in the same status
        if current_enum == new_enum:
            return True, None
            
        # Import transitions from models
        from models import ORDER_STATUS_TRANSITIONS
        
        # Check if transition is allowed
        allowed_transitions = ORDER_STATUS_TRANSITIONS.get(current_enum, [])
        if new_enum in allowed_transitions:
            return True, None
        else:
            return False, f"Cannot transition from {current_status} to {new_status}"
            
    except ValueError as e:
        return False, f"Invalid status value: {str(e)}"
    except Exception as e:
        current_app.logger.error(f"Error validating status transition: {str(e)}")
        return False, "Status validation error"


def log_exceptions(fn):
    """
    Decorator to log exceptions and handle database rollbacks.
    
    Args:
        fn: Function to wrap
        
    Returns:
        function: Wrapped function with exception handling
    """
    @wraps(fn)
    def wrapper(*args, **kwargs):
        try:
            return fn(*args, **kwargs)
        except Exception as e:
            current_app.logger.exception(f"Error in {fn.__name__}: {str(e)}")
            try:
                db.session.rollback()
            except Exception:
                pass  # Rollback already happened or session is invalid
            raise
    return wrapper


def calculate_order_totals(order_items):
    """
    Calculate order totals with precise decimal arithmetic.
    
    Args:
        order_items: List of order items (can be model instances or dicts)
        
    Returns:
        dict: Dictionary containing subtotal, vat_breakdown, total_vat, grand_total
    """
    subtotal = Decimal('0.00')
    vat_breakdown = {}
    
    for item in order_items:
        # Handle both model instances and dictionaries
        if hasattr(item, 'quantity'):
            quantity = Decimal(str(item.quantity))
            price = to_decimal(item.price)
            vat_rate = to_decimal(item.vat_rate)
        else:
            quantity = Decimal(str(item.get('quantity', 0)))
            price = to_decimal(item.get('price', 0))
            vat_rate = to_decimal(item.get('vat_rate', 19))
            
        # Calculate item subtotal
        item_subtotal = quantity * price
        subtotal += item_subtotal
        
        # Calculate VAT for this item
        vat_amount = (item_subtotal * vat_rate / Decimal('100')).quantize(
            Decimal('0.01'), rounding=ROUND_HALF_UP
        )
        
        # Accumulate VAT by rate
        if vat_rate in vat_breakdown:
            vat_breakdown[vat_rate] += vat_amount
        else:
            vat_breakdown[vat_rate] = vat_amount
    
    # Calculate total VAT and grand total
    total_vat = sum(vat_breakdown.values(), Decimal('0.00'))
    grand_total = subtotal + total_vat
    
    return {
        'subtotal': subtotal,
        'vat_breakdown': vat_breakdown,
        'total_vat': total_vat,
        'grand_total': grand_total
    }


def format_currency(amount, currency_symbol='€'):
    """
    Format a Decimal amount as currency string.
    
    Args:
        amount: Decimal amount to format
        currency_symbol: Currency symbol to use
        
    Returns:
        str: Formatted currency string
    """
    if amount is None:
        return f"{currency_symbol}0.00"
    
    if isinstance(amount, (int, float)):
        amount = to_decimal(amount)
    
    return f"{currency_symbol}{amount:.2f}"


def update_customer_price_list_safe(customer_id, product_id, price, commit=False):
    """
    Safely update customer price list with proper error handling.
    
    Args:
        customer_id: ID of the customer
        product_id: ID of the product
        price: New price (will be converted to Decimal)
        commit: Whether to commit the transaction
        
    Returns:
        tuple: (success, error_message)
    """
    try:
        from models import PriceList, PriceListItem, Customer, Product
        
        # Validate inputs
        if not customer_id or not product_id:
            return False, "Customer ID and Product ID are required"
        
        price_decimal = to_decimal(price)
        if price_decimal is None or price_decimal < 0:
            return False, "Invalid price value"
        
        # Get or create price list for customer
        price_list = PriceList.query.filter_by(customer_id=customer_id).first()
        if not price_list:
            customer = Customer.query.get(customer_id)
            if not customer:
                return False, "Customer not found"
            
            price_list = PriceList(
                customer_id=customer_id,
                name=f"{customer.name} Price List"
            )
            db.session.add(price_list)
            db.session.flush()  # Get the ID
        
        # Get or create price list item
        price_item = PriceListItem.query.filter_by(
            price_list_id=price_list.id,
            product_id=product_id
        ).first()
        
        if price_item:
            price_item.price = float(price_decimal)  # Store as float for now
            price_item.updated_at = db.func.now()
        else:
            product = Product.query.get(product_id)
            if not product:
                return False, "Product not found"
            
            price_item = PriceListItem(
                price_list_id=price_list.id,
                product_id=product_id,
                name=product.name,
                size=getattr(product, 'size', ''),
                price=float(price_decimal)  # Store as float for now
            )
            db.session.add(price_item)
        
        if commit:
            db.session.commit()
        
        return True, None
        
    except Exception as e:
        current_app.logger.error(f"Error updating customer price list: {str(e)}")
        if commit:
            db.session.rollback()
        return False, f"Error updating price list: {str(e)}"
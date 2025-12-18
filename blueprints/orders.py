from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required, current_user
from datetime import datetime, date
import json

from app import db
from models import Customer, Product, Order, OrderItem, PriceList, PriceListItem, OrderStatus, ORDER_STATUS_COLORS
from utils.translations import translate_to_language
from utils.pdf_generator import generate_delivery_note_pdf

# Create the blueprint
orders_bp = Blueprint('orders', __name__, url_prefix='/orders')

# Global variables to store translated status labels
TRANSLATED_STATUS_LABELS = {}

# Routes for daily orders

@orders_bp.route('/')
@login_required
def index():
    """Order dashboard page"""
    # Get all orders with sorting by date (most recent first)
    orders = Order.query.order_by(Order.created_at.desc()).all()
    
    # Get counts for status filter badges
    status_counts = {}
    for status in OrderStatus:
        count = Order.query.filter_by(status=status.value).count()
        status_counts[status.value] = count
    
    # Get distinct customers for filter
    customers = Customer.query.order_by(Customer.name).all()
    
    # Get today's delivery orders
    today = date.today()
    today_deliveries = Order.query.filter(Order.delivery_date == today).all()
    
    return render_template('orders/index_new.html', 
                           orders=orders,
                           status_counts=status_counts,
                           customers=customers,
                           today_deliveries=today_deliveries,
                           OrderStatus=OrderStatus,
                           ORDER_STATUS_COLORS=ORDER_STATUS_COLORS)

@orders_bp.route('/new', methods=['GET', 'POST'])
@login_required
def new_order():
    """Create a new order"""
    if request.method == 'POST':
        # Extract form data
        customer_id = request.form.get('customer_id')
        delivery_date_str = request.form.get('delivery_date')
        notes = request.form.get('notes')
        
        # Basic validation
        if not customer_id:
            flash('Customer is required', 'danger')
            return redirect(url_for('orders.new_order'))
            
        # Convert delivery date string to date object if provided
        delivery_date = None
        if delivery_date_str and delivery_date_str.strip():
            try:
                delivery_date = datetime.strptime(delivery_date_str, '%Y-%m-%d').date()
            except ValueError:
                flash('Invalid delivery date format', 'danger')
                return redirect(url_for('orders.new_order'))
        
        # Generate a unique order number (based on date and sequential numbering)
        today = date.today()
        # Count orders from today to determine the daily sequence number
        daily_order_count = Order.query.filter(
            db.func.date(Order.created_at) == today
        ).count()
        
        # Format: ORD-YYYYMMDD-XXX where XXX is the sequence number
        order_number = f"ORD-{today.strftime('%Y%m%d')}-{daily_order_count + 1:03d}"
        
        # Create new order
        order = Order(
            customer_id=customer_id,
            order_number=order_number,
            status="new",  # Default status is NEW
            delivery_date=delivery_date,
            notes=notes
        )
        
        db.session.add(order)
        db.session.commit()
        
        flash(f'Order {order_number} created successfully', 'success')
        return redirect(url_for('orders.view_order', order_id=order.id))
    
    # GET request - display the form
    customers = Customer.query.order_by(Customer.name).all()
    return render_template('orders/new.html', customers=customers)

@orders_bp.route('/<int:order_id>')
@login_required
def view_order(order_id):
    """View a single order"""
    order = Order.query.get_or_404(order_id)
    products = Product.query.order_by(Product.name).all()
    
    # Get all available statuses for the status transition dropdown
    available_statuses = []
    current_status = order.status
    
    # Convert string status to enum for transitions lookup
    try:
        from models import ORDER_STATUS_TRANSITIONS
        current_status_enum = OrderStatus(current_status)
        # Add current status and all available transitions
        available_statuses = [current_status_enum] + list(ORDER_STATUS_TRANSITIONS.get(current_status_enum, []))
    except ValueError:
        # If invalid status, just show all statuses as available
        available_statuses = list(OrderStatus)
    
    return render_template('orders/view.html', 
                           order=order, 
                           products=products,
                           available_statuses=available_statuses)

@orders_bp.route('/<int:order_id>/update-status', methods=['POST'])
@login_required
def update_status(order_id):
    """Update the status of an order"""
    order = Order.query.get_or_404(order_id)
    new_status = request.form.get('status')
    
    if not new_status:
        flash('Status is required', 'danger')
        return redirect(url_for('orders.view_order', order_id=order.id))
    
    # Check if the requested status transition is valid
    if not order.transition_to(new_status):
        flash(f'Cannot transition from {order.status} to {new_status}', 'danger')
        return redirect(url_for('orders.view_order', order_id=order.id))
    
    db.session.commit()
    flash('Order status updated successfully', 'success')
    return redirect(url_for('orders.view_order', order_id=order.id))

@orders_bp.route('/<int:order_id>/add-item', methods=['POST'])
@login_required
def add_item(order_id):
    """Add a product to an order"""
    order = Order.query.get_or_404(order_id)
    
    # Extract form data
    product_id = request.form.get('product_id')
    quantity = request.form.get('quantity', type=float)
    unit_price = request.form.get('unit_price', type=float)
    
    # Basic validation
    if not product_id or not quantity:
        flash('Product and quantity are required', 'danger')
        return redirect(url_for('orders.view_order', order_id=order.id))
    
    product = Product.query.get_or_404(product_id)
    
    # If unit price wasn't provided, look it up from customer's price list
    if not unit_price:
        # Try to find this product in the customer's price list
        price_list_item = PriceListItem.query.join(PriceList).filter(
            PriceList.customer_id == order.customer_id,
            PriceListItem.product_id == product_id
        ).first()
        
        if price_list_item:
            unit_price = price_list_item.price
        else:
            # Fall back to product's standard price
            unit_price = product.standard_price or 0
    
    # Create the order item
    order_item = OrderItem(
        order_id=order.id,
        product_id=product_id,
        quantity=quantity,
        unit_price=unit_price
    )
    
    db.session.add(order_item)
    
    # Update customer's price list with this price if it's different
    update_customer_price_list(order.customer_id, product_id, unit_price)
    
    db.session.commit()
    flash('Item added to order', 'success')
    return redirect(url_for('orders.view_order', order_id=order.id))

@orders_bp.route('/<int:order_id>/remove-item/<int:item_id>', methods=['POST'])
@login_required
def remove_item(order_id, item_id):
    """Remove an item from an order"""
    order = Order.query.get_or_404(order_id)
    item = OrderItem.query.get_or_404(item_id)
    
    # Verify the item belongs to this order
    if item.order_id != order.id:
        flash('Item does not belong to this order', 'danger')
        return redirect(url_for('orders.view_order', order_id=order.id))
    
    db.session.delete(item)
    db.session.commit()
    
    flash('Item removed from order', 'success')
    return redirect(url_for('orders.view_order', order_id=order.id))

@orders_bp.route('/<int:order_id>/update-item/<int:item_id>', methods=['POST'])
@login_required
def update_item(order_id, item_id):
    """Update an item in an order"""
    order = Order.query.get_or_404(order_id)
    item = OrderItem.query.get_or_404(item_id)
    
    # Verify the item belongs to this order
    if item.order_id != order.id:
        flash('Item does not belong to this order', 'danger')
        return redirect(url_for('orders.view_order', order_id=order.id))
    
    # Extract form data
    quantity = request.form.get('quantity', type=float)
    unit_price = request.form.get('unit_price', type=float)
    
    # Basic validation
    if not quantity or not unit_price:
        flash('Quantity and unit price are required', 'danger')
        return redirect(url_for('orders.view_order', order_id=order.id))
    
    # Update item
    item.quantity = quantity
    item.unit_price = unit_price
    
    # Update customer's price list with the new price
    update_customer_price_list(order.customer_id, item.product_id, unit_price)
    
    db.session.commit()
    flash('Item updated', 'success')
    return redirect(url_for('orders.view_order', order_id=order.id))

@orders_bp.route('/<int:order_id>/print-delivery-note', methods=['GET'])
@login_required
def print_delivery_note(order_id):
    """Generate PDF delivery note"""
    order = Order.query.get_or_404(order_id)
    
    # Get requested language (default to English)
    language = request.args.get('language', 'en')
    
    # Generate the PDF
    pdf_data = generate_delivery_note_pdf(order, language)
    
    # Define filename for download
    filename = f"delivery_note_{order.order_number}.pdf"
    
    # Return the PDF as download
    from flask import send_file
    import io
    return send_file(
        io.BytesIO(pdf_data),
        mimetype='application/pdf',
        as_attachment=True,
        download_name=filename
    )

def update_customer_price_list(customer_id, product_id, new_price):
    """
    Update a customer's price list with the new price for a product.
    If the product doesn't exist in their price list, add it.
    """
    # Look for existing price list or create a new one
    price_list = PriceList.query.filter_by(customer_id=customer_id).first()
    if not price_list:
        # Create a new price list for this customer
        price_list = PriceList(
            customer_id=customer_id,
            name=f"Price List for Customer #{customer_id}",
            is_active=True
        )
        db.session.add(price_list)
        db.session.flush()  # Get the ID without committing
    
    # Look for existing price list item
    price_list_item = PriceListItem.query.filter_by(
        price_list_id=price_list.id, 
        product_id=product_id
    ).first()
    
    if price_list_item:
        # Update existing price if it's different
        if price_list_item.price != new_price:
            price_list_item.price = new_price
            price_list_item.updated_at = datetime.utcnow()
    else:
        # Add new price list item
        price_list_item = PriceListItem(
            price_list_id=price_list.id,
            product_id=product_id,
            price=new_price
        )
        db.session.add(price_list_item)
"""
Orders Blueprint - Handles all routes related to daily orders management
"""
from datetime import datetime, timedelta
import os
from io import BytesIO

from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify, send_file
from flask_login import login_required, current_user
from sqlalchemy import desc
from werkzeug.utils import secure_filename

from app import db
from models import Order, OrderItem, OrderStatus, Customer, Product, PriceList, PriceListItem
from utils.pdf_generator import generate_pdf
from utils.translations import get_translations

# Initialize blueprint
orders = Blueprint('orders', __name__, url_prefix='/orders')

# Helper functions
def get_status_choices():
    """Get a list of order status options for forms"""
    return [(status.name, status.value['label']) for status in OrderStatus]

def get_status_colors():
    """Get a dictionary of status colors for UI rendering"""
    return {status.name: status.value['color'] for status in OrderStatus}

def generate_order_number():
    """Generate a unique order number with format ORD-YYYY-XXX"""
    year = datetime.now().year
    latest_order = Order.query.filter(
        Order.order_number.like(f"ORD-{year}-%")
    ).order_by(desc(Order.order_number)).first()
    
    if latest_order:
        try:
            # Extract the numerical part from the latest order number
            latest_number = int(latest_order.order_number.split('-')[-1])
            new_number = latest_number + 1
        except (ValueError, IndexError):
            # If parsing fails, start from 1
            new_number = 1
    else:
        new_number = 1
    
    return f"ORD-{year}-{new_number:03d}"

def get_default_delivery_date():
    """Return tomorrow's date as the default delivery date"""
    return datetime.now().date() + timedelta(days=1)

def can_cancel_order(order):
    """Check if an order can be cancelled"""
    return order.status != OrderStatus.DELIVERED and order.status != OrderStatus.CANCELLED

# Routes
@orders.route('/')
@login_required
def index():
    """Orders dashboard view"""
    # Get filter parameters
    status_filter = request.args.get('status')
    customer_filter = request.args.get('customer_id')
    date_from = request.args.get('date_from')
    date_to = request.args.get('date_to')
    
    # Base query
    query = Order.query
    
    # Apply filters
    if status_filter:
        query = query.filter(Order.status == OrderStatus[status_filter])
    
    if customer_filter:
        query = query.filter(Order.customer_id == customer_filter)
    
    if date_from:
        try:
            date_from_obj = datetime.strptime(date_from, '%Y-%m-%d').date()
            query = query.filter(Order.delivery_date >= date_from_obj)
        except ValueError:
            flash('Invalid from date format. Please use YYYY-MM-DD.', 'warning')
    
    if date_to:
        try:
            date_to_obj = datetime.strptime(date_to, '%Y-%m-%d').date()
            query = query.filter(Order.delivery_date <= date_to_obj)
        except ValueError:
            flash('Invalid to date format. Please use YYYY-MM-DD.', 'warning')
    
    # Get orders, sorted by newest first
    orders_list = query.order_by(desc(Order.created_at)).all()
    
    # Get customers for filter dropdown
    customers = Customer.query.order_by(Customer.name).all()
    
    # Prepare data for calendar view (upcoming deliveries)
    today = datetime.now().date()
    upcoming_week = [today + timedelta(days=i) for i in range(7)]
    
    upcoming_deliveries = {}
    for day in upcoming_week:
        day_str = day.strftime('%Y-%m-%d')
        upcoming_deliveries[day_str] = Order.query.filter(
            Order.delivery_date == day,
            Order.status != OrderStatus.CANCELLED
        ).all()
    
    return render_template(
        'orders/index.html',
        orders=orders_list,
        customers=customers,
        statuses=OrderStatus,
        status_filter=status_filter,
        customer_filter=customer_filter,
        date_from=date_from,
        date_to=date_to,
        upcoming_deliveries=upcoming_deliveries,
        upcoming_week=upcoming_week,
        today=today
    )

@orders.route('/new', methods=['GET', 'POST'])
@login_required
def new_order():
    """Create a new order"""
    if request.method == 'POST':
        customer_id = request.form.get('customer_id')
        delivery_date_str = request.form.get('delivery_date')
        notes = request.form.get('notes')
        
        # Validate customer
        if not customer_id:
            flash('Customer is required.', 'danger')
            return redirect(url_for('orders.new_order'))
        
        # Parse delivery date if provided
        delivery_date = None
        if delivery_date_str:
            try:
                delivery_date = datetime.strptime(delivery_date_str, '%Y-%m-%d').date()
            except ValueError:
                flash('Invalid delivery date format.', 'warning')
                return redirect(url_for('orders.new_order'))
        
        # Create the order
        order = Order(
            order_number=generate_order_number(),
            customer_id=customer_id,
            delivery_date=delivery_date,
            notes=notes,
            status=OrderStatus.NEW
        )
        
        db.session.add(order)
        db.session.commit()
        
        flash(f'Order {order.order_number} created successfully.', 'success')
        return redirect(url_for('orders.view', order_id=order.id))
    
    # GET request - show the new order form
    customers = Customer.query.order_by(Customer.name).all()
    return render_template(
        'orders/new.html',
        customers=customers,
        default_delivery_date=get_default_delivery_date().strftime('%Y-%m-%d')
    )

@orders.route('/<int:order_id>')
@login_required
def view(order_id):
    """View a specific order"""
    order = Order.query.get_or_404(order_id)
    products = Product.query.order_by(Product.name).all()
    return render_template('orders/view.html', order=order, products=products, OrderStatus=OrderStatus)

@orders.route('/<int:order_id>/edit', methods=['POST'])
@login_required
def edit_order(order_id):
    """Edit order details"""
    order = Order.query.get_or_404(order_id)
    
    # Update order details
    delivery_date_str = request.form.get('delivery_date')
    notes = request.form.get('notes')
    
    # Parse delivery date if provided
    if delivery_date_str:
        try:
            order.delivery_date = datetime.strptime(delivery_date_str, '%Y-%m-%d').date()
        except ValueError:
            flash('Invalid delivery date format.', 'warning')
            return redirect(url_for('orders.view', order_id=order.id))
    else:
        order.delivery_date = None
    
    order.notes = notes
    db.session.commit()
    
    flash('Order details updated successfully.', 'success')
    return redirect(url_for('orders.view', order_id=order.id))

@orders.route('/<int:order_id>/status', methods=['POST'])
@login_required
def update_status(order_id):
    """Update order status"""
    order = Order.query.get_or_404(order_id)
    status_name = request.form.get('status')
    
    if not status_name or status_name not in [s.name for s in OrderStatus]:
        flash('Invalid status.', 'danger')
        return redirect(url_for('orders.view', order_id=order.id))
    
    new_status = OrderStatus[status_name]
    
    # Check if status transition is allowed
    if not order.can_transition_to(new_status):
        flash(f'Cannot change status from {order.get_status_label()} to {new_status.value["label"]}.', 'danger')
        return redirect(url_for('orders.view', order_id=order.id))
    
    # Update status
    order.status = new_status
    db.session.commit()
    
    flash(f'Order status updated to {new_status.value["label"]}.', 'success')
    return redirect(url_for('orders.view', order_id=order.id))

@orders.route('/<int:order_id>/add-item', methods=['POST'])
@login_required
def add_item(order_id):
    """Add an item to an order"""
    order = Order.query.get_or_404(order_id)
    
    # Get form data
    product_id = request.form.get('product_id')
    plant_name = request.form.get('plant_name')
    size = request.form.get('size')
    quantity = request.form.get('quantity')
    price = request.form.get('price')
    notes = request.form.get('notes')
    update_price_list = 'update_price_list' in request.form
    
    # Validate required fields
    if not plant_name or not quantity or not price:
        flash('Plant name, quantity, and price are required.', 'danger')
        return redirect(url_for('orders.view', order_id=order.id))
    
    try:
        quantity = int(quantity)
        price = float(price)
    except ValueError:
        flash('Quantity must be a whole number and price must be a decimal number.', 'danger')
        return redirect(url_for('orders.view', order_id=order.id))
    
    # Create order item
    item = OrderItem(
        order_id=order.id,
        plant_name=plant_name,
        size=size,
        quantity=quantity,
        price=price,
        notes=notes,
        product_id=product_id if product_id else None
    )
    
    db.session.add(item)
    
    # Update or create price list item if requested
    if update_price_list:
        # Get or create a price list for this customer
        price_list = PriceList.query.filter_by(
            customer_id=order.customer_id,
            is_active=True
        ).first()
        
        if not price_list:
            price_list = PriceList(
                customer_id=order.customer_id,
                name=f"{order.customer.name} Price List",
                is_active=True
            )
            db.session.add(price_list)
            db.session.flush()  # Get ID without committing yet
        
        # Check if this plant exists in the price list
        existing_item = None
        if product_id:
            existing_item = PriceListItem.query.filter_by(
                price_list_id=price_list.id,
                product_id=product_id
            ).first()
        else:
            # Search by name and size if no product_id
            existing_item = PriceListItem.query.filter_by(
                price_list_id=price_list.id,
                plant_name=plant_name,
                size=size
            ).first()
        
        if existing_item:
            # Update existing price
            existing_item.price = price
            existing_item.updated_at = datetime.now()
        else:
            # Create new price list item
            price_list_item = PriceListItem(
                price_list_id=price_list.id,
                product_id=product_id if product_id else None,
                plant_name=plant_name,
                size=size,
                price=price
            )
            db.session.add(price_list_item)
        
        # Mark this item as having updated the price list
        item.updated_price_list = True
    
    db.session.commit()
    
    flash('Item added to order.', 'success')
    return redirect(url_for('orders.view', order_id=order.id))

@orders.route('/<int:order_id>/remove-item/<int:item_id>', methods=['POST'])
@login_required
def remove_item(order_id, item_id):
    """Remove an item from an order"""
    order = Order.query.get_or_404(order_id)
    item = OrderItem.query.get_or_404(item_id)
    
    # Ensure item belongs to this order
    if item.order_id != order.id:
        flash('Item does not belong to this order.', 'danger')
        return redirect(url_for('orders.view', order_id=order.id))
    
    db.session.delete(item)
    db.session.commit()
    
    flash('Item removed from order.', 'success')
    return redirect(url_for('orders.view', order_id=order.id))

@orders.route('/product/<int:product_id>')
@login_required
def get_product(product_id):
    """Get product details as JSON"""
    product = Product.query.get_or_404(product_id)
    customer_id = request.args.get('customer_id')
    price = product.price  # Default to product's standard price
    
    # Check if there's a special price for this customer
    if customer_id:
        price_list = PriceList.query.filter_by(
            customer_id=customer_id,
            is_active=True
        ).first()
        
        if price_list:
            price_list_item = PriceListItem.query.filter_by(
                price_list_id=price_list.id,
                product_id=product_id
            ).first()
            
            if price_list_item:
                price = price_list_item.price
    
    return jsonify({
        'id': product.id,
        'name': product.name,
        'size': product.size,
        'price': price
    })

@orders.route('/<int:order_id>/delivery-notes')
@login_required
def delivery_notes(order_id):
    """View delivery notes in HTML"""
    order = Order.query.get_or_404(order_id)
    language = request.args.get('language', 'en')
    
    # Apply translations based on selected language
    translations = get_translations(language)
    
    return render_template(
        'pdfs/delivery_note.html',
        order=order,
        language=language,
        _=translations.gettext  # Translation function
    )

@orders.route('/<int:order_id>/delivery-notes-pdf')
@login_required
def pdf_delivery_notes(order_id):
    """Generate and download PDF delivery notes"""
    order = Order.query.get_or_404(order_id)
    language = request.args.get('language', 'en')
    
    # Apply translations based on selected language
    translations = get_translations(language)
    
    # Generate HTML with translations
    html = render_template(
        'pdfs/delivery_note.html',
        order=order,
        language=language,
        _=translations.gettext  # Translation function
    )
    
    # Generate PDF
    pdf_file = generate_pdf(html)
    
    # Create a response with the PDF
    filename = f"delivery_note_{order.order_number}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
    
    return send_file(
        BytesIO(pdf_file),
        download_name=filename,
        as_attachment=True,
        mimetype='application/pdf'
    )
"""
Orders Blueprint - Handles all order-related routes and functionality.

This blueprint provides routes for:
- Order dashboard
- Creating new orders
- Viewing and updating existing orders
- Generating delivery notes
- Calendar view for upcoming deliveries
"""
import os
import json
from datetime import datetime, date, timedelta
from collections import defaultdict
from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify, abort, current_app
from flask_login import login_required, current_user
from sqlalchemy import desc, and_, or_, func
from werkzeug.utils import secure_filename

from app import db
from models import Order, OrderItem, Customer, Product, PriceList, OrderStatus
from utils.pdf_generator import generate_delivery_note_pdf

# Create the blueprint
orders = Blueprint('orders', __name__)

# Helper functions
def generate_order_number():
    """Generate a unique order number with format 'ORD-YYYY-XXXX'"""
    year = date.today().year
    # Get the last order number for this year
    last_order = Order.query.filter(
        Order.order_number.like(f'ORD-{year}-%')
    ).order_by(desc(Order.order_number)).first()
    
    if last_order:
        # Extract the sequence number from the last order
        try:
            seq_num = int(last_order.order_number.split('-')[-1])
            next_seq_num = seq_num + 1
        except ValueError:
            next_seq_num = 1
    else:
        next_seq_num = 1
    
    # Format with 4 digits padding
    return f'ORD-{year}-{next_seq_num:04d}'

def update_price_list(customer_id, product_id, plant_name, size, price):
    """
    Update or create a price list entry for a customer/product.
    
    Args:
        customer_id: The customer ID
        product_id: The product ID (or None if not linked to a product)
        plant_name: Name of the plant
        size: Size or pot size
        price: The price to set
        
    Returns:
        PriceList: The created or updated price list object
    """
    # If no product_id, try to find an existing product or create one
    if not product_id:
        # Look for a product with the same name and pot size
        product = Product.query.filter(
            func.lower(Product.name) == func.lower(plant_name)
        ).filter(
            func.lower(Product.pot) == func.lower(size) if size else Product.pot.is_(None)
        ).first()
        
        if product:
            product_id = product.id
        else:
            # Create a new product
            product = Product(
                name=plant_name,
                pot=size
            )
            db.session.add(product)
            db.session.flush()  # Get the ID without committing
            product_id = product.id
    
    # Check if a price list entry already exists
    price_list = None
    if product_id:
        price_list = PriceList.query.filter_by(
            customer_id=customer_id,
            product_id=product_id
        ).first()
    
    if price_list:
        # Update existing price list
        price_list.price = price
        price_list.effective_date = date.today()
    else:
        # Create new price list entry
        price_list = PriceList(
            customer_id=customer_id,
            product_id=product_id,
            price=price,
            effective_date=date.today()
        )
        db.session.add(price_list)
    
    return price_list

# Routes

@orders.route('/')
@login_required
def index():
    """Orders dashboard with overview and stats"""
    # Get stats
    total_orders = Order.query.count()
    new_orders = Order.query.filter_by(status=OrderStatus.NEW).count()
    preparing_orders = Order.query.filter_by(status=OrderStatus.PREPARING).count()
    ready_orders = Order.query.filter_by(status=OrderStatus.READY).count()
    
    # Get orders due today
    today = date.today()
    orders_due_today = Order.query.filter(
        Order.delivery_date == today,
        Order.status != OrderStatus.DELIVERED
    ).order_by(Order.updated_at.desc()).all()
    
    # Get orders due tomorrow
    tomorrow = today + timedelta(days=1)
    orders_due_tomorrow = Order.query.filter(
        Order.delivery_date == tomorrow,
        Order.status != OrderStatus.DELIVERED
    ).order_by(Order.updated_at.desc()).all()
    
    # Get recent orders
    recent_orders = Order.query.order_by(Order.created_at.desc()).limit(10).all()
    
    return render_template(
        'orders/index.html',
        total_orders=total_orders,
        new_orders=new_orders,
        preparing_orders=preparing_orders,
        ready_orders=ready_orders,
        orders_due_today=orders_due_today,
        orders_due_tomorrow=orders_due_tomorrow,
        recent_orders=recent_orders
    )

@orders.route('/new', methods=['GET', 'POST'])
@login_required
def new_order():
    """Create a new order"""
    if request.method == 'POST':
        try:
            # Get form data
            customer_id = request.form.get('customer_id')
            delivery_date_str = request.form.get('delivery_date')
            notes = request.form.get('notes')
            items_data = json.loads(request.form.get('items_data', '[]'))
            
            if not customer_id:
                flash('Customer is required', 'danger')
                return redirect(url_for('orders.new_order'))
            
            if not items_data:
                flash('At least one item is required', 'danger')
                return redirect(url_for('orders.new_order'))
            
            # Parse delivery date
            delivery_date = None
            if delivery_date_str:
                try:
                    delivery_date = datetime.strptime(delivery_date_str, '%Y-%m-%d').date()
                except ValueError:
                    flash('Invalid delivery date format', 'danger')
                    return redirect(url_for('orders.new_order'))
            
            # Create new order
            order = Order(
                customer_id=customer_id,
                order_number=generate_order_number(),
                status=OrderStatus.NEW,
                delivery_date=delivery_date,
                notes=notes
            )
            db.session.add(order)
            db.session.flush()  # Get the order ID without committing
            
            # Process order items
            for item_data in items_data:
                product_id = item_data.get('product_id') or None
                plant_name = item_data.get('plant_name')
                size = item_data.get('size')
                quantity = int(item_data.get('quantity', 1))
                price = float(item_data.get('price', 0))
                notes = item_data.get('notes')
                
                if not plant_name:
                    continue  # Skip blank items
                
                # Create new order item
                order_item = OrderItem(
                    order_id=order.id,
                    product_id=product_id,
                    plant_name=plant_name,
                    size=size,
                    quantity=quantity,
                    price=price,
                    notes=notes
                )
                db.session.add(order_item)
                
                # Update price list
                price_list = update_price_list(
                    customer_id=customer_id,
                    product_id=product_id,
                    plant_name=plant_name,
                    size=size,
                    price=price
                )
                
                # Link order item to price list
                if price_list:
                    order_item.price_list_id = price_list.id
                    order_item.updated_price_list = True
            
            db.session.commit()
            flash(f'Order {order.order_number} created successfully', 'success')
            return redirect(url_for('orders.view_order', order_id=order.id))
            
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Error creating order: {str(e)}")
            flash(f'Error creating order: {str(e)}', 'danger')
            return redirect(url_for('orders.new_order'))
    
    # GET method - show form
    customers = Customer.query.order_by(Customer.name).all()
    products = Product.query.order_by(Product.name).all()
    today = date.today().strftime('%Y-%m-%d')
    
    return render_template(
        'orders/new.html',
        customers=customers,
        products=products,
        today=today
    )

@orders.route('/view/<int:order_id>')
@login_required
def view_order(order_id):
    """View a specific order"""
    order = Order.query.get_or_404(order_id)
    return render_template('orders/view.html', order=order)

@orders.route('/edit/<int:order_id>', methods=['GET', 'POST'])
@login_required
def edit_order(order_id):
    """Edit an existing order"""
    order = Order.query.get_or_404(order_id)
    
    if request.method == 'POST':
        try:
            # Get form data
            delivery_date_str = request.form.get('delivery_date')
            notes = request.form.get('notes')
            items_data = json.loads(request.form.get('items_data', '[]'))
            
            if not items_data:
                flash('At least one item is required', 'danger')
                return redirect(url_for('orders.edit_order', order_id=order.id))
            
            # Parse delivery date
            if delivery_date_str:
                try:
                    order.delivery_date = datetime.strptime(delivery_date_str, '%Y-%m-%d').date()
                except ValueError:
                    flash('Invalid delivery date format', 'danger')
                    return redirect(url_for('orders.edit_order', order_id=order.id))
            else:
                order.delivery_date = None
            
            # Update order data
            order.notes = notes
            
            # Keep track of processed items to delete removed ones
            processed_item_ids = []
            
            # Process order items
            for item_data in items_data:
                item_id = item_data.get('id')
                product_id = item_data.get('product_id') or None
                plant_name = item_data.get('plant_name')
                size = item_data.get('size')
                quantity = int(item_data.get('quantity', 1))
                price = float(item_data.get('price', 0))
                notes = item_data.get('notes')
                
                if not plant_name:
                    continue  # Skip blank items
                
                if item_id:
                    # Update existing item
                    item = OrderItem.query.get(item_id)
                    if item and item.order_id == order.id:
                        item.product_id = product_id
                        item.plant_name = plant_name
                        item.size = size
                        item.quantity = quantity
                        item.price = price
                        item.notes = notes
                        processed_item_ids.append(item.id)
                else:
                    # Create new item
                    new_item = OrderItem(
                        order_id=order.id,
                        product_id=product_id,
                        plant_name=plant_name,
                        size=size,
                        quantity=quantity,
                        price=price,
                        notes=notes
                    )
                    db.session.add(new_item)
                    db.session.flush()  # Get ID without committing
                    processed_item_ids.append(new_item.id)
                
                # Update price list
                price_list = update_price_list(
                    customer_id=order.customer_id,
                    product_id=product_id,
                    plant_name=plant_name,
                    size=size,
                    price=price
                )
                
                # Link order item to price list if new
                if price_list and not item_id:
                    new_item.price_list_id = price_list.id
                    new_item.updated_price_list = True
            
            # Remove items that were deleted
            for item in order.items:
                if item.id not in processed_item_ids:
                    db.session.delete(item)
            
            db.session.commit()
            flash(f'Order {order.order_number} updated successfully', 'success')
            return redirect(url_for('orders.view_order', order_id=order.id))
            
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Error updating order: {str(e)}")
            flash(f'Error updating order: {str(e)}', 'danger')
            return redirect(url_for('orders.edit_order', order_id=order.id))
    
    # GET method - show form
    customers = Customer.query.order_by(Customer.name).all()
    products = Product.query.order_by(Product.name).all()
    
    return render_template(
        'orders/edit.html',
        order=order,
        customers=customers,
        products=products
    )

@orders.route('/update_status/<int:order_id>', methods=['POST'])
@login_required
def update_status(order_id):
    """Update the status of an order"""
    order = Order.query.get_or_404(order_id)
    new_status = request.form.get('status')
    
    if not new_status:
        flash('Status is required', 'danger')
        return redirect(url_for('orders.view_order', order_id=order.id))
    
    if order.transition_to(new_status):
        db.session.commit()
        flash(f'Order status updated to {order.get_status_label()}', 'success')
    else:
        flash(f'Cannot transition from {order.get_status_label()} to {OrderStatus.LABELS.get(new_status, new_status)}', 'danger')
    
    return redirect(url_for('orders.view_order', order_id=order.id))

@orders.route('/list')
@login_required
def list_orders():
    """List all orders with filtering options"""
    # Get filter parameters
    status = request.args.get('status')
    customer_id = request.args.get('customer_id')
    date_from = request.args.get('date_from')
    date_to = request.args.get('date_to')
    page = request.args.get('page', 1, type=int)
    
    # Base query
    query = Order.query
    
    # Apply filters
    if status:
        query = query.filter(Order.status == status)
    
    if customer_id:
        query = query.filter(Order.customer_id == customer_id)
    
    if date_from:
        try:
            date_from_obj = datetime.strptime(date_from, '%Y-%m-%d').date()
            query = query.filter(Order.delivery_date >= date_from_obj)
        except ValueError:
            flash('Invalid "from" date format', 'warning')
    
    if date_to:
        try:
            date_to_obj = datetime.strptime(date_to, '%Y-%m-%d').date()
            query = query.filter(Order.delivery_date <= date_to_obj)
        except ValueError:
            flash('Invalid "to" date format', 'warning')
    
    # Order by creation date (newest first)
    query = query.order_by(Order.created_at.desc())
    
    # Paginate results
    orders = query.paginate(page=page, per_page=20, error_out=False)
    
    # Get all customers for filter dropdown
    customers = Customer.query.order_by(Customer.name).all()
    
    # Get all order statuses
    statuses = OrderStatus.LABELS
    
    return render_template(
        'orders/list.html',
        orders=orders,
        customers=customers,
        statuses=statuses,
        current_filters={
            'status': status,
            'customer_id': customer_id,
            'date_from': date_from,
            'date_to': date_to
        }
    )

@orders.route('/delivery_notes')
@login_required
def delivery_notes():
    """Show form to generate delivery notes for today's orders"""
    # Get filter parameters
    delivery_date_str = request.args.get('delivery_date', date.today().strftime('%Y-%m-%d'))
    customer_id = request.args.get('customer_id')
    
    try:
        delivery_date = datetime.strptime(delivery_date_str, '%Y-%m-%d').date()
    except ValueError:
        delivery_date = date.today()
    
    # Query orders
    query = Order.query.filter(
        Order.delivery_date == delivery_date,
        Order.status.in_([OrderStatus.PREPARING, OrderStatus.READY])
    )
    
    if customer_id:
        query = query.filter(Order.customer_id == customer_id)
    
    orders = query.order_by(Order.created_at).all()
    
    # Get all customers for filter dropdown
    customers = Customer.query.order_by(Customer.name).all()
    
    return render_template(
        'orders/delivery_notes.html',
        orders=orders,
        customers=customers,
        delivery_date=delivery_date_str
    )

@orders.route('/generate_delivery_note/<int:order_id>')
@login_required
def generate_delivery_note(order_id):
    """Generate a delivery note PDF for a single order"""
    order = Order.query.get_or_404(order_id)
    language = request.args.get('language', 'en')
    
    # Generate PDF
    pdf_path = generate_delivery_note_pdf(order_id, language)
    
    if not pdf_path:
        flash('Error generating delivery note', 'danger')
        return redirect(url_for('orders.view_order', order_id=order.id))
    
    # Get just the filename from the path
    pdf_filename = os.path.basename(pdf_path)
    
    # Return the PDF file
    return redirect(url_for('static', filename=f'pdfs/{pdf_filename}'))

@orders.route('/generate_batch_delivery_note', methods=['POST'])
@login_required
def generate_batch_delivery_note():
    """Generate delivery notes for multiple orders"""
    order_ids = request.form.getlist('order_ids')
    language = request.form.get('language', 'en')
    
    if not order_ids:
        flash('No orders selected', 'warning')
        return redirect(url_for('orders.delivery_notes'))
    
    # Convert to integers
    order_ids = [int(id) for id in order_ids]
    
    # Generate batch PDF
    pdf_path = generate_delivery_note_pdf(order_ids, language, batch=True)
    
    if not pdf_path:
        flash('Error generating delivery notes', 'danger')
        return redirect(url_for('orders.delivery_notes'))
    
    # Get just the filename from the path
    pdf_filename = os.path.basename(pdf_path)
    
    # Return the PDF file
    return redirect(url_for('static', filename=f'pdfs/{pdf_filename}'))

@orders.route('/calendar')
@login_required
def calendar():
    """Show calendar view of upcoming deliveries"""
    # Get date range parameters or use defaults
    start_date_str = request.args.get('start_date')
    end_date_str = request.args.get('end_date')
    
    # Default to this week
    today = date.today()
    start_of_week = today - timedelta(days=today.weekday())
    end_of_week = start_of_week + timedelta(days=13)  # Two weeks
    
    # Parse custom date range if provided
    try:
        if start_date_str:
            start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
        else:
            start_date = start_of_week
            
        if end_date_str:
            end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()
        else:
            end_date = end_of_week
    except ValueError:
        start_date = start_of_week
        end_date = end_of_week
        flash('Invalid date format, showing default range', 'warning')
    
    # Query orders within the date range
    orders = Order.query.filter(
        Order.delivery_date.between(start_date, end_date)
    ).order_by(Order.delivery_date, Order.created_at).all()
    
    # Group orders by date
    orders_by_date = defaultdict(list)
    for order in orders:
        if order.delivery_date:
            orders_by_date[order.delivery_date].append(order)
    
    # Generate calendar days
    days = []
    current_date = start_date
    while current_date <= end_date:
        days.append({
            'date': current_date,
            'is_today': current_date == today,
            'is_weekend': current_date.weekday() >= 5,  # 5=Saturday, 6=Sunday
            'orders': orders_by_date.get(current_date, [])
        })
        current_date += timedelta(days=1)
    
    return render_template(
        'orders/calendar.html',
        days=days,
        start_date=start_date,
        end_date=end_date,
        today=today
    )

@orders.route('/api/product_info/<int:product_id>')
@login_required
def get_product_info(product_id):
    """API endpoint to get product information including customer-specific pricing"""
    product = Product.query.get_or_404(product_id)
    customer_id = request.args.get('customer_id')
    
    response = {
        'id': product.id,
        'name': product.name,
        'scientific_name': product.scientific_name,
        'pot': product.pot,
        'price': None
    }
    
    # If customer_id is provided, try to get the customer-specific price
    if customer_id:
        price_list = PriceList.query.filter_by(
            customer_id=customer_id,
            product_id=product_id
        ).order_by(PriceList.effective_date.desc()).first()
        
        if price_list:
            response['price'] = price_list.price
    
    return jsonify(response)
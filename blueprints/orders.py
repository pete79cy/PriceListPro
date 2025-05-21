"""
Orders blueprint for the Plant Pricing System.

This blueprint handles all order-related routes, including:
- Creating new orders
- Viewing order lists
- Order status management
- Delivery note generation
"""
import os
import uuid
import json
from datetime import datetime, date, timedelta
from flask import Blueprint, render_template, request, redirect, url_for, jsonify, flash, send_file
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
from app import db
from models import Customer, Product, PriceList, Order, OrderItem, OrderStatus
from utils.logger import logger
from utils.pdf_generator import generate_delivery_note_pdf

# Initialize blueprint
orders_bp = Blueprint('orders', __name__, url_prefix='/orders')

def generate_order_number():
    """Generate a unique order number with format ORD-YYYY-XXXX"""
    year = datetime.now().year
    # Get count of orders for the current year and increment by 1
    count = Order.query.filter(Order.order_number.like(f'ORD-{year}-%')).count() + 1
    return f'ORD-{year}-{count:04d}'

@orders_bp.route('/')
@login_required
def index():
    """Orders dashboard"""
    # Get overview statistics
    total_orders = Order.query.count()
    new_orders = Order.query.filter_by(status=OrderStatus.NEW).count()
    preparing_orders = Order.query.filter_by(status=OrderStatus.PREPARING).count()
    ready_orders = Order.query.filter_by(status=OrderStatus.READY).count()
    delivered_orders = Order.query.filter_by(status=OrderStatus.DELIVERED).count()
    
    # Get orders due soon
    today = date.today()
    tomorrow = today + timedelta(days=1)
    next_week = today + timedelta(days=7)
    
    orders_due_today = Order.query.filter(
        Order.delivery_date == today,
        Order.status.in_([OrderStatus.NEW, OrderStatus.PREPARING, OrderStatus.READY])
    ).all()
    
    orders_due_tomorrow = Order.query.filter(
        Order.delivery_date == tomorrow,
        Order.status.in_([OrderStatus.NEW, OrderStatus.PREPARING, OrderStatus.READY])
    ).all()
    
    # Get recent orders (last 5)
    recent_orders = Order.query.order_by(Order.created_at.desc()).limit(5).all()
    
    return render_template('orders/index.html',
                          total_orders=total_orders,
                          new_orders=new_orders,
                          preparing_orders=preparing_orders,
                          ready_orders=ready_orders,
                          delivered_orders=delivered_orders,
                          orders_due_today=orders_due_today,
                          orders_due_tomorrow=orders_due_tomorrow,
                          recent_orders=recent_orders)

@orders_bp.route('/new', methods=['GET', 'POST'])
@login_required
def new_order():
    """Create a new order"""
    if request.method == 'POST':
        try:
            # Get form data
            customer_id = request.form.get('customer_id')
            delivery_date_str = request.form.get('delivery_date')
            notes = request.form.get('notes')
            
            # Validate required fields
            if not customer_id:
                flash('Customer is required', 'danger')
                return redirect(url_for('orders.new_order'))
            
            # Parse delivery date if provided
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
            
            # Get order items from form
            items_data = request.form.get('items_data', '[]')
            items_list = json.loads(items_data)
            
            if not items_list:
                flash('At least one order item is required', 'danger')
                return redirect(url_for('orders.new_order'))
            
            # Add order to database first to get ID
            db.session.add(order)
            db.session.commit()
            
            # Process each item
            for item in items_list:
                plant_name = item.get('plant_name')
                product_id = item.get('product_id')
                quantity = int(item.get('quantity', 1))
                size = item.get('size')
                price = float(item.get('price', 0))
                item_notes = item.get('notes', '')
                
                # Validate required item fields
                if not plant_name or price <= 0:
                    continue
                
                # Check if price differs from price list and update if needed
                price_list_entry = None
                price_updated = False
                
                if product_id:
                    # Find existing price list entry for this customer and product
                    price_list_entry = PriceList.query.filter_by(
                        customer_id=customer_id,
                        product_id=product_id
                    ).first()
                    
                    if price_list_entry:
                        if price_list_entry.price != price:
                            # Update price list with new price
                            price_list_entry.price = price
                            price_list_entry.updated_at = datetime.utcnow()
                            price_updated = True
                    else:
                        # Create new price list entry
                        price_list_entry = PriceList(
                            customer_id=customer_id,
                            product_id=product_id,
                            price=price,
                            effective_date=date.today()
                        )
                        db.session.add(price_list_entry)
                        price_updated = True
                
                # Create order item
                order_item = OrderItem(
                    order_id=order.id,
                    product_id=product_id,
                    price_list_id=price_list_entry.id if price_list_entry else None,
                    plant_name=plant_name,
                    size=size,
                    quantity=quantity,
                    price=price,
                    updated_price_list=price_updated,
                    notes=item_notes
                )
                
                db.session.add(order_item)
            
            # Commit all changes
            db.session.commit()
            
            flash(f'Order {order.order_number} created successfully', 'success')
            return redirect(url_for('orders.view_order', order_id=order.id))
            
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error creating order: {str(e)}")
            flash(f'Error creating order: {str(e)}', 'danger')
            return redirect(url_for('orders.new_order'))
    
    # GET request - show order form
    customers = Customer.query.order_by(Customer.name).all()
    products = Product.query.order_by(Product.name).all()
    
    return render_template('orders/new.html', 
                          customers=customers,
                          products=products,
                          today=date.today().strftime('%Y-%m-%d'))

@orders_bp.route('/list')
@login_required
def list_orders():
    """List all orders with filters"""
    # Get filter parameters
    status = request.args.get('status')
    customer_id = request.args.get('customer_id')
    date_from = request.args.get('date_from')
    date_to = request.args.get('date_to')
    
    # Base query
    query = Order.query
    
    # Apply filters
    if status:
        query = query.filter_by(status=status)
    
    if customer_id:
        query = query.filter_by(customer_id=customer_id)
    
    if date_from:
        try:
            from_date = datetime.strptime(date_from, '%Y-%m-%d').date()
            query = query.filter(Order.delivery_date >= from_date)
        except ValueError:
            pass
    
    if date_to:
        try:
            to_date = datetime.strptime(date_to, '%Y-%m-%d').date()
            query = query.filter(Order.delivery_date <= to_date)
        except ValueError:
            pass
    
    # Execute query with pagination
    page = request.args.get('page', 1, type=int)
    per_page = 20
    orders = query.order_by(Order.created_at.desc()).paginate(page=page, per_page=per_page)
    
    # Get data for filters
    customers = Customer.query.order_by(Customer.name).all()
    
    return render_template('orders/list.html',
                          orders=orders,
                          customers=customers,
                          statuses=OrderStatus.LABELS,
                          current_filters={
                              'status': status,
                              'customer_id': customer_id,
                              'date_from': date_from,
                              'date_to': date_to
                          })

@orders_bp.route('/<int:order_id>')
@login_required
def view_order(order_id):
    """View a single order"""
    order = Order.query.get_or_404(order_id)
    return render_template('orders/view.html', order=order)

@orders_bp.route('/<int:order_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_order(order_id):
    """Edit an existing order"""
    order = Order.query.get_or_404(order_id)
    
    if request.method == 'POST':
        try:
            # Get form data
            customer_id = request.form.get('customer_id')
            delivery_date_str = request.form.get('delivery_date')
            notes = request.form.get('notes')
            status = request.form.get('status')
            
            # Validate required fields
            if not customer_id:
                flash('Customer is required', 'danger')
                return redirect(url_for('orders.edit_order', order_id=order.id))
            
            # Parse delivery date if provided
            delivery_date = None
            if delivery_date_str:
                try:
                    delivery_date = datetime.strptime(delivery_date_str, '%Y-%m-%d').date()
                except ValueError:
                    flash('Invalid delivery date format', 'danger')
                    return redirect(url_for('orders.edit_order', order_id=order.id))
            
            # Update order
            order.customer_id = customer_id
            order.delivery_date = delivery_date
            order.notes = notes
            
            # Update status if changed
            if status and status != order.status:
                if order.can_transition_to(status):
                    order.transition_to(status)
                else:
                    flash(f'Invalid status transition from {order.status} to {status}', 'warning')
            
            # Get order items from form
            items_data = request.form.get('items_data', '[]')
            items_list = json.loads(items_data)
            
            if not items_list:
                flash('At least one order item is required', 'danger')
                return redirect(url_for('orders.edit_order', order_id=order.id))
            
            # Remove existing items not in the list
            item_ids_to_keep = [int(item.get('id')) for item in items_list if item.get('id')]
            for item in order.items:
                if item.id not in item_ids_to_keep:
                    db.session.delete(item)
            
            # Process each item
            for item_data in items_list:
                item_id = item_data.get('id')
                plant_name = item_data.get('plant_name')
                product_id = item_data.get('product_id')
                quantity = int(item_data.get('quantity', 1))
                size = item_data.get('size')
                price = float(item_data.get('price', 0))
                item_notes = item_data.get('notes', '')
                
                if item_id:
                    # Update existing item
                    item = OrderItem.query.get(item_id)
                    if item and item.order_id == order.id:
                        item.plant_name = plant_name
                        item.product_id = product_id
                        item.quantity = quantity
                        item.size = size
                        item.price = price
                        item.notes = item_notes
                        
                        # Check if price differs from price list and update if needed
                        if product_id:
                            price_list_entry = PriceList.query.filter_by(
                                customer_id=customer_id,
                                product_id=product_id
                            ).first()
                            
                            if price_list_entry:
                                if price_list_entry.price != price:
                                    # Update price list with new price
                                    price_list_entry.price = price
                                    price_list_entry.updated_at = datetime.utcnow()
                                    item.updated_price_list = True
                                    item.price_list_id = price_list_entry.id
                            else:
                                # Create new price list entry
                                price_list_entry = PriceList(
                                    customer_id=customer_id,
                                    product_id=product_id,
                                    price=price,
                                    effective_date=date.today()
                                )
                                db.session.add(price_list_entry)
                                db.session.flush()  # Get ID
                                item.price_list_id = price_list_entry.id
                                item.updated_price_list = True
                else:
                    # Create new item
                    # Validate required item fields
                    if not plant_name or price <= 0:
                        continue
                    
                    # Check if price differs from price list and update if needed
                    price_list_id = None
                    price_updated = False
                    
                    if product_id:
                        # Find existing price list entry for this customer and product
                        price_list_entry = PriceList.query.filter_by(
                            customer_id=customer_id,
                            product_id=product_id
                        ).first()
                        
                        if price_list_entry:
                            if price_list_entry.price != price:
                                # Update price list with new price
                                price_list_entry.price = price
                                price_list_entry.updated_at = datetime.utcnow()
                                price_updated = True
                            price_list_id = price_list_entry.id
                        else:
                            # Create new price list entry
                            price_list_entry = PriceList(
                                customer_id=customer_id,
                                product_id=product_id,
                                price=price,
                                effective_date=date.today()
                            )
                            db.session.add(price_list_entry)
                            db.session.flush()  # Get ID
                            price_list_id = price_list_entry.id
                            price_updated = True
                    
                    # Create order item
                    new_item = OrderItem(
                        order_id=order.id,
                        product_id=product_id,
                        price_list_id=price_list_id,
                        plant_name=plant_name,
                        size=size,
                        quantity=quantity,
                        price=price,
                        updated_price_list=price_updated,
                        notes=item_notes
                    )
                    
                    db.session.add(new_item)
            
            # Save all changes
            db.session.commit()
            
            flash(f'Order {order.order_number} updated successfully', 'success')
            return redirect(url_for('orders.view_order', order_id=order.id))
            
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error updating order: {str(e)}")
            flash(f'Error updating order: {str(e)}', 'danger')
            return redirect(url_for('orders.edit_order', order_id=order.id))
    
    # GET request - show edit form
    customers = Customer.query.order_by(Customer.name).all()
    products = Product.query.order_by(Product.name).all()
    
    # Format items as JSON for JavaScript
    items_json = json.dumps([{
        'id': item.id,
        'product_id': item.product_id,
        'plant_name': item.plant_name,
        'size': item.size,
        'quantity': item.quantity,
        'price': item.price,
        'notes': item.notes
    } for item in order.items])
    
    return render_template('orders/edit.html',
                          order=order,
                          customers=customers,
                          products=products,
                          items_json=items_json,
                          statuses=OrderStatus.LABELS,
                          status_transitions=OrderStatus.TRANSITIONS[order.status])

@orders_bp.route('/<int:order_id>/status', methods=['POST'])
@login_required
def update_status(order_id):
    """Update the status of an order"""
    order = Order.query.get_or_404(order_id)
    new_status = request.form.get('status')
    
    if not new_status:
        flash('Status is required', 'danger')
        return redirect(url_for('orders.view_order', order_id=order.id))
    
    if new_status == order.status:
        flash('Status is already set to ' + OrderStatus.LABELS[new_status], 'info')
        return redirect(url_for('orders.view_order', order_id=order.id))
    
    if order.can_transition_to(new_status):
        order.transition_to(new_status)
        db.session.commit()
        flash(f'Order status updated to {OrderStatus.LABELS[new_status]}', 'success')
    else:
        flash(f'Invalid status transition from {order.status} to {new_status}', 'danger')
    
    return redirect(url_for('orders.view_order', order_id=order.id))

@orders_bp.route('/delivery-notes')
@login_required
def delivery_notes():
    """Delivery notes generation page"""
    # Get filter parameters
    delivery_date_str = request.args.get('delivery_date')
    customer_id = request.args.get('customer_id')
    
    # Default to today if no date provided
    if not delivery_date_str:
        delivery_date = date.today()
        delivery_date_str = delivery_date.strftime('%Y-%m-%d')
    else:
        try:
            delivery_date = datetime.strptime(delivery_date_str, '%Y-%m-%d').date()
        except ValueError:
            flash('Invalid delivery date format', 'danger')
            delivery_date = date.today()
            delivery_date_str = delivery_date.strftime('%Y-%m-%d')
    
    # Base query for orders due on the selected date
    query = Order.query.filter(
        Order.delivery_date == delivery_date,
        Order.status.in_([OrderStatus.NEW, OrderStatus.PREPARING, OrderStatus.READY])
    )
    
    # Apply customer filter if provided
    if customer_id:
        query = query.filter_by(customer_id=customer_id)
    
    # Get orders
    orders = query.all()
    
    # Get customers for filter dropdown
    customers = Customer.query.order_by(Customer.name).all()
    
    return render_template('orders/delivery_notes.html',
                          orders=orders,
                          customers=customers,
                          delivery_date=delivery_date_str)

@orders_bp.route('/<int:order_id>/delivery-note')
@login_required
def generate_delivery_note(order_id):
    """Generate a delivery note for a specific order"""
    order = Order.query.get_or_404(order_id)
    
    language = request.args.get('language', 'en')  # Default to English
    
    try:
        # Generate PDF delivery note
        pdf_path = generate_delivery_note_pdf(order, language)
        
        if not pdf_path or not os.path.exists(pdf_path):
            flash('Error generating delivery note', 'danger')
            return redirect(url_for('orders.view_order', order_id=order.id))
        
        # Return the generated PDF
        return send_file(
            pdf_path,
            download_name=f'Delivery_Note_{order.order_number}.pdf',
            as_attachment=True
        )
        
    except Exception as e:
        logger.error(f"Error generating delivery note: {str(e)}")
        flash(f'Error generating delivery note: {str(e)}', 'danger')
        return redirect(url_for('orders.view_order', order_id=order.id))

@orders_bp.route('/batch-delivery-note', methods=['POST'])
@login_required
def generate_batch_delivery_note():
    """Generate a combined delivery note for multiple orders"""
    order_ids = request.form.getlist('order_ids')
    language = request.form.get('language', 'en')
    
    if not order_ids:
        flash('No orders selected', 'danger')
        return redirect(url_for('orders.delivery_notes'))
    
    try:
        # Fetch all selected orders
        orders = Order.query.filter(Order.id.in_(order_ids)).all()
        
        if not orders:
            flash('No valid orders found', 'danger')
            return redirect(url_for('orders.delivery_notes'))
        
        # Generate combined PDF delivery note
        pdf_path = generate_delivery_note_pdf(orders, language, batch=True)
        
        if not pdf_path or not os.path.exists(pdf_path):
            flash('Error generating batch delivery note', 'danger')
            return redirect(url_for('orders.delivery_notes'))
        
        # Return the generated PDF
        delivery_date = orders[0].delivery_date.strftime('%Y-%m-%d') if orders[0].delivery_date else 'batch'
        return send_file(
            pdf_path,
            download_name=f'Delivery_Notes_{delivery_date}.pdf',
            as_attachment=True
        )
        
    except Exception as e:
        logger.error(f"Error generating batch delivery note: {str(e)}")
        flash(f'Error generating batch delivery note: {str(e)}', 'danger')
        return redirect(url_for('orders.delivery_notes'))

@orders_bp.route('/calendar')
@login_required
def calendar():
    """Calendar view of upcoming deliveries"""
    # Get the current month/year or from query parameters
    current_date = date.today()
    month = request.args.get('month', current_date.month, type=int)
    year = request.args.get('year', current_date.year, type=int)
    
    # Validate month/year
    if month < 1 or month > 12:
        month = current_date.month
    if year < current_date.year or year > current_date.year + 5:
        year = current_date.year
    
    # Get first and last day of the month
    first_day = date(year, month, 1)
    if month == 12:
        last_day = date(year + 1, 1, 1) - timedelta(days=1)
    else:
        last_day = date(year, month + 1, 1) - timedelta(days=1)
    
    # Get orders for this month
    orders = Order.query.filter(
        Order.delivery_date >= first_day,
        Order.delivery_date <= last_day
    ).all()
    
    # Group orders by day
    calendar_data = {}
    for day in range(1, last_day.day + 1):
        current_day = date(year, month, day)
        calendar_data[day] = [order for order in orders if order.delivery_date == current_day]
    
    # Next and previous month links
    if month == 1:
        prev_month = 12
        prev_year = year - 1
    else:
        prev_month = month - 1
        prev_year = year
        
    if month == 12:
        next_month = 1
        next_year = year + 1
    else:
        next_month = month + 1
        next_year = year
    
    return render_template('orders/calendar.html',
                          year=year,
                          month=month,
                          current_date=current_date,
                          calendar_data=calendar_data,
                          month_name=first_day.strftime('%B'),
                          prev_month=prev_month,
                          prev_year=prev_year,
                          next_month=next_month,
                          next_year=next_year,
                          first_day_weekday=first_day.weekday())

@orders_bp.route('/api/get-product-info/<int:product_id>')
@login_required
def get_product_info(product_id):
    """API endpoint to get product information"""
    product = Product.query.get_or_404(product_id)
    
    # Try to get price from price list if customer_id is provided
    customer_id = request.args.get('customer_id')
    price = None
    
    if customer_id:
        price_list_entry = PriceList.query.filter_by(
            customer_id=customer_id,
            product_id=product_id
        ).order_by(PriceList.updated_at.desc()).first()
        
        if price_list_entry:
            price = price_list_entry.price
    
    return jsonify({
        'id': product.id,
        'name': product.name,
        'scientific_name': product.scientific_name,
        'pot': product.pot,
        'price': price
    })

# Helper function for routes that need to generate delivery notes
def generate_delivery_note_pdf(order_or_orders, language='en', batch=False):
    """
    Generate a PDF delivery note for a single order or multiple orders.
    
    Args:
        order_or_orders: A single Order object or a list of Order objects
        language: Language code for the delivery note ('en', 'el', or 'ar')
        batch: Whether this is a batch delivery note
        
    Returns:
        str: Path to the generated PDF
    """
    # Placeholder until we implement the actual PDF generator
    # This should be implemented in utils/pdf_generator.py
    return None
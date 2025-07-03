from datetime import datetime, date, timedelta
from flask import render_template, request, redirect, url_for, flash, abort, current_app, jsonify
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
import os
import uuid
import json

from . import orders
from models import db, Customer, Product, PriceList, OrderStatusEnum, ORDER_STATUS_LABELS, ORDER_STATUS_COLORS, ORDER_STATUS_TRANSITIONS
from models import Order, OrderItem
from utils.pdf_generator import generate_delivery_note_pdf, generate_charge_sheet_pdf
from utils.proforma_invoice_generator import generate_proforma_invoice_bytes
from utils.translations import get_translations
from utils.orders_helpers import (
    to_decimal, validate_order_item_data, validate_status_transition,
    log_exceptions, calculate_order_totals, update_customer_price_list_safe
)
from forms import EnhancedOrderForm, OrderItemForm

# Helper functions
def as_int_or_none(raw):
    """Coerce '', None, or non-digit strings to None; else return int(value)."""
    if raw is None or raw == '':
        return None
    return int(raw) if str(raw).isdigit() else None

def generate_order_number():
    """Atomic, race-safe order number generator: ORD-YYYY-NNN"""
    year = datetime.utcnow().year
    prefix = f"ORD-{year}-"
    
    # Start with highest existing number + 1 to avoid unnecessary retries
    latest_order = Order.query.filter(
        Order.order_number.like(f'ORD-{year}-%')
    ).order_by(Order.order_number.desc()).first()
    
    if latest_order:
        try:
            parts = latest_order.order_number.split('-')
            if len(parts) >= 3:
                next_seq_num = int(parts[2]) + 1
            else:
                next_seq_num = 1
        except (ValueError, IndexError):
            next_seq_num = 1
    else:
        next_seq_num = 1
    
    # Try up to 100 times to avoid infinite loop
    max_attempts = 100
    for attempt in range(max_attempts):
        candidate = f"{prefix}{next_seq_num:03d}"
        
        # Check if this number is already taken
        existing = Order.query.filter_by(order_number=candidate).first()
        if not existing:
            return candidate
        
        next_seq_num += 1
    
    # Fallback with timestamp if all attempts failed
    import time
    timestamp = int(time.time() * 1000) % 99999
    return f"ORD-{year}-{timestamp:05d}"

def get_customer_price(customer_id, product_id):
    """Get the price for a product from customer's price list"""
    price_list_item = PriceList.query.filter_by(
        customer_id=customer_id, 
        product_id=product_id
    ).order_by(PriceList.updated_at.desc()).first()
    
    if price_list_item:
        return price_list_item.price
    
    # If no customer-specific price found, set a default price
    # We don't have a standard_price field in the Product model
    # So we'll return a reasonable default or look for other price sources
    
    # First try to find any price list entry for this product to use as reference
    any_price_list = PriceList.query.filter_by(product_id=product_id).order_by(PriceList.updated_at.desc()).first()
    if any_price_list:
        return any_price_list.price
    
    # If still no price found, return a default value
    return 0.0  # Default price can be adjusted as needed

def update_customer_price_list(customer_id, product_id, price):
    """Update or create a price list entry for a customer-product pair"""
    price_list_item = PriceList.query.filter_by(
        customer_id=customer_id,
        product_id=product_id
    ).first()
    
    if price_list_item:
        # Update existing price
        price_list_item.price = price
        price_list_item.updated_at = datetime.utcnow()
    else:
        # Create new price list entry
        price_list_item = PriceList(
            customer_id=customer_id,
            product_id=product_id,
            price=price,
            effective_date=date.today()
        )
        db.session.add(price_list_item)
        
    db.session.commit()
    return price_list_item

# Routes
@orders.route('/')
@login_required
def index():
    """Daily Orders dashboard"""
    # Get all orders with their items, newest first
    orders_list = Order.query.order_by(Order.created_at.desc()).all()
    
    # Get today's delivery orders
    today = date.today()
    
    # Using simpler individual queries to avoid SQLAlchemy compatibility issues
    today_deliveries = []
    
    # Get new orders for today
    new_orders = Order.query.filter_by(delivery_date=today, status=OrderStatusEnum.NEW.value).all()
    today_deliveries.extend(new_orders)
    
    # Get preparing orders for today
    preparing_orders = Order.query.filter_by(delivery_date=today, status=OrderStatusEnum.PREPARING.value).all()
    today_deliveries.extend(preparing_orders)
    
    # Get ready orders for today
    ready_orders = Order.query.filter_by(delivery_date=today, status=OrderStatusEnum.READY.value).all()
    today_deliveries.extend(ready_orders)
    
    # Count orders by status
    status_counts = {
        status: Order.query.filter_by(status=status).count() 
        for status in ORDER_STATUS_LABELS.keys()
    }
    
    # Get all customers for the filter dropdown
    customers = Customer.query.order_by(Customer.name).all()
    
    # Get all products for adding items to orders
    products = Product.query.order_by(Product.name).all()
    
    return render_template(
        'orders/index.html',
        orders=orders_list,
        today_deliveries=today_deliveries,
        status_counts=status_counts,
        OrderStatus=OrderStatusEnum,
        ORDER_STATUS_COLORS=ORDER_STATUS_COLORS,
        customers=customers,
        products=products
    )

@orders.route('/new', methods=['GET', 'POST'])
@login_required
def new_order():
    """Create a new order with enhanced functionality"""
    if request.method == 'POST':
        # Extract form data
        customer_id = request.form.get('customer_id')
        delivery_date_str = request.form.get('delivery_date')
        notes = request.form.get('notes')
        items_json = request.form.get('items')
        
        # Validate required fields
        if not customer_id or customer_id == '0':
            flash('Please select a valid customer', 'danger')
            form = EnhancedOrderForm()
            customers = Customer.query.order_by(Customer.name).all()
            return render_template('orders/enhanced_order_form.html', 
                                 form=form, 
                                 order=None,
                                 status_choices=[],
                                 customers=customers)
            
        # Parse delivery date if provided
        delivery_date = None
        if delivery_date_str:
            try:
                delivery_date = datetime.strptime(delivery_date_str, '%Y-%m-%d').date()
            except ValueError:
                flash('Invalid delivery date format', 'warning')
        
        # Create new order
        order = Order(
            order_number=generate_order_number(),
            customer_id=customer_id,
            status=OrderStatusEnum.NEW.value,
            notes=notes,
            delivery_date=delivery_date
        )
        
        db.session.add(order)
        db.session.flush()  # Get the order ID
        
        # Process order items if provided
        if items_json:
            try:
                import json
                items = json.loads(items_json)
                
                for item_data in items:
                    if not item_data.get('plant_name') or not item_data.get('quantity'):
                        continue
                        
                    item = OrderItem(
                        order_id=order.id,
                        product_id=as_int_or_none(item_data.get('product_id')),
                        price_list_id=as_int_or_none(item_data.get('price_list_id')),
                        plant_name=item_data['plant_name'],
                        size=item_data.get('size', ''),
                        quantity=int(item_data['quantity']),
                        price=float(item_data.get('price', 0)),
                        vat_rate=float(item_data.get('vat_rate', 19.0)),
                        notes=item_data.get('notes', '')
                    )
                    
                    db.session.add(item)
                    
                    # Update customer price list if requested
                    if (item_data.get('update_price_list', False) and 
                        item.product_id and item.price > 0):
                        update_customer_price_list(order.customer_id, item.product_id, item.price)
                        item.updated_price_list = True
                        
            except (json.JSONDecodeError, ValueError, KeyError) as e:
                flash(f'Error processing order items: {str(e)}', 'warning')
        
        db.session.commit()
        
        flash(f'Order {order.order_number} created successfully', 'success')
        return redirect(url_for('orders.view_order', order_id=order.id))
    
    # GET request - display the enhanced form
    form = EnhancedOrderForm()
    customers = Customer.query.order_by(Customer.name).all()
    return render_template('orders/enhanced_order_form.html', 
                         form=form, 
                         order=None,
                         status_choices=[],
                         customers=customers)

@orders.route('/enhanced/new', methods=['GET', 'POST'])
@login_required
def new_enhanced_order():
    """Create a new order using the enhanced interface"""
    return new_order()

@orders.route('/<int:order_id>')
@login_required
def view_order(order_id):
    """View a specific order"""
    order = Order.query.get_or_404(order_id)
    
    # Get all products for adding items to order
    products = Product.query.order_by(Product.name).all()
    
    # Get available status options for this order
    available_statuses = []
    for status in OrderStatusEnum:
        if status.value == order.status or status.value in ORDER_STATUS_TRANSITIONS.get(order.status, []):
            available_statuses.append(status)
    
    return render_template(
        'orders/view.html',
        order=order,
        products=products,
        available_statuses=available_statuses,
        ORDER_STATUS_COLORS=ORDER_STATUS_COLORS
    )

@orders.route('/<int:order_id>/add_item', methods=['POST'])
@login_required
def add_item_to_order(order_id):
    """Add a new item to an existing order"""
    order = Order.query.get_or_404(order_id)
    
    try:
        # Extract item data from form
        product_id = request.form.get('product_id')
        price_list_id = request.form.get('price_list_id')
        plant_name = request.form.get('plant_name')
        size = request.form.get('size', '')
        quantity = request.form.get('quantity')
        price = request.form.get('price')
        vat_rate = request.form.get('vat_rate', '19.0')
        notes = request.form.get('notes', '')
        
        # Validate required fields
        if not plant_name or not quantity or not price:
            flash('Plant name, quantity, and price are required', 'danger')
            return redirect(url_for('orders.view_order', order_id=order_id))
        
        # Create new order item with proper data type conversion
        item = OrderItem(
            order_id=order.id,
            product_id=as_int_or_none(product_id),
            price_list_id=as_int_or_none(price_list_id),
            plant_name=plant_name,
            size=size,
            quantity=int(quantity),
            price=float(price),
            vat_rate=float(vat_rate),
            notes=notes
        )
        
        db.session.add(item)
        db.session.commit()
        
        flash(f'Product "{plant_name}" added to order successfully', 'success')
        
    except ValueError as e:
        db.session.rollback()
        flash(f'Invalid data provided: {str(e)}', 'danger')
    except Exception as e:
        db.session.rollback()
        flash(f'Error adding product to order: {str(e)}', 'danger')
    
    return redirect(url_for('orders.view_order', order_id=order_id))

@orders.route('/<int:order_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_order(order_id):
    """Edit an existing order with enhanced functionality"""
    order = Order.query.get_or_404(order_id)
    
    if request.method == 'POST':
        # Extract form data
        customer_id = request.form.get('customer_id')
        delivery_date_str = request.form.get('delivery_date')
        notes = request.form.get('notes')
        status = request.form.get('status')
        items_json = request.form.get('items')
        
        # Validate required fields
        if not customer_id:
            flash('Customer is required', 'danger')
            return redirect(url_for('orders.edit_order', order_id=order_id))
            
        # Parse delivery date if provided
        delivery_date = None
        if delivery_date_str:
            try:
                delivery_date = datetime.strptime(delivery_date_str, '%Y-%m-%d').date()
            except ValueError:
                flash('Invalid delivery date format', 'warning')
        
        # Update order fields
        order.customer_id = customer_id
        order.delivery_date = delivery_date
        order.notes = notes
        order.updated_at = datetime.utcnow()
        
        # Update status if provided and valid
        if status and status in ORDER_STATUS_TRANSITIONS.get(order.status, []) or status == order.status:
            order.status = status
        
        # Clear existing items if new items provided
        if items_json:
            try:
                import json
                items = json.loads(items_json)
                
                # Remove existing items
                OrderItem.query.filter_by(order_id=order.id).delete()
                
                # Add new items
                for item_data in items:
                    if not item_data.get('plant_name') or not item_data.get('quantity'):
                        continue
                        
                    item = OrderItem(
                        order_id=order.id,
                        product_id=item_data.get('product_id'),
                        price_list_id=item_data.get('price_list_id'),
                        plant_name=item_data['plant_name'],
                        size=item_data.get('size', ''),
                        quantity=int(item_data['quantity']),
                        price=float(item_data.get('price', 0)),
                        vat_rate=float(item_data.get('vat_rate', 19.0)),
                        notes=item_data.get('notes', '')
                    )
                    
                    db.session.add(item)
                    
                    # Update customer price list if requested
                    if (item_data.get('update_price_list', False) and 
                        item.product_id and item.price > 0):
                        update_customer_price_list(order.customer_id, item.product_id, item.price)
                        item.updated_price_list = True
                        
            except (json.JSONDecodeError, ValueError, KeyError) as e:
                flash(f'Error processing order items: {str(e)}', 'warning')
        
        db.session.commit()
        
        flash(f'Order {order.order_number} updated successfully', 'success')
        return redirect(url_for('orders.view_order', order_id=order.id))
    
    # GET request - display the enhanced form
    form = EnhancedOrderForm(obj=order)
    customers = Customer.query.order_by(Customer.name).all()
    
    # Set current customer
    if order.customer_id:
        form.customer_id.data = order.customer_id
    
    # Get available status choices
    status_choices = [(order.status, ORDER_STATUS_LABELS.get(order.status, order.status))]
    for status_value in ORDER_STATUS_TRANSITIONS.get(order.status, []):
        status_choices.append((status_value, ORDER_STATUS_LABELS.get(status_value, status_value)))
    
    return render_template('orders/enhanced_order_form.html', 
                         form=form, 
                         order=order,
                         status_choices=status_choices,
                         customers=customers)

@orders.route('/demo')
@login_required
def demo():
    """Demo page for enhanced daily orders management"""
    return render_template('orders/demo.html')

@orders.route('/price-list')
@login_required
def customer_price_list():
    """Manage customer price lists"""
    # Get all price list entries with relationships
    price_list_entries = PriceList.query.join(Customer).join(Product).order_by(
        Customer.name, Product.name
    ).all()
    
    # Get all customers and products for the dropdowns
    customers = Customer.query.order_by(Customer.name).all()
    products = Product.query.order_by(Product.name).all()
    
    return render_template('orders/customer_price_list.html',
                         price_list_entries=price_list_entries,
                         customers=customers,
                         products=products)

@orders.route('/<int:order_id>/status', methods=['POST'])
@login_required
def update_status(order_id):
    """Update the status of an order"""
    order = Order.query.get_or_404(order_id)
    new_status = request.form.get('status')
    
    # Validate the status transition
    if new_status not in ORDER_STATUS_TRANSITIONS.get(order.status, []) and new_status != order.status:
        flash(f'Cannot change status from {order.status} to {new_status}', 'danger')
        return redirect(url_for('orders.view_order', order_id=order.id))
    
    # Update the status
    old_status = order.status
    order.status = new_status
    order.updated_at = datetime.utcnow()
    db.session.commit()
    
    flash(f'Order status updated from {old_status} to {new_status}', 'success')
    return redirect(url_for('orders.view_order', order_id=order.id))

@orders.route('/<int:order_id>/add_item', methods=['POST'])
@login_required
def add_item(order_id):
    """Add an item to an order - supports both existing products and creating new ones"""
    order = Order.query.get_or_404(order_id)
    
    # Extract form data
    product_id = request.form.get('product_id')
    quantity = request.form.get('quantity', type=int)
    unit_price = request.form.get('unit_price', type=float)
    vat_rate = request.form.get('vat_rate', type=float, default=19.0)
    update_price_list = 'update_price_list' in request.form
    
    # New product fields (for products that don't exist)
    new_product_name = request.form.get('new_product_name', '').strip()
    new_product_category = request.form.get('new_product_category', '').strip()
    new_product_scientific_name = request.form.get('new_product_scientific_name', '').strip()
    new_product_pot = request.form.get('new_product_pot', '').strip()
    new_product_sku = request.form.get('new_product_sku', '').strip()
    new_product_description = request.form.get('new_product_description', '').strip()
    
    # Validate required fields
    if not quantity:
        flash('Quantity is required', 'danger')
        return redirect(url_for('orders.view_order', order_id=order.id))
    
    product = None
    
    # Check if we're adding a new product or using an existing one
    if new_product_name:
        # Creating a new product
        if not unit_price:
            flash('Price is required when adding a new product', 'danger')
            return redirect(url_for('orders.view_order', order_id=order.id))
        
        # Check if a similar product already exists
        existing_product = Product.query.filter_by(name=new_product_name).first()
        if existing_product:
            flash(f'A product with the name "{new_product_name}" already exists. Please use the existing product or choose a different name.', 'warning')
            return redirect(url_for('orders.view_order', order_id=order.id))
        
        # Create new product
        product = Product(
            name=new_product_name,
            category=new_product_category if new_product_category else None,
            scientific_name=new_product_scientific_name if new_product_scientific_name else None,
            pot=new_product_pot if new_product_pot else None,
            sku=new_product_sku if new_product_sku else None,
            description=new_product_description if new_product_description else None
        )
        db.session.add(product)
        db.session.flush()  # Flush to get the ID
        
        product_id = product.id
        plant_name = product.name
        size = product.pot if product.pot else ''
        
        flash(f'Created new product: {new_product_name}', 'info')
        
    elif product_id:
        # Using existing product
        product = Product.query.get(product_id)
        if not product:
            flash('Invalid product selected', 'danger')
            return redirect(url_for('orders.view_order', order_id=order.id))
        
        # If unit price not provided, get from customer's price list
        if not unit_price:
            unit_price = get_customer_price(order.customer_id, product_id)
            if not unit_price:
                flash('No price found for this product. Please enter a price.', 'warning')
                return redirect(url_for('orders.view_order', order_id=order.id))
        
        plant_name = product.name
        size = product.pot if product.pot else ''
        
    else:
        flash('Please select an existing product or enter details for a new product', 'danger')
        return redirect(url_for('orders.view_order', order_id=order.id))
    
    # Create new order item
    order_item = OrderItem(
        order_id=order.id,
        product_id=product_id,
        plant_name=plant_name,
        size=size,
        quantity=quantity,
        price=unit_price,
        vat_rate=vat_rate
    )
    
    db.session.add(order_item)
    
    # Update the customer's price list if requested
    if update_price_list and product_id:
        update_customer_price_list(order.customer_id, product_id, unit_price)
    
    db.session.commit()
    
    flash(f'Added {quantity} x {plant_name} to the order', 'success')
    return redirect(url_for('orders.view_order', order_id=order.id))

@orders.route('/<int:order_id>/item/<int:item_id>/update', methods=['POST'])
@login_required
def update_item(order_id, item_id):
    """Update an order item"""
    order = Order.query.get_or_404(order_id)
    item = OrderItem.query.filter_by(id=item_id, order_id=order_id).first_or_404()
    
    # Extract form data
    quantity = request.form.get('quantity', type=int)
    unit_price = request.form.get('unit_price', type=float)
    vat_rate = request.form.get('vat_rate', type=float, default=19.0)
    update_price_list = 'update_price_list' in request.form
    
    # Validate required fields
    if not quantity or not unit_price:
        flash('Quantity and price are required', 'danger')
        return redirect(url_for('orders.view_order', order_id=order.id))
    
    # Update item
    item.quantity = quantity
    item.price = unit_price
    item.vat_rate = vat_rate
    
    # Update the customer's price list if requested and a product is linked
    if update_price_list and item.product_id:
        update_customer_price_list(order.customer_id, item.product_id, unit_price)
    
    db.session.commit()
    
    flash('Order item updated successfully', 'success')
    return redirect(url_for('orders.view_order', order_id=order.id))

@orders.route('/<int:order_id>/item/<int:item_id>/update-inline', methods=['PUT'])
@login_required
def update_item_inline(order_id, item_id):
    """Update an order item via AJAX for inline editing"""
    from flask import jsonify
    
    order = Order.query.get_or_404(order_id)
    item = OrderItem.query.filter_by(id=item_id, order_id=order_id).first_or_404()
    
    # Get JSON data from request
    data = request.get_json()
    if not data:
        return jsonify({'error': 'No data provided'}), 400
    
    try:
        # Update item fields
        item.quantity = int(data.get('quantity', item.quantity))
        item.price = float(data.get('unit_price', item.price))
        item.vat_rate = float(data.get('vat_rate', item.vat_rate or 19.0))
        item.updated_at = datetime.utcnow()
        
        db.session.commit()
        
        # Calculate totals for the entire order
        subtotal = sum(item.price * item.quantity for item in order.items)
        vat_5 = sum((item.price * item.quantity) * 0.05 for item in order.items if item.vat_rate == 5.0)
        vat_19 = sum((item.price * item.quantity) * 0.19 for item in order.items if item.vat_rate == 19.0)
        total = subtotal + vat_5 + vat_19
        
        # Return updated data
        return jsonify({
            'id': item.id,
            'quantity': item.quantity,
            'unit_price': float(item.price),
            'vat_rate': float(item.vat_rate),
            'total': float(item.price * item.quantity),
            'order_subtotal': float(subtotal),
            'order_vat_5': float(vat_5),
            'order_vat_19': float(vat_19),
            'order_total': float(total)
        })
        
    except (ValueError, TypeError) as e:
        return jsonify({'error': 'Invalid data format'}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Failed to update item'}), 500

@orders.route('/<int:order_id>/item/<int:item_id>/remove', methods=['POST'])
@login_required
def remove_item(order_id, item_id):
    """Remove an item from an order"""
    order = Order.query.get_or_404(order_id)
    item = OrderItem.query.filter_by(id=item_id, order_id=order_id).first_or_404()
    
    db.session.delete(item)
    db.session.commit()
    
    flash('Item removed from order', 'success')
    return redirect(url_for('orders.view_order', order_id=order.id))

@orders.route('/<int:order_id>/delivery_note')
@login_required
def print_delivery_note(order_id):
    """Generate and display a PDF delivery note"""
    order = Order.query.get_or_404(order_id)
    
    # Get requested language (default to English)
    language = request.args.get('lang', 'en')
    
    # Only allow certain languages
    if language not in ['en', 'el', 'ar']:
        language = 'en'
    
    # Get translations
    _ = get_translations(language)
    
    # Generate PDF
    pdf_data = generate_delivery_note_pdf(order, language)
    if not pdf_data:
        flash('Error generating delivery note', 'danger')
        return redirect(url_for('orders.view_order', order_id=order.id))
    
    # Create a unique filename for the PDF
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f"delivery_note_{order.order_number}_{timestamp}.pdf"
    
    # Save the PDF file
    pdf_dir = os.path.join(current_app.static_folder, 'pdfs')
    os.makedirs(pdf_dir, exist_ok=True)
    pdf_path = os.path.join(pdf_dir, filename)
    
    with open(pdf_path, 'wb') as f:
        f.write(pdf_data)
    
    # Return a link to the generated PDF
    return redirect(url_for('static', filename=f'pdfs/{filename}'))

@orders.route('/<int:order_id>/charge_sheet')
@login_required
def generate_charge_sheet(order_id):
    """Generate and display a PDF Pro Forma Invoice"""
    order = Order.query.get_or_404(order_id)
    
    # Generate PDF
    pdf_data = generate_charge_sheet_pdf(order)
    if not pdf_data:
        flash('Error generating charge sheet', 'danger')
        return redirect(url_for('orders.view_order', order_id=order.id))
    
    # Create a unique filename for the PDF
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f"pro_forma_invoice_{order.order_number}_{timestamp}.pdf"
    
    # Save the PDF file
    pdf_dir = os.path.join(current_app.static_folder, 'pdfs')
    os.makedirs(pdf_dir, exist_ok=True)
    pdf_path = os.path.join(pdf_dir, filename)
    
    with open(pdf_path, 'wb') as f:
        f.write(pdf_data)
    
    # Return a link to the generated PDF
    return redirect(url_for('static', filename=f'pdfs/{filename}'))

@orders.route('/<int:order_id>/proforma_invoice')
@login_required
def generate_proforma_invoice(order_id):
    """Generate and download a Pro Forma Invoice PDF for the order"""
    from flask import Response
    
    order = Order.query.get_or_404(order_id)
    
    try:
        # Generate PDF as bytes
        pdf_bytes = generate_proforma_invoice_bytes(order)
        
        # Create filename for download
        filename = f"proforma_invoice_{order.order_number}.pdf"
        
        # Return PDF as download
        return Response(
            pdf_bytes,
            mimetype='application/pdf',
            headers={
                'Content-Disposition': f'attachment; filename="{filename}"',
                'Content-Type': 'application/pdf'
            }
        )
        
    except Exception as e:
        flash(f'Error generating Pro Forma Invoice: {str(e)}', 'danger')
        return redirect(url_for('orders.view_order', order_id=order.id))
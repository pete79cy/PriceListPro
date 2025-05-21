"""
Orders Blueprint - Handles daily plant orders management with status workflow
"""
from datetime import datetime, date, timedelta
import re
from sqlalchemy import desc, or_, and_, func
from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify, g
from flask_login import login_required, current_user
from werkzeug.exceptions import NotFound

from app import db
from models import Customer, Product, Order, OrderItem, OrderStatus, PriceList, PriceListItem


orders = Blueprint('orders', __name__, url_prefix='/orders')


@orders.route('/')
@login_required
def index():
    """Orders dashboard with overview and recent activity"""
    # Get counts by status
    status_counts = {}
    for status in OrderStatus:
        count = Order.query.filter_by(status=status).count()
        status_counts[status.name] = {
            'count': count,
            'label': OrderStatus.LABELS[status],
            'color': OrderStatus.COLORS[status]
        }
    
    # Today's orders
    today = date.today()
    todays_orders = Order.query.filter(
        Order.delivery_date == today,
        Order.status != OrderStatus.CANCELLED
    ).order_by(Order.created_at.desc()).all()
    
    # Tomorrow's orders
    tomorrow = today + timedelta(days=1)
    tomorrows_orders = Order.query.filter(
        Order.delivery_date == tomorrow,
        Order.status != OrderStatus.CANCELLED
    ).order_by(Order.created_at.desc()).all()
    
    # Recent orders (last 10)
    recent_orders = Order.query.order_by(
        Order.created_at.desc()
    ).limit(10).all()
    
    # Prepare order items for JSON
    recent_order_data = []
    for order in recent_orders:
        customer_name = order.customer.name if order.customer else "Unknown"
        delivery_date = order.delivery_date.strftime('%Y-%m-%d') if order.delivery_date else None
        recent_order_data.append({
            'id': order.id,
            'order_number': order.order_number,
            'customer': customer_name,
            'status': order.get_status_label(),
            'status_color': order.get_status_color(),
            'delivery_date': delivery_date,
            'created_at': order.created_at.strftime('%Y-%m-%d %H:%M'),
            'item_count': len(order.items)
        })
    
    return render_template(
        'orders/index.html',
        status_counts=status_counts,
        todays_orders=todays_orders,
        tomorrows_orders=tomorrows_orders,
        recent_orders=recent_orders,
        recent_order_data=recent_order_data
    )


@orders.route('/new', methods=['GET', 'POST'])
@login_required
def new_order():
    """Create a new order"""
    if request.method == 'POST':
        # Get form data
        customer_id = request.form.get('customer_id')
        notes = request.form.get('notes', '')
        delivery_date_str = request.form.get('delivery_date')
        
        # Validate required fields
        if not customer_id:
            flash('Customer is required', 'error')
            return redirect(url_for('orders.new_order'))
        
        # Parse delivery date if provided
        delivery_date = None
        if delivery_date_str:
            try:
                delivery_date = datetime.strptime(delivery_date_str, '%Y-%m-%d').date()
            except ValueError:
                flash('Invalid delivery date format', 'error')
                return redirect(url_for('orders.new_order'))
        
        # Create the order
        new_order = Order(
            order_number=Order.generate_order_number(),
            customer_id=customer_id,
            notes=notes,
            delivery_date=delivery_date,
            status=OrderStatus.NEW
        )
        
        db.session.add(new_order)
        db.session.commit()
        
        flash(f'Order {new_order.order_number} created successfully', 'success')
        return redirect(url_for('orders.view_order', order_id=new_order.id))
    
    # Get all customers for the dropdown
    customers = Customer.query.order_by(Customer.name).all()
    
    # Default delivery date to tomorrow
    tomorrow = date.today() + timedelta(days=1)
    default_delivery_date = tomorrow.strftime('%Y-%m-%d')
    
    return render_template(
        'orders/new.html',
        customers=customers,
        default_delivery_date=default_delivery_date
    )


@orders.route('/<int:order_id>', methods=['GET'])
@login_required
def view_order(order_id):
    """View a single order"""
    order = Order.query.get_or_404(order_id)
    
    # Get available products for adding to order
    products = Product.query.order_by(Product.name).all()
    
    # Get customer's price list if available
    price_list = None
    if order.customer_id:
        price_list = PriceList.query.filter_by(
            customer_id=order.customer_id, 
            is_active=True
        ).order_by(desc(PriceList.created_at)).first()
    
    return render_template(
        'orders/view.html',
        order=order,
        products=products,
        price_list=price_list,
        OrderStatus=OrderStatus
    )


@orders.route('/list', methods=['GET'])
@login_required
def list_orders():
    """List all orders with filtering options"""
    # Get filter parameters
    status = request.args.get('status')
    customer_id = request.args.get('customer_id')
    date_from = request.args.get('date_from')
    date_to = request.args.get('date_to')
    search = request.args.get('search', '')
    
    # Base query
    query = Order.query
    
    # Apply filters
    if status:
        try:
            status_enum = OrderStatus[status]
            query = query.filter(Order.status == status_enum)
        except KeyError:
            pass
    
    if customer_id and customer_id.isdigit():
        query = query.filter(Order.customer_id == int(customer_id))
    
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
    
    if search:
        search_term = f"%{search}%"
        query = query.join(Customer).filter(
            or_(
                Order.order_number.like(search_term),
                Customer.name.like(search_term),
                Order.notes.like(search_term)
            )
        )
    
    # Default sort by newest first
    orders = query.order_by(Order.created_at.desc()).all()
    
    # Get all customers for the filter dropdown
    customers = Customer.query.order_by(Customer.name).all()
    
    return render_template(
        'orders/list.html',
        orders=orders,
        customers=customers,
        OrderStatus=OrderStatus,
        filters={
            'status': status,
            'customer_id': customer_id,
            'date_from': date_from,
            'date_to': date_to,
            'search': search
        }
    )


@orders.route('/calendar', methods=['GET'])
@login_required
def calendar():
    """Calendar view of orders by delivery date"""
    # Get the month/year from query params or use current month
    year = request.args.get('year')
    month = request.args.get('month')
    
    today = date.today()
    if not year or not month:
        year = today.year
        month = today.month
    else:
        year = int(year)
        month = int(month)
    
    # Create date range for the month
    start_date = date(year, month, 1)
    if month == 12:
        end_date = date(year + 1, 1, 1) - timedelta(days=1)
    else:
        end_date = date(year, month + 1, 1) - timedelta(days=1)
    
    # Get all orders for the month
    orders = Order.query.filter(
        Order.delivery_date.between(start_date, end_date),
        Order.status != OrderStatus.CANCELLED
    ).order_by(Order.delivery_date, Order.created_at).all()
    
    # Group orders by date for the calendar
    calendar_data = {}
    for day in range(1, end_date.day + 1):
        current_date = date(year, month, day)
        calendar_data[current_date] = []
    
    for order in orders:
        if order.delivery_date in calendar_data:
            calendar_data[order.delivery_date].append(order)
    
    # Navigation links for prev/next month
    if month == 1:
        prev_month = (year - 1, 12)
    else:
        prev_month = (year, month - 1)
        
    if month == 12:
        next_month = (year + 1, 1)
    else:
        next_month = (year, month + 1)
    
    month_name = start_date.strftime('%B %Y')
    
    return render_template(
        'orders/calendar.html',
        calendar_data=calendar_data,
        month_name=month_name,
        prev_month=prev_month,
        next_month=next_month,
        year=year,
        month=month,
        today=today
    )


@orders.route('/<int:order_id>/update_status', methods=['POST'])
@login_required
def update_status(order_id):
    """Update order status"""
    order = Order.query.get_or_404(order_id)
    
    try:
        new_status = OrderStatus[request.form.get('status')]
        
        if order.can_transition_to(new_status):
            order.status = new_status
            order.updated_at = datetime.utcnow()
            db.session.commit()
            flash(f'Order status updated to {order.get_status_label()}', 'success')
        else:
            flash(f'Cannot transition order from {order.get_status_label()} to {OrderStatus.LABELS[new_status]}', 'error')
    except KeyError:
        flash('Invalid status', 'error')
    
    return redirect(url_for('orders.view_order', order_id=order_id))


@orders.route('/<int:order_id>/add_item', methods=['POST'])
@login_required
def add_item(order_id):
    """Add item to an order"""
    order = Order.query.get_or_404(order_id)
    
    product_id = request.form.get('product_id')
    plant_name = request.form.get('plant_name')
    size = request.form.get('size', '')
    quantity = request.form.get('quantity', 1)
    price = request.form.get('price', 0.0)
    notes = request.form.get('notes', '')
    update_price_list = request.form.get('update_price_list') == 'on'
    
    # Validate required fields
    if not plant_name:
        flash('Plant name is required', 'error')
        return redirect(url_for('orders.view_order', order_id=order_id))
    
    try:
        quantity = int(quantity)
        price = float(price)
    except ValueError:
        flash('Invalid quantity or price', 'error')
        return redirect(url_for('orders.view_order', order_id=order_id))
    
    # Create the order item
    new_item = OrderItem(
        order_id=order_id,
        product_id=product_id if product_id else None,
        plant_name=plant_name,
        size=size,
        quantity=quantity,
        price=price,
        notes=notes,
        updated_price_list=False  # Will be updated below if needed
    )
    
    db.session.add(new_item)
    db.session.commit()
    
    # Update customer's price list if requested
    if update_price_list and order.customer_id:
        # Get or create customer's price list
        price_list = PriceList.query.filter_by(
            customer_id=order.customer_id,
            is_active=True
        ).order_by(desc(PriceList.created_at)).first()
        
        if not price_list:
            price_list = PriceList(
                name=f"{order.customer.name}'s Price List",
                customer_id=order.customer_id,
                is_active=True
            )
            db.session.add(price_list)
            db.session.commit()
        
        # Check if this product is already in the price list
        existing_item = None
        if product_id:
            existing_item = PriceListItem.query.filter_by(
                price_list_id=price_list.id,
                product_id=product_id
            ).first()
        
        # If not found by product_id, try to find by name and size
        if not existing_item:
            existing_item = PriceListItem.query.filter(
                PriceListItem.price_list_id == price_list.id,
                func.lower(PriceListItem.name) == func.lower(plant_name),
                func.lower(PriceListItem.size) == func.lower(size)
            ).first()
        
        if existing_item:
            # Update existing price list item
            existing_item.price = price
            existing_item.updated_at = datetime.utcnow()
        else:
            # Create new price list item
            new_price_item = PriceListItem(
                price_list_id=price_list.id,
                product_id=product_id if product_id else None,
                name=plant_name,
                size=size,
                price=price
            )
            db.session.add(new_price_item)
        
        # Mark the order item as having updated the price list
        new_item.updated_price_list = True
        db.session.commit()
        
        flash('Item added and customer price list updated', 'success')
    else:
        flash('Item added to order', 'success')
    
    return redirect(url_for('orders.view_order', order_id=order_id))


@orders.route('/<int:order_id>/remove_item/<int:item_id>', methods=['POST'])
@login_required
def remove_item(order_id, item_id):
    """Remove item from an order"""
    order = Order.query.get_or_404(order_id)
    item = OrderItem.query.get_or_404(item_id)
    
    if item.order_id != order.id:
        flash('Item does not belong to this order', 'error')
        return redirect(url_for('orders.view_order', order_id=order_id))
    
    db.session.delete(item)
    db.session.commit()
    
    flash('Item removed from order', 'success')
    return redirect(url_for('orders.view_order', order_id=order_id))


@orders.route('/<int:order_id>/edit', methods=['POST'])
@login_required
def edit_order(order_id):
    """Edit order details"""
    order = Order.query.get_or_404(order_id)
    
    # Get form data
    delivery_date_str = request.form.get('delivery_date')
    notes = request.form.get('notes', '')
    
    # Update fields
    if delivery_date_str:
        try:
            delivery_date = datetime.strptime(delivery_date_str, '%Y-%m-%d').date()
            order.delivery_date = delivery_date
        except ValueError:
            flash('Invalid delivery date format', 'error')
    
    order.notes = notes
    order.updated_at = datetime.utcnow()
    db.session.commit()
    
    flash('Order updated successfully', 'success')
    return redirect(url_for('orders.view_order', order_id=order_id))


@orders.route('/api/get_product/<int:product_id>', methods=['GET'])
@login_required
def get_product(product_id):
    """API to get product details including price from customer's price list"""
    product = Product.query.get_or_404(product_id)
    customer_id = request.args.get('customer_id')
    
    response = {
        'id': product.id,
        'name': product.name,
        'size': product.size or '',
        'price': product.price or 0.0
    }
    
    # If customer_id is provided, check for customer-specific price
    if customer_id and customer_id.isdigit():
        price_list = PriceList.query.filter_by(
            customer_id=int(customer_id),
            is_active=True
        ).order_by(desc(PriceList.created_at)).first()
        
        if price_list:
            # Check if this product is in the price list
            price_item = PriceListItem.query.filter_by(
                price_list_id=price_list.id,
                product_id=product.id
            ).first()
            
            if price_item:
                response['price'] = price_item.price
    
    return jsonify(response)


@orders.route('/delivery_notes/<int:order_id>', methods=['GET'])
@login_required
def delivery_notes(order_id):
    """Generate delivery notes for an order"""
    order = Order.query.get_or_404(order_id)
    
    # Get language preference from query param, default to English
    language = request.args.get('language', 'en')
    # Set language for translations in the template
    g.language = language
    
    return render_template(
        'pdfs/delivery_note.html',
        order=order,
        language=language
    )


@orders.route('/pdf/delivery_notes/<int:order_id>', methods=['GET'])
@login_required
def pdf_delivery_notes(order_id):
    """Generate PDF delivery notes for an order"""
    from weasyprint import HTML, CSS
    from flask import make_response
    from io import BytesIO
    import os
    
    order = Order.query.get_or_404(order_id)
    
    # Get language preference from query param, default to English
    language = request.args.get('language', 'en')
    # Set language for translations in the template
    g.language = language
    
    # Generate HTML for the delivery note
    html_content = render_template(
        'pdfs/delivery_note.html',
        order=order,
        language=language,
        is_pdf=True
    )
    
    # Define static folder path for CSS and assets
    static_folder = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'static')
    
    # Create WeasyPrint HTML object
    html = HTML(string=html_content, base_url=static_folder)
    
    # Generate PDF
    pdf_file = BytesIO()
    html.write_pdf(pdf_file)
    pdf_file.seek(0)
    
    # Create response
    response = make_response(pdf_file.getvalue())
    response.headers['Content-Type'] = 'application/pdf'
    response.headers['Content-Disposition'] = f'attachment; filename=delivery_note_{order.order_number}.pdf'
    
    return response
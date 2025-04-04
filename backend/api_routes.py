"""
API Routes Module
---------------
This module provides API endpoints for the frontend to interact with the backend.
"""

from flask import Blueprint, jsonify, request, current_app
from flask_login import login_user, current_user, logout_user, login_required
from werkzeug.security import check_password_hash
from backend.models import User, Customer, Product, Quotation, Invoice, PriceList, db

# Create the API blueprint
api_bp = Blueprint('api', __name__, url_prefix='/api')

def register_api_routes(app):
    """Register API routes with the application"""
    app.register_blueprint(api_bp)
    current_app.logger.info("API routes registered")

# Authentication routes
@api_bp.route('/auth/login', methods=['POST'])
def login():
    """API endpoint for user login"""
    data = request.get_json()
    
    if not data or 'username' not in data or 'password' not in data:
        return jsonify({'success': False, 'message': 'Missing username or password'}), 400
    
    user = User.query.filter_by(username=data['username']).first()
    
    if user and user.check_password(data['password']):
        login_user(user)
        return jsonify({
            'success': True,
            'user': {
                'id': user.id,
                'username': user.username,
                'is_admin': user.is_admin
            }
        })
    
    return jsonify({'success': False, 'message': 'Invalid username or password'}), 401

@api_bp.route('/auth/logout', methods=['POST'])
@login_required
def logout():
    """API endpoint for user logout"""
    logout_user()
    return jsonify({'success': True})

@api_bp.route('/auth/user', methods=['GET'])
def get_user():
    """Get the current user's information"""
    if current_user.is_authenticated:
        return jsonify({
            'authenticated': True,
            'user': {
                'id': current_user.id,
                'username': current_user.username,
                'is_admin': current_user.is_admin
            }
        })
    
    return jsonify({'authenticated': False}), 401

# Customer APIs
@api_bp.route('/customers', methods=['GET'])
@login_required
def get_customers():
    """Get all customers"""
    customers = Customer.query.all()
    return jsonify({
        'customers': [
            {
                'id': c.id,
                'name': c.name,
                'email': c.email,
                'phone': c.phone,
                'address': c.address
            } for c in customers
        ]
    })

@api_bp.route('/customers/<int:customer_id>', methods=['GET'])
@login_required
def get_customer(customer_id):
    """Get a specific customer by ID"""
    customer = Customer.query.get_or_404(customer_id)
    return jsonify({
        'id': customer.id,
        'name': customer.name,
        'email': customer.email,
        'phone': customer.phone,
        'address': customer.address
    })

# Product APIs
@api_bp.route('/products', methods=['GET'])
@login_required
def get_products():
    """Get all products"""
    products = Product.query.all()
    return jsonify({
        'products': [
            {
                'id': p.id,
                'name': p.name,
                'scientific_name': p.scientific_name,
                'category': p.category,
                'pot': p.pot,
                'sku': p.sku
            } for p in products
        ]
    })

@api_bp.route('/products/<int:product_id>', methods=['GET'])
@login_required
def get_product(product_id):
    """Get a specific product by ID"""
    product = Product.query.get_or_404(product_id)
    return jsonify({
        'id': product.id,
        'name': product.name,
        'scientific_name': product.scientific_name,
        'category': product.category,
        'pot': product.pot,
        'sku': product.sku,
        'description': product.description
    })

# Price List APIs
@api_bp.route('/price-lists', methods=['GET'])
@login_required
def get_price_lists():
    """Get price lists with filtering options"""
    customer_id = request.args.get('customer_id', type=int)
    product_id = request.args.get('product_id', type=int)
    
    query = PriceList.query
    
    if customer_id:
        query = query.filter_by(customer_id=customer_id)
    if product_id:
        query = query.filter_by(product_id=product_id)
    
    price_lists = query.all()
    
    return jsonify({
        'price_lists': [
            {
                'id': pl.id,
                'customer_id': pl.customer_id,
                'customer_name': pl.customer.name,
                'product_id': pl.product_id,
                'product_name': pl.product.name,
                'scientific_name': pl.product.scientific_name,
                'pot': pl.product.pot,
                'price': pl.price,
                'effective_date': pl.effective_date.isoformat() if pl.effective_date else None,
                'expiry_date': pl.expiry_date.isoformat() if pl.expiry_date else None
            } for pl in price_lists
        ]
    })

# Quotation APIs
@api_bp.route('/quotations', methods=['GET'])
@login_required
def get_quotations():
    """Get all quotations"""
    quotations = Quotation.query.all()
    return jsonify({
        'quotations': [
            {
                'id': q.id,
                'customer_id': q.customer_id,
                'customer_name': q.customer.name,
                'quotation_number': q.quotation_number,
                'quotation_date': q.quotation_date.isoformat(),
                'total_amount': q.total_amount,
                'currency': q.currency,
                'items_count': len(q.items)
            } for q in quotations
        ]
    })

@api_bp.route('/quotations/<int:quotation_id>', methods=['GET'])
@login_required
def get_quotation(quotation_id):
    """Get a specific quotation by ID"""
    quotation = Quotation.query.get_or_404(quotation_id)
    return jsonify({
        'id': quotation.id,
        'customer_id': quotation.customer_id,
        'customer_name': quotation.customer.name,
        'quotation_number': quotation.quotation_number,
        'quotation_date': quotation.quotation_date.isoformat(),
        'total_amount': quotation.total_amount,
        'currency': quotation.currency,
        'notes': quotation.notes,
        'items': [
            {
                'id': item.id,
                'product_id': item.product_id,
                'description': item.description,
                'scientific_name': item.scientific_name,
                'pot_size': item.pot_size,
                'height': item.height,
                'quantity': item.quantity,
                'selling_price': item.selling_price,
                'vat_rate': item.vat_rate,
                'supplier': item.supplier,
                'cost_price': item.cost_price,
                'total': item.total
            } for item in quotation.items
        ]
    })

# Invoice APIs
@api_bp.route('/invoices', methods=['GET'])
@login_required
def get_invoices():
    """Get all invoices"""
    invoices = Invoice.query.all()
    return jsonify({
        'invoices': [
            {
                'id': i.id,
                'customer_id': i.customer_id,
                'customer_name': i.customer.name,
                'invoice_number': i.invoice_number,
                'invoice_date': i.invoice_date.isoformat(),
                'total_amount': i.total_amount,
                'currency': i.currency,
                'items_count': len(i.items)
            } for i in invoices
        ]
    })

@api_bp.route('/invoices/<int:invoice_id>', methods=['GET'])
@login_required
def get_invoice(invoice_id):
    """Get a specific invoice by ID"""
    invoice = Invoice.query.get_or_404(invoice_id)
    return jsonify({
        'id': invoice.id,
        'customer_id': invoice.customer_id,
        'customer_name': invoice.customer.name,
        'invoice_number': invoice.invoice_number,
        'invoice_date': invoice.invoice_date.isoformat(),
        'total_amount': invoice.total_amount,
        'currency': invoice.currency,
        'items': [
            {
                'id': item.id,
                'product_id': item.product_id,
                'description': item.description,
                'scientific_name': item.scientific_name,
                'pot_size': item.pot_size,
                'quantity': item.quantity,
                'price': item.price,
                'vat': item.vat,
                'vat_percentage': item.vat_percentage,
                'total': item.total
            } for item in invoice.items
        ]
    })

# Search API
@api_bp.route('/search', methods=['GET'])
@login_required
def search():
    """Search across products, customers, etc."""
    query = request.args.get('q', '')
    
    if not query or len(query) < 2:
        return jsonify({'results': {}}), 400
    
    # Search in products
    products = Product.query.filter(
        (Product.name.ilike(f'%{query}%')) |
        (Product.scientific_name.ilike(f'%{query}%')) |
        (Product.sku.ilike(f'%{query}%'))
    ).limit(10).all()
    
    # Search in customers
    customers = Customer.query.filter(
        (Customer.name.ilike(f'%{query}%')) |
        (Customer.email.ilike(f'%{query}%'))
    ).limit(10).all()
    
    return jsonify({
        'results': {
            'products': [
                {
                    'id': p.id,
                    'name': p.name,
                    'scientific_name': p.scientific_name,
                    'category': p.category,
                    'pot': p.pot
                } for p in products
            ],
            'customers': [
                {
                    'id': c.id,
                    'name': c.name,
                    'email': c.email
                } for c in customers
            ]
        }
    })
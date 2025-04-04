"""
API Routes for the Plant Pricing System
---------------------------------------
These routes handle API requests from the React frontend.
"""

from flask import Blueprint, jsonify, request, current_app
from flask_login import login_required, current_user
from backend.models import db, User, Customer, Product, PriceList, Invoice, Quotation, Supplier, SupplierProduct

# Import our custom logger
try:
    from utils.logger import logger
except ImportError:
    import logging
    logger = logging.getLogger("plant_pricing_system")

# Create a blueprint for API routes
api_bp = Blueprint('api', __name__, url_prefix='/api')

def register_api_routes(app):
    """Register the API routes with the app"""
    app.register_blueprint(api_bp)
    logger.info("API routes registered")

# API routes

@api_bp.route('/health', methods=['GET'])
def health_check():
    """Simple health check endpoint"""
    return jsonify({
        'status': 'ok',
        'message': 'Plant Pricing System API is operational'
    })

@api_bp.route('/auth/user', methods=['GET'])
def get_current_user():
    """Get the current authenticated user"""
    if current_user.is_authenticated:
        return jsonify({
            'authenticated': True,
            'user': {
                'id': current_user.id,
                'username': current_user.username,
                'is_admin': current_user.is_admin
            }
        })
    else:
        return jsonify({
            'authenticated': False
        })

# Customer endpoints
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
    """Get a specific customer"""
    customer = Customer.query.get_or_404(customer_id)
    return jsonify({
        'id': customer.id,
        'name': customer.name,
        'email': customer.email,
        'phone': customer.phone,
        'address': customer.address
    })

# Product endpoints
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
                'category': p.category,
                'scientific_name': p.scientific_name,
                'pot': p.pot,
                'sku': p.sku,
                'description': p.description
            } for p in products
        ]
    })

@api_bp.route('/products/<int:product_id>', methods=['GET'])
@login_required
def get_product(product_id):
    """Get a specific product"""
    product = Product.query.get_or_404(product_id)
    return jsonify({
        'id': product.id,
        'name': product.name,
        'category': product.category,
        'scientific_name': product.scientific_name,
        'pot': product.pot,
        'sku': product.sku,
        'description': product.description
    })

# Price list endpoints
@api_bp.route('/price-lists', methods=['GET'])
@login_required
def get_price_lists():
    """Get all price lists with filtering options"""
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

# Invoice endpoints
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
                'file_path': i.file_path
            } for i in invoices
        ]
    })

# Quotation endpoints
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
                'notes': q.notes,
                'file_path': q.file_path
            } for q in quotations
        ]
    })

# Supplier endpoints
@api_bp.route('/suppliers', methods=['GET'])
@login_required
def get_suppliers():
    """Get all suppliers"""
    suppliers = Supplier.query.all()
    return jsonify({
        'suppliers': [
            {
                'id': s.id,
                'name': s.name,
                'contact_person': s.contact_person,
                'email': s.email,
                'phone': s.phone,
                'address': s.address,
                'is_inhouse': s.is_inhouse
            } for s in suppliers
        ]
    })

# Supplier product endpoints
@api_bp.route('/supplier-products', methods=['GET'])
@login_required
def get_supplier_products():
    """Get all supplier products with filtering options"""
    supplier_id = request.args.get('supplier_id', type=int)
    
    query = SupplierProduct.query
    
    if supplier_id:
        query = query.filter_by(supplier_id=supplier_id)
    
    supplier_products = query.all()
    
    return jsonify({
        'supplier_products': [
            {
                'id': sp.id,
                'supplier_id': sp.supplier_id,
                'supplier_name': sp.supplier.name,
                'product_name': sp.product_name,
                'scientific_name': sp.scientific_name,
                'height': sp.height,
                'pot_size': sp.pot_size,
                'price': sp.price,
                'cost_price': sp.cost_price
            } for sp in supplier_products
        ]
    })

# Search endpoint
@api_bp.route('/search', methods=['GET'])
@login_required
def search():
    """Search products and customers"""
    query = request.args.get('query', '')
    
    if not query:
        return jsonify({
            'products': [],
            'customers': []
        })
    
    # Search for products
    products = Product.query.filter(
        (Product.name.ilike(f'%{query}%')) | 
        (Product.scientific_name.ilike(f'%{query}%')) |
        (Product.description.ilike(f'%{query}%')) |
        (Product.category.ilike(f'%{query}%'))
    ).limit(10).all()
    
    # Search for customers
    customers = Customer.query.filter(
        (Customer.name.ilike(f'%{query}%')) | 
        (Customer.email.ilike(f'%{query}%'))
    ).limit(10).all()
    
    return jsonify({
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
    })
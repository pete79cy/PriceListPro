"""
API Blueprint for Quotation Management.
Provides endpoints for creating and retrieving quotations via JSON.
"""
import os
from flask import Blueprint, request, jsonify, current_app, abort, render_template
from flask_httpauth import HTTPTokenAuth
from app import db
from models import Quotation, QuotationItem, QuotationItemSizeOption, Customer, Product, Supplier, SupplierProduct
from utils.logger import logger, log_api_request
from datetime import datetime

# Create Blueprint and auth handler
auth = HTTPTokenAuth(scheme="Bearer")
api = Blueprint("api", __name__, url_prefix="/api/v1")

# Verify token function
@auth.verify_token
def verify_token(token):
    """
    Verify the API token against the configured token.
    Returns True if the token is valid, False otherwise.
    """
    api_token = current_app.config.get("API_TOKEN") or os.environ.get("API_TOKEN")
    if not api_token:
        logger.warning("API_TOKEN not configured - API endpoints will be inaccessible")
        return False
    
    valid = token == api_token
    if not valid:
        logger.warning(f"Invalid API token attempt: {token[:5]}...")
    return valid

# Helper Functions
def generate_quotation_number():
    """
    Generate a unique quotation number with format: PAK-YYYY-XXX
    Where YYYY is current year and XXX is a sequential number.
    """
    year = datetime.now().year
    prefix = f"PAK-{year}-"
    
    # Find the highest number for this year
    latest = Quotation.query.filter(
        Quotation.quotation_number.like(f"{prefix}%")
    ).order_by(
        Quotation.quotation_number.desc()
    ).first()
    
    if latest:
        try:
            number = int(latest.quotation_number.split('-')[-1])
            new_number = number + 1
        except (ValueError, IndexError):
            new_number = 1
    else:
        new_number = 1
    
    return f"{prefix}{new_number:03d}"

def make_quotation_response(quotation):
    """
    Create a standardized response for quotation operations.
    """
    return {
        "status": "success",
        "quotation_id": quotation.id,
        "quotation_number": quotation.quotation_number,
        "edit_url": f"/quotations/{quotation.id}"
    }

def get_or_create_customer(customer_data):
    """
    Get an existing customer or create a new one if not found.
    """
    if not customer_data or not customer_data.get("name"):
        return None
    
    # Try to find by name
    customer = Customer.query.filter_by(name=customer_data["name"]).first()
    
    if not customer:
        # Create new customer
        customer = Customer(
            name=customer_data["name"],
            email=customer_data.get("email"),
            phone=customer_data.get("phone"),
            address=customer_data.get("address")
        )
        db.session.add(customer)
        db.session.flush()  # Get customer.id
    
    return customer

def _find_supplier_products(item):
    """
    Find matching supplier products for a quotation item.
    Searches by product name/description and optional pot_size/height.
    Returns a list of supplier options with cost prices.
    """
    if not item.description:
        return []
    
    search_term = f"%{item.description}%"
    query = SupplierProduct.query.join(Supplier).filter(
        SupplierProduct.product_name.ilike(search_term)
    )
    
    if item.pot_size:
        query = query.filter(SupplierProduct.pot_size == item.pot_size)
    if item.height:
        query = query.filter(SupplierProduct.height == item.height)
    
    matches = query.all()
    
    if not matches:
        query = SupplierProduct.query.join(Supplier).filter(
            SupplierProduct.product_name.ilike(search_term)
        )
        matches = query.all()
    
    if not matches and item.scientific_name:
        sci_term = f"%{item.scientific_name}%"
        query = SupplierProduct.query.join(Supplier).filter(
            SupplierProduct.scientific_name.ilike(sci_term)
        )
        if item.pot_size:
            query = query.filter(SupplierProduct.pot_size == item.pot_size)
        if item.height:
            query = query.filter(SupplierProduct.height == item.height)
        matches = query.all()
        
        if not matches and item.scientific_name:
            query = SupplierProduct.query.join(Supplier).filter(
                SupplierProduct.scientific_name.ilike(sci_term)
            )
            matches = query.all()
    
    return [{
        "supplier_product_id": sp.id,
        "supplier_id": sp.supplier_id,
        "supplier_name": sp.supplier.name if sp.supplier else None,
        "is_inhouse": sp.supplier.is_inhouse if sp.supplier else False,
        "product_name": sp.product_name,
        "scientific_name": sp.scientific_name,
        "pot_size": sp.pot_size,
        "height": sp.height,
        "cost_price": sp.cost_price,
        "price": sp.price,
    } for sp in matches]


# API Routes
@api.route("/quotations", methods=["POST"])
@auth.login_required
@log_api_request
def create_quotation():
    """
    Create a new quotation from JSON data.
    
    Expected JSON format:
    {
        "customer": {
            "name": "Customer Name",
            "email": "customer@example.com",
            "phone": "+1234567890",
            "address": "Customer Address"
        },
        "items": [
            {
                "description": "Product Name",
                "scientific_name": "Scientific Name",
                "pot_size": "5L",
                "height": "30cm",
                "quantity": 5,
                "selling_price": 29.99,
                "vat_rate": 19.0
            }
        ],
        "currency": "€",
        "notes": "Additional notes about the quotation"
    }
    """
    data = request.get_json() or {}
    customer_data = data.get("customer", {})
    items_data = data.get("items", [])
    
    # Basic validation
    if not customer_data.get("name"):
        return jsonify({
            "status": "error", 
            "message": "Customer name is required"
        }), 400
    
    if not items_data:
        return jsonify({
            "status": "error", 
            "message": "At least one item is required"
        }), 400
    
    try:
        # Get or create customer
        customer = get_or_create_customer(customer_data)
        if not customer:
            return jsonify({
                "status": "error", 
                "message": "Could not create customer"
            }), 400
        
        # Create quotation
        quotation = Quotation(
            customer_id=customer.id,
            quotation_number=generate_quotation_number(),
            quotation_date=datetime.now().date(),
            currency=data.get("currency", "€"),
            notes=data.get("notes", "")
        )
        db.session.add(quotation)
        db.session.flush()  # Get quotation.id
        
        # Add items
        position = 0
        total_amount = 0
        
        for item_data in items_data:
            item = QuotationItem(
                quotation_id=quotation.id,
                description=item_data.get("description", "Unnamed Product"),
                scientific_name=item_data.get("scientific_name"),
                pot_size=item_data.get("pot_size"),
                height=item_data.get("height"),
                quantity=item_data.get("quantity", 1),
                selling_price=item_data.get("selling_price", 0),
                vat_rate=item_data.get("vat_rate", 19.0),
                position=position
            )
            
            # Calculate item total
            item.total = item.quantity * item.selling_price
            total_amount += item.total
            
            db.session.add(item)
            position += 1
        
        quotation.total_amount = total_amount
        db.session.commit()
        
        response = make_quotation_response(quotation)
        return jsonify(response), 201
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error creating quotation: {str(e)}")
        return jsonify({
            "status": "error", 
            "message": f"Error creating quotation: {str(e)}"
        }), 500

@api.route("/quotations/<quotation_number>", methods=["GET"])
@auth.login_required
@log_api_request
def get_quotation(quotation_number):
    """
    Retrieve a quotation by its quotation number.
    Returns full quotation details including supplier info, cost prices, and size options.
    """
    quotation = Quotation.query.filter_by(quotation_number=quotation_number).first()
    if not quotation:
        return jsonify({
            "status": "error", 
            "message": f"Quotation {quotation_number} not found"
        }), 404
    
    customer = Customer.query.get(quotation.customer_id)
    items = quotation.items
    
    items_data = []
    for item in items:
        item_dict = {
            "id": item.id,
            "description": item.description,
            "scientific_name": item.scientific_name,
            "pot_size": item.pot_size,
            "height": item.height,
            "quantity": item.quantity,
            "selling_price": item.selling_price,
            "cost_price": item.cost_price,
            "vat_rate": item.vat_rate,
            "total": item.total,
            "position": item.position,
            "pricing_status": item.pricing_status,
            "supplier_name": item.supplier,
            "supplier_id": item.supplier_id,
            "has_size_options": item.has_size_options,
        }
        
        if item.supplier_id:
            supplier_obj = Supplier.query.get(item.supplier_id)
            if supplier_obj:
                item_dict["supplier_details"] = {
                    "id": supplier_obj.id,
                    "name": supplier_obj.name,
                    "contact_person": supplier_obj.contact_person,
                    "email": supplier_obj.email,
                    "phone": supplier_obj.phone,
                    "is_inhouse": supplier_obj.is_inhouse,
                }
        
        if item.product_id:
            product_obj = Product.query.get(item.product_id)
            if product_obj:
                item_dict["product"] = {
                    "id": product_obj.id,
                    "name": product_obj.name,
                    "category": product_obj.category,
                    "sku": product_obj.sku,
                    "scientific_name": product_obj.scientific_name,
                }
        
        if item.has_size_options and item.size_options:
            item_dict["size_options"] = [{
                "id": opt.id,
                "size": opt.size,
                "price": opt.price,
                "cost_price": opt.cost_price,
                "supplier": opt.supplier,
                "is_default": opt.is_default,
                "position": opt.position,
                "notes": opt.notes,
            } for opt in item.size_options]
        
        supplier_products = _find_supplier_products(item)
        if supplier_products:
            item_dict["available_suppliers"] = supplier_products
        
        items_data.append(item_dict)
    
    response = {
        "status": "success",
        "quotation_id": quotation.id,
        "quotation_number": quotation.quotation_number,
        "quotation_date": quotation.quotation_date.isoformat() if quotation.quotation_date else None,
        "status_label": quotation.get_status_label(),
        "status_code": quotation.status,
        "valid_until": quotation.valid_until.isoformat() if quotation.valid_until else None,
        "customer": {
            "id": customer.id,
            "name": customer.name,
            "email": customer.email,
            "phone": customer.phone,
            "address": customer.address
        },
        "items": items_data,
        "currency": quotation.currency,
        "notes": quotation.notes,
        "internal_notes": quotation.internal_notes,
        "total_amount": quotation.total_amount,
        "created_at": quotation.created_at.isoformat() if quotation.created_at else None,
        "updated_at": quotation.updated_at.isoformat() if quotation.updated_at else None,
        "viewed_at": quotation.viewed_at.isoformat() if quotation.viewed_at else None,
        "accepted_at": quotation.accepted_at.isoformat() if quotation.accepted_at else None,
        "edit_url": f"/quotations/{quotation.id}"
    }
    
    return jsonify(response), 200

@api.route("/quotations", methods=["GET"])
@auth.login_required
@log_api_request
def list_quotations():
    """
    List all quotations with full details, optional filtering by customer_id and status.
    Returns quotations with items, suppliers, and cost prices.
    """
    customer_id = request.args.get("customer_id")
    status = request.args.get("status")
    limit = request.args.get("limit", 50, type=int)
    offset = request.args.get("offset", 0, type=int)
    
    query = Quotation.query
    
    if customer_id:
        query = query.filter_by(customer_id=customer_id)
    if status:
        query = query.filter_by(status=status)
    
    total_count = query.count()
    quotations = query.order_by(Quotation.created_at.desc()).limit(limit).offset(offset).all()
    
    results = []
    for quotation in quotations:
        items_summary = []
        for item in quotation.items:
            item_data = {
                "id": item.id,
                "description": item.description,
                "scientific_name": item.scientific_name,
                "pot_size": item.pot_size,
                "height": item.height,
                "quantity": item.quantity,
                "selling_price": item.selling_price,
                "cost_price": item.cost_price,
                "vat_rate": item.vat_rate,
                "total": item.total,
                "pricing_status": item.pricing_status,
                "supplier_name": item.supplier,
                "supplier_id": item.supplier_id,
            }
            items_summary.append(item_data)
        
        quotation_data = {
            "id": quotation.id,
            "quotation_number": quotation.quotation_number,
            "status_code": quotation.status,
            "status_label": quotation.get_status_label(),
            "customer": {
                "id": quotation.customer.id,
                "name": quotation.customer.name,
            } if quotation.customer else {"id": None, "name": "Unknown"},
            "quotation_date": quotation.quotation_date.isoformat() if quotation.quotation_date else None,
            "valid_until": quotation.valid_until.isoformat() if quotation.valid_until else None,
            "total_amount": quotation.total_amount,
            "currency": quotation.currency,
            "item_count": len(quotation.items),
            "items": items_summary,
            "notes": quotation.notes,
            "created_at": quotation.created_at.isoformat() if quotation.created_at else None,
            "updated_at": quotation.updated_at.isoformat() if quotation.updated_at else None,
        }
        results.append(quotation_data)
    
    response = {
        "status": "success",
        "count": len(results),
        "total": total_count,
        "limit": limit,
        "offset": offset,
        "quotations": results
    }
    
    return jsonify(response), 200

@api.route("/products", methods=["GET"])
def search_products():
    """
    Search products endpoint for the add item modal.
    No authentication required for internal use.
    """
    search_query = request.args.get('search', '').strip()
    limit = request.args.get('limit', 50, type=int)
    
    # Start with base query
    query = Product.query
    
    # Apply search filter if provided
    if search_query:
        search_term = f"%{search_query}%"
        query = query.filter(
            db.or_(
                Product.name.ilike(search_term),
                Product.category.ilike(search_term),
                Product.pot.ilike(search_term),
                Product.sku.ilike(search_term),
                Product.scientific_name.ilike(search_term),
                Product.description.ilike(search_term)
            )
        )
    
    # Get results with limit
    products = query.order_by(Product.name).limit(limit).all()
    
    # Format response
    results = []
    for product in products:
        results.append({
            'id': product.id,
            'name': product.name,
            'category': product.category or '',
            'pot': product.pot or '',
            'sku': product.sku or '',
            'scientific_name': product.scientific_name or '',
            'description': product.description or ''
        })
    
    return jsonify(results), 200

# Route for API documentation
@api.route("/", methods=["GET"])
def api_documentation():
    """
    Show API documentation.
    """
    # Show HTML documentation page
    if request.headers.get('Accept', '').find('text/html') >= 0 or \
       request.headers.get('User-Agent', '').find('Mozilla') >= 0:
        return render_template('api_docs.html')
    
    # Return JSON if requested via API client
    return jsonify({
        "status": "success",
        "message": "Plant Pricing System API v1",
        "endpoints": [
            {"method": "POST", "path": "/api/v1/quotations", "description": "Create a new quotation"},
            {"method": "GET", "path": "/api/v1/quotations", "description": "List all quotations"},
            {"method": "GET", "path": "/api/v1/quotations/{quotation_number}", "description": "Get a specific quotation"}
        ]
    }), 200
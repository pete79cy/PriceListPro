"""
API Blueprint for Quotation Management.
Provides endpoints for creating and retrieving quotations via JSON.
"""
import os
from flask import Blueprint, request, jsonify, current_app, abort, render_template
from flask_httpauth import HTTPTokenAuth
from app import db
from models import (Quotation, QuotationItem, QuotationItemSizeOption, Customer, CustomerCategory,
                    CustomerContact, Product, Supplier, SupplierProduct, Order, OrderItem,
                    Invoice, InvoiceItem, PriceList, CompanySettings)
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
                "cost_price": 15.00,
                "vat_rate": 19.0,
                "supplier_id": 2,
                "supplier": "Supplier Name",
                "product_id": null,
                "pricing_status": "CONFIRMED"
            }
        ],
        "currency": "€",
        "notes": "Additional notes about the quotation",
        "internal_notes": "Internal notes for staff",
        "valid_until": "2026-03-31",
        "status": "DRAFT"
    }
    """
    data = request.get_json() or {}
    customer_data = data.get("customer", {})
    items_data = data.get("items", [])
    
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
        customer = get_or_create_customer(customer_data)
        if not customer:
            return jsonify({
                "status": "error", 
                "message": "Could not create customer"
            }), 400
        
        valid_until = None
        if data.get("valid_until"):
            try:
                valid_until = datetime.strptime(data["valid_until"], "%Y-%m-%d").date()
            except ValueError:
                pass
        
        quotation = Quotation(
            customer_id=customer.id,
            quotation_number=generate_quotation_number(),
            quotation_date=datetime.now().date(),
            currency=data.get("currency", "€"),
            notes=data.get("notes", ""),
            internal_notes=data.get("internal_notes"),
            valid_until=valid_until,
            status=data.get("status", "DRAFT")
        )
        db.session.add(quotation)
        db.session.flush()
        
        position = 0
        total_amount = 0
        items_created = []
        
        for item_data in items_data:
            selling_price = item_data.get("selling_price") or 0
            quantity = item_data.get("quantity", 1)
            cost_price = item_data.get("cost_price")
            supplier_id = item_data.get("supplier_id")
            supplier_name = item_data.get("supplier", "")
            pricing_status = item_data.get("pricing_status", "CONFIRMED")
            
            if supplier_id:
                supplier_obj = Supplier.query.get(supplier_id)
                if supplier_obj and not supplier_name:
                    supplier_name = supplier_obj.name
            
            if selling_price == 0 and pricing_status == "CONFIRMED":
                pricing_status = "PENDING"
            
            item = QuotationItem(
                quotation_id=quotation.id,
                product_id=item_data.get("product_id"),
                description=item_data.get("description", "Unnamed Product"),
                scientific_name=item_data.get("scientific_name"),
                pot_size=item_data.get("pot_size"),
                height=item_data.get("height"),
                quantity=quantity,
                selling_price=selling_price,
                cost_price=cost_price,
                vat_rate=item_data.get("vat_rate", 19.0),
                supplier=supplier_name,
                supplier_id=supplier_id,
                pricing_status=pricing_status,
                position=position
            )
            
            item.total = quantity * selling_price
            total_amount += item.total
            
            db.session.add(item)
            db.session.flush()
            
            items_created.append({
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
                "position": item.position,
            })
            position += 1
        
        quotation.total_amount = total_amount
        db.session.commit()
        
        response = {
            "status": "success",
            "quotation_id": quotation.id,
            "quotation_number": quotation.quotation_number,
            "quotation_date": quotation.quotation_date.isoformat(),
            "status_code": quotation.status,
            "status_label": quotation.get_status_label(),
            "customer": {
                "id": customer.id,
                "name": customer.name,
            },
            "items": items_created,
            "total_amount": total_amount,
            "currency": quotation.currency,
            "notes": quotation.notes,
            "internal_notes": quotation.internal_notes,
            "valid_until": quotation.valid_until.isoformat() if quotation.valid_until else None,
            "edit_url": f"/quotations/{quotation.id}",
        }
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

# ── CUSTOMERS ──────────────────────────────────────────────────────────────

@api.route("/customers", methods=["GET"])
@auth.login_required
@log_api_request
def list_customers():
    search = request.args.get("search", "").strip()
    category_id = request.args.get("category_id")
    limit = request.args.get("limit", 100, type=int)
    offset = request.args.get("offset", 0, type=int)

    query = Customer.query
    if search:
        query = query.filter(
            db.or_(
                Customer.name.ilike(f"%{search}%"),
                Customer.email.ilike(f"%{search}%"),
                Customer.phone.ilike(f"%{search}%"),
            )
        )
    if category_id:
        query = query.filter_by(category_id=category_id)

    total = query.count()
    customers = query.order_by(Customer.name).limit(limit).offset(offset).all()

    results = []
    for c in customers:
        results.append({
            "id": c.id,
            "name": c.name,
            "email": c.email,
            "phone": c.phone,
            "address": c.address,
            "category_id": c.category_id,
            "category_name": c.category.name if c.category else None,
            "created_at": c.created_at.isoformat() if c.created_at else None,
            "updated_at": c.updated_at.isoformat() if c.updated_at else None,
        })

    return jsonify({"status": "success", "total": total, "count": len(results),
                    "limit": limit, "offset": offset, "customers": results}), 200


@api.route("/customers/<int:customer_id>", methods=["GET"])
@auth.login_required
@log_api_request
def get_customer(customer_id):
    c = Customer.query.get_or_404(customer_id)

    contacts = [{
        "id": ct.id,
        "contact_date": ct.contact_date.isoformat() if ct.contact_date else None,
        "contact_type": ct.contact_type,
        "notes": ct.notes,
    } for ct in c.contacts]

    quotations_summary = [{
        "id": q.id,
        "quotation_number": q.quotation_number,
        "status": q.status,
        "status_label": q.get_status_label(),
        "total_amount": q.total_amount,
        "currency": q.currency,
        "quotation_date": q.quotation_date.isoformat() if q.quotation_date else None,
    } for q in c.quotations]

    orders_summary = [{
        "id": o.id,
        "order_number": o.order_number,
        "status": o.status,
        "status_label": o.get_status_label(),
        "delivery_date": o.delivery_date.isoformat() if o.delivery_date else None,
        "total": float(o.total),
    } for o in c.customer_orders]

    return jsonify({
        "status": "success",
        "id": c.id,
        "name": c.name,
        "email": c.email,
        "phone": c.phone,
        "address": c.address,
        "category_id": c.category_id,
        "category_name": c.category.name if c.category else None,
        "created_at": c.created_at.isoformat() if c.created_at else None,
        "updated_at": c.updated_at.isoformat() if c.updated_at else None,
        "contacts": contacts,
        "quotations": quotations_summary,
        "orders": orders_summary,
    }), 200


# ── SUPPLIERS ──────────────────────────────────────────────────────────────

@api.route("/suppliers", methods=["GET"])
@auth.login_required
@log_api_request
def list_suppliers():
    search = request.args.get("search", "").strip()
    is_inhouse = request.args.get("is_inhouse")
    limit = request.args.get("limit", 100, type=int)
    offset = request.args.get("offset", 0, type=int)

    query = Supplier.query
    if search:
        query = query.filter(
            db.or_(
                Supplier.name.ilike(f"%{search}%"),
                Supplier.contact_person.ilike(f"%{search}%"),
                Supplier.email.ilike(f"%{search}%"),
            )
        )
    if is_inhouse is not None:
        query = query.filter_by(is_inhouse=(is_inhouse.lower() == "true"))

    total = query.count()
    suppliers = query.order_by(Supplier.name).limit(limit).offset(offset).all()

    return jsonify({
        "status": "success",
        "total": total,
        "count": len(suppliers),
        "limit": limit,
        "offset": offset,
        "suppliers": [s.to_dict() for s in suppliers],
    }), 200


@api.route("/suppliers/<int:supplier_id>", methods=["GET"])
@auth.login_required
@log_api_request
def get_supplier(supplier_id):
    s = Supplier.query.get_or_404(supplier_id)
    data = s.to_dict()
    data["products"] = [{
        "id": sp.id,
        "product_name": sp.product_name,
        "scientific_name": sp.scientific_name,
        "pot_size": sp.pot_size,
        "height": sp.height,
        "price": sp.price,
        "cost_price": sp.cost_price,
        "notes": sp.notes,
        "flagged_duplicate": sp.flagged_duplicate,
        "last_detected": sp.last_detected.isoformat() if sp.last_detected else None,
    } for sp in s.products]
    return jsonify({"status": "success", **data}), 200


@api.route("/suppliers/<int:supplier_id>/products", methods=["GET"])
@auth.login_required
@log_api_request
def get_supplier_products(supplier_id):
    s = Supplier.query.get_or_404(supplier_id)
    search = request.args.get("search", "").strip()
    limit = request.args.get("limit", 200, type=int)
    offset = request.args.get("offset", 0, type=int)

    query = SupplierProduct.query.filter_by(supplier_id=supplier_id)
    if search:
        query = query.filter(SupplierProduct.product_name.ilike(f"%{search}%"))

    total = query.count()
    products = query.order_by(SupplierProduct.product_name).limit(limit).offset(offset).all()

    results = [{
        "id": sp.id,
        "product_name": sp.product_name,
        "scientific_name": sp.scientific_name,
        "pot_size": sp.pot_size,
        "height": sp.height,
        "price": sp.price,
        "cost_price": sp.cost_price,
        "notes": sp.notes,
        "flagged_duplicate": sp.flagged_duplicate,
        "last_detected": sp.last_detected.isoformat() if sp.last_detected else None,
    } for sp in products]

    return jsonify({
        "status": "success",
        "supplier_id": supplier_id,
        "supplier_name": s.name,
        "total": total,
        "count": len(results),
        "limit": limit,
        "offset": offset,
        "products": results,
    }), 200


# ── ORDERS ─────────────────────────────────────────────────────────────────

@api.route("/orders", methods=["GET"])
@auth.login_required
@log_api_request
def list_orders():
    status = request.args.get("status")
    customer_id = request.args.get("customer_id")
    limit = request.args.get("limit", 50, type=int)
    offset = request.args.get("offset", 0, type=int)

    query = Order.query
    if status:
        query = query.filter_by(status=status)
    if customer_id:
        query = query.filter_by(customer_id=customer_id)

    total = query.count()
    orders = query.order_by(Order.created_at.desc()).limit(limit).offset(offset).all()

    results = []
    for o in orders:
        results.append({
            "id": o.id,
            "order_number": o.order_number,
            "status": o.status,
            "status_label": o.get_status_label(),
            "customer": {
                "id": o.customer.id,
                "name": o.customer.name,
            } if o.customer else None,
            "delivery_date": o.delivery_date.isoformat() if o.delivery_date else None,
            "item_count": len(o.items),
            "subtotal": float(o.subtotal),
            "discount_type": o.discount_type,
            "discount_percentage": o.discount_percentage,
            "discount_amount": float(o.discount_amount),
            "discount_value": float(o.discount_value),
            "vat_amount": float(o.vat_amount),
            "total": float(o.total),
            "notes": o.notes,
            "created_at": o.created_at.isoformat() if o.created_at else None,
            "updated_at": o.updated_at.isoformat() if o.updated_at else None,
        })

    return jsonify({"status": "success", "total": total, "count": len(results),
                    "limit": limit, "offset": offset, "orders": results}), 200


@api.route("/orders/<order_number>", methods=["GET"])
@auth.login_required
@log_api_request
def get_order(order_number):
    o = Order.query.filter_by(order_number=order_number).first()
    if not o:
        return jsonify({"status": "error", "message": f"Order {order_number} not found"}), 404

    items = [{
        "id": item.id,
        "plant_name": item.plant_name,
        "size": item.size,
        "quantity": item.quantity,
        "price": item.price,
        "vat_rate": item.vat_rate,
        "net_total": float(item.net_total),
        "vat_amount": float(item.vat_amount),
        "gross_total": float(item.gross_total),
        "notes": item.notes,
        "product_id": item.product_id,
    } for item in o.items]

    return jsonify({
        "status": "success",
        "id": o.id,
        "order_number": o.order_number,
        "status": o.status,
        "status_label": o.get_status_label(),
        "customer": {
            "id": o.customer.id,
            "name": o.customer.name,
            "email": o.customer.email,
            "phone": o.customer.phone,
        } if o.customer else None,
        "delivery_date": o.delivery_date.isoformat() if o.delivery_date else None,
        "notes": o.notes,
        "discount_type": o.discount_type,
        "discount_percentage": o.discount_percentage,
        "discount_amount": float(o.discount_amount),
        "discount_value": float(o.discount_value),
        "subtotal": float(o.subtotal),
        "vat_amount": float(o.vat_amount),
        "total": float(o.total),
        "items": items,
        "created_at": o.created_at.isoformat() if o.created_at else None,
        "updated_at": o.updated_at.isoformat() if o.updated_at else None,
    }), 200


# ── INVOICES ───────────────────────────────────────────────────────────────

@api.route("/invoices", methods=["GET"])
@auth.login_required
@log_api_request
def list_invoices():
    customer_id = request.args.get("customer_id")
    limit = request.args.get("limit", 50, type=int)
    offset = request.args.get("offset", 0, type=int)

    query = Invoice.query
    if customer_id:
        query = query.filter_by(customer_id=customer_id)

    total = query.count()
    invoices = query.order_by(Invoice.invoice_date.desc()).limit(limit).offset(offset).all()

    results = []
    for inv in invoices:
        results.append({
            "id": inv.id,
            "invoice_number": inv.invoice_number,
            "invoice_date": inv.invoice_date.isoformat() if inv.invoice_date else None,
            "total_amount": inv.total_amount,
            "currency": inv.currency,
            "customer": {
                "id": inv.customer.id,
                "name": inv.customer.name,
            } if inv.customer else None,
            "item_count": len(inv.items),
            "created_at": inv.created_at.isoformat() if inv.created_at else None,
        })

    return jsonify({"status": "success", "total": total, "count": len(results),
                    "limit": limit, "offset": offset, "invoices": results}), 200


@api.route("/invoices/<invoice_number>", methods=["GET"])
@auth.login_required
@log_api_request
def get_invoice(invoice_number):
    inv = Invoice.query.filter_by(invoice_number=invoice_number).first()
    if not inv:
        return jsonify({"status": "error", "message": f"Invoice {invoice_number} not found"}), 404

    items = [{
        "id": item.id,
        "description": item.description,
        "scientific_name": item.scientific_name,
        "pot_size": item.pot_size,
        "quantity": item.quantity,
        "price": item.price,
        "vat": item.vat,
        "vat_percentage": item.vat_percentage,
        "total": item.total,
        "product_id": item.product_id,
    } for item in inv.items]

    return jsonify({
        "status": "success",
        "id": inv.id,
        "invoice_number": inv.invoice_number,
        "invoice_date": inv.invoice_date.isoformat() if inv.invoice_date else None,
        "total_amount": inv.total_amount,
        "currency": inv.currency,
        "customer": {
            "id": inv.customer.id,
            "name": inv.customer.name,
            "email": inv.customer.email,
            "phone": inv.customer.phone,
        } if inv.customer else None,
        "items": items,
        "created_at": inv.created_at.isoformat() if inv.created_at else None,
        "updated_at": inv.updated_at.isoformat() if inv.updated_at else None,
    }), 200


# ── PRICE LISTS ────────────────────────────────────────────────────────────

@api.route("/price-lists", methods=["GET"])
@auth.login_required
@log_api_request
def list_price_lists():
    customer_id = request.args.get("customer_id")
    product_id = request.args.get("product_id")
    limit = request.args.get("limit", 100, type=int)
    offset = request.args.get("offset", 0, type=int)

    query = PriceList.query
    if customer_id:
        query = query.filter_by(customer_id=customer_id)
    if product_id:
        query = query.filter_by(product_id=product_id)

    total = query.count()
    entries = query.order_by(PriceList.customer_id, PriceList.product_id).limit(limit).offset(offset).all()

    results = []
    for pl in entries:
        results.append({
            "id": pl.id,
            "customer_id": pl.customer_id,
            "customer_name": pl.customer.name if pl.customer else None,
            "product_id": pl.product_id,
            "product_name": pl.product.name if pl.product else None,
            "price": pl.price,
            "effective_date": pl.effective_date.isoformat() if pl.effective_date else None,
            "expiry_date": pl.expiry_date.isoformat() if pl.expiry_date else None,
            "source_file": pl.source_file,
            "created_at": pl.created_at.isoformat() if pl.created_at else None,
        })

    return jsonify({"status": "success", "total": total, "count": len(results),
                    "limit": limit, "offset": offset, "price_lists": results}), 200


# ── PRODUCTS (extended) ────────────────────────────────────────────────────

@api.route("/products/<int:product_id>", methods=["GET"])
@auth.login_required
@log_api_request
def get_product(product_id):
    p = Product.query.get_or_404(product_id)
    return jsonify({
        "status": "success",
        "id": p.id,
        "name": p.name,
        "category": p.category,
        "scientific_name": p.scientific_name,
        "pot": p.pot,
        "sku": p.sku,
        "description": p.description,
        "created_at": p.created_at.isoformat() if p.created_at else None,
        "updated_at": p.updated_at.isoformat() if p.updated_at else None,
    }), 200


# ── COMPANY SETTINGS ───────────────────────────────────────────────────────

@api.route("/company-settings", methods=["GET"])
@auth.login_required
@log_api_request
def get_company_settings():
    settings = CompanySettings.query.first()
    if not settings:
        return jsonify({"status": "error", "message": "No company settings found"}), 404

    return jsonify({
        "status": "success",
        "id": settings.id,
        "name": settings.name,
        "address_line1": settings.address_line1,
        "address_line2": settings.address_line2,
        "phone": settings.phone,
        "email": settings.email,
        "pdf_orientation": settings.pdf_orientation,
        "updated_at": settings.updated_at.isoformat() if settings.updated_at else None,
    }), 200


# ── API DOCUMENTATION ──────────────────────────────────────────────────────

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
        "authentication": "Bearer token required in Authorization header for all endpoints marked with *",
        "endpoints": [
            {"method": "POST", "path": "/api/v1/quotations", "auth": True, "description": "Create a new quotation"},
            {"method": "GET", "path": "/api/v1/quotations", "auth": True, "description": "List all quotations"},
            {"method": "GET", "path": "/api/v1/quotations/{quotation_number}", "auth": True, "description": "Get a specific quotation"},
            {"method": "GET", "path": "/api/v1/customers", "auth": True, "description": "List all customers"},
            {"method": "GET", "path": "/api/v1/customers/{id}", "auth": True, "description": "Get a specific customer"},
            {"method": "GET", "path": "/api/v1/suppliers", "auth": True, "description": "List all suppliers"},
            {"method": "GET", "path": "/api/v1/suppliers/{id}", "auth": True, "description": "Get a specific supplier with products"},
            {"method": "GET", "path": "/api/v1/suppliers/{id}/products", "auth": True, "description": "List products for a supplier"},
            {"method": "GET", "path": "/api/v1/orders", "auth": True, "description": "List all orders"},
            {"method": "GET", "path": "/api/v1/orders/{order_number}", "auth": True, "description": "Get a specific order"},
            {"method": "GET", "path": "/api/v1/invoices", "auth": True, "description": "List all invoices"},
            {"method": "GET", "path": "/api/v1/invoices/{invoice_number}", "auth": True, "description": "Get a specific invoice"},
            {"method": "GET", "path": "/api/v1/price-lists", "auth": True, "description": "List price list entries"},
            {"method": "GET", "path": "/api/v1/products", "auth": False, "description": "Search products (no auth required)"},
            {"method": "GET", "path": "/api/v1/products/{id}", "auth": True, "description": "Get a specific product"},
            {"method": "GET", "path": "/api/v1/company-settings", "auth": True, "description": "Get company settings"},
        ]
    }), 200
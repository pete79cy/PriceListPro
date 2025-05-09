"""
API Blueprint for Quotation Management.
Provides endpoints for creating and retrieving quotations via JSON.
"""
import os
from flask import Blueprint, request, jsonify, current_app, url_for, abort, render_template
from flask_httpauth import HTTPTokenAuth
from app import db
from models import Quotation, QuotationItem, Customer
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
        "edit_url": url_for("quotation.edit", quotation_id=quotation.id, _external=True)
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
    Returns the quotation details in JSON format.
    """
    quotation = Quotation.query.filter_by(quotation_number=quotation_number).first()
    if not quotation:
        return jsonify({
            "status": "error", 
            "message": f"Quotation {quotation_number} not found"
        }), 404
    
    # Get customer and items
    customer = Customer.query.get(quotation.customer_id)
    items = quotation.items
    
    # Format response
    items_data = []
    for item in items:
        items_data.append({
            "id": item.id,
            "description": item.description,
            "scientific_name": item.scientific_name,
            "pot_size": item.pot_size,
            "height": item.height,
            "quantity": item.quantity,
            "selling_price": item.selling_price,
            "vat_rate": item.vat_rate,
            "total": item.total,
            "position": item.position
        })
    
    response = {
        "status": "success",
        "quotation_id": quotation.id,
        "quotation_number": quotation.quotation_number,
        "quotation_date": quotation.quotation_date.isoformat() if quotation.quotation_date else None,
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
        "total_amount": quotation.total_amount,
        "created_at": quotation.created_at.isoformat() if quotation.created_at else None,
        "updated_at": quotation.updated_at.isoformat() if quotation.updated_at else None,
        "edit_url": url_for("quotation.edit", quotation_id=quotation.id, _external=True)
    }
    
    return jsonify(response), 200

@api.route("/quotations", methods=["GET"])
@auth.login_required
@log_api_request
def list_quotations():
    """
    List all quotations, with optional filtering by customer ID.
    Returns a list of quotations in JSON format.
    """
    customer_id = request.args.get("customer_id")
    limit = request.args.get("limit", 50, type=int)
    offset = request.args.get("offset", 0, type=int)
    
    # Build query
    query = Quotation.query
    
    if customer_id:
        query = query.filter_by(customer_id=customer_id)
    
    # Add sorting and pagination
    quotations = query.order_by(Quotation.created_at.desc()).limit(limit).offset(offset).all()
    
    # Format response
    results = []
    for quotation in quotations:
        results.append({
            "id": quotation.id,
            "quotation_number": quotation.quotation_number,
            "customer_name": quotation.customer.name if quotation.customer else "Unknown",
            "quotation_date": quotation.quotation_date.isoformat() if quotation.quotation_date else None,
            "total_amount": quotation.total_amount,
            "currency": quotation.currency,
            "item_count": len(quotation.items),
            "created_at": quotation.created_at.isoformat() if quotation.created_at else None
        })
    
    response = {
        "status": "success",
        "count": len(results),
        "quotations": results
    }
    
    return jsonify(response), 200

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
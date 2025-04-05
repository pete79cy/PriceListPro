import os
import re
import json
import logging
from flask import Blueprint, request, jsonify, url_for
from viberbot import Api
from viberbot.api.bot_configuration import BotConfiguration
from viberbot.api.messages import TextMessage
from viberbot.api.viber_requests import ViberConversationStartedRequest
from viberbot.api.viber_requests import ViberFailedRequest
from viberbot.api.viber_requests import ViberMessageRequest
from viberbot.api.viber_requests import ViberSubscribedRequest
from viberbot.api.viber_requests import ViberUnsubscribedRequest

from app import db
from models import Supplier, SupplierProduct

# Set up logging
logger = logging.getLogger(__name__)

# Initialize variables
VIBER_AUTH_TOKEN = os.environ.get('VIBER_AUTH_TOKEN')
VIBER_SUPPLIER_MAPPING = {}  # Map Viber IDs to supplier IDs

# Initialize Viber bot if token is available
viber_bot = None
if VIBER_AUTH_TOKEN:
    try:
        viber_bot = Api(BotConfiguration(
            name='SupplierPriceBot',
            avatar='https://raw.githubusercontent.com/devrelv/drop/master/151-icon.png',
            auth_token=VIBER_AUTH_TOKEN
        ))
        logger.info("Viber bot initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize Viber bot: {str(e)}")

# Create a Blueprint for Viber integration
viber_blueprint = Blueprint('viber', __name__)

def extract_product_info(message_text):
    """
    Extract product information from a Viber message text.
    
    Different suppliers might use different message formats, so this function can be
    customized with specific regex patterns or other extraction methods per supplier.
    
    Basic format example: 
    "Product: Plant name, Scientific name: Latin name, Size: 20cm, Pot: 17cm, Price: €10.50"
    
    Returns a dictionary with the extracted information or None if extraction failed.
    """
    try:
        # Define regex patterns for extraction
        patterns = {
            'product_name': r'Product:\s*([^,]+)',
            'scientific_name': r'Scientific name:\s*([^,]+)',
            'height': r'Size:\s*([^,]+)',
            'pot_size': r'Pot:\s*([^,]+)',
            'price': r'Price:\s*[€£$]?(\d+(?:\.\d+)?)'
        }
        
        # Extract information using regex
        extracted_info = {}
        for key, pattern in patterns.items():
            match = re.search(pattern, message_text, re.IGNORECASE)
            if match:
                extracted_info[key] = match.group(1).strip()
        
        # Check if required fields are present
        if 'product_name' in extracted_info and 'price' in extracted_info:
            # Convert price to float
            try:
                extracted_info['price'] = float(extracted_info['price'])
                return extracted_info
            except ValueError:
                logger.error(f"Failed to convert price to float: {extracted_info['price']}")
                return None
        else:
            logger.warning(f"Required fields missing in message: {message_text}")
            return None
            
    except Exception as e:
        logger.error(f"Error extracting product info: {str(e)}")
        return None

def get_supplier_id_from_viber(sender_id, conversation_id):
    """
    Map a Viber sender ID or conversation ID to a supplier ID in the database.
    
    Args:
        sender_id: The Viber ID of the sender
        conversation_id: The ID of the conversation/group
        
    Returns:
        int: The supplier ID from the database or None if not found
    """
    # First check if the conversation ID is mapped (for group chats)
    if conversation_id and conversation_id in VIBER_SUPPLIER_MAPPING:
        return VIBER_SUPPLIER_MAPPING[conversation_id]
    
    # Then check if the sender ID is mapped (for direct messages)
    if sender_id and sender_id in VIBER_SUPPLIER_MAPPING:
        return VIBER_SUPPLIER_MAPPING[sender_id]
    
    # No mapping found
    return None

def update_supplier_product(supplier_id, product_info):
    """
    Update or create a supplier product in the database based on message information.
    
    Args:
        supplier_id: ID of the supplier in the database
        product_info: Dictionary containing the extracted product information
        
    Returns:
        bool: True if the update was successful, False otherwise
    """
    try:
        # Validate required fields
        if not product_info or 'product_name' not in product_info or 'price' not in product_info:
            logger.error("Required product information missing")
            return False
        
        # Try to find an existing product by name for this supplier
        existing_product = SupplierProduct.query.filter_by(
            supplier_id=supplier_id,
            product_name=product_info['product_name']
        ).first()
        
        if existing_product:
            # Update existing product
            if 'scientific_name' in product_info:
                existing_product.scientific_name = product_info['scientific_name']
            if 'height' in product_info:
                existing_product.height = product_info['height']
            if 'pot_size' in product_info:
                existing_product.pot_size = product_info['pot_size']
            
            # Always update the price
            existing_product.price = float(product_info['price'])
            
            # Set the cost price the same as the price if it doesn't exist
            if not existing_product.cost_price:
                existing_product.cost_price = float(product_info['price'])
                
            db.session.commit()
            logger.info(f"Updated existing product: {product_info['product_name']} for supplier ID {supplier_id}")
            return True
        else:
            # Create new product
            new_product = SupplierProduct(
                supplier_id=supplier_id,
                product_name=product_info['product_name'],
                price=float(product_info['price']),
                cost_price=float(product_info['price']),  # Set cost price same as price initially
                scientific_name=product_info.get('scientific_name', ''),
                height=product_info.get('height', ''),
                pot_size=product_info.get('pot_size', '')
            )
            
            db.session.add(new_product)
            db.session.commit()
            logger.info(f"Created new product: {product_info['product_name']} for supplier ID {supplier_id}")
            return True
            
    except Exception as e:
        logger.error(f"Error updating supplier product: {str(e)}")
        db.session.rollback()
        return False

@viber_blueprint.route('/viber-webhook', methods=['POST'])
def viber_webhook():
    """
    Webhook endpoint for receiving Viber messages.
    This endpoint should be registered with Viber as the webhook URL.
    """
    if not viber_bot:
        return jsonify({"status": "error", "message": "Viber bot not configured"}), 500
    
    # Parse the request body
    request_data = request.get_data()
    
    # Check if this is a valid Viber request
    if not viber_bot.verify_signature(request_data, request.headers.get('X-Viber-Content-Signature')):
        return jsonify({"status": "error", "message": "Invalid signature"}), 403
    
    # Process the request
    viber_request = viber_bot.parse_request(request_data)
    
    if isinstance(viber_request, ViberMessageRequest):
        # Extract message information
        message = viber_request.message
        sender_id = viber_request.sender.id
        
        # Get conversation ID if available (for group chats)
        conversation_id = getattr(viber_request, 'chat_id', None)
        
        # Only process text messages
        if isinstance(message, TextMessage):
            # Get supplier ID from the mapping
            supplier_id = get_supplier_id_from_viber(sender_id, conversation_id)
            
            if supplier_id:
                # Extract product information from the message
                product_info = extract_product_info(message.text)
                
                if product_info:
                    # Update or create the supplier product
                    success = update_supplier_product(supplier_id, product_info)
                    
                    if success:
                        # Send confirmation message
                        viber_bot.send_messages(viber_request.sender.id, [
                            TextMessage(text=f"Product '{product_info['product_name']}' updated with price {product_info['price']}€")
                        ])
                    else:
                        # Send error message
                        viber_bot.send_messages(viber_request.sender.id, [
                            TextMessage(text="Failed to update product. Please check the format and try again.")
                        ])
                else:
                    # Send format error message
                    viber_bot.send_messages(viber_request.sender.id, [
                        TextMessage(text="Could not extract product information. Please use the format: Product: Plant name, Scientific name: Latin name, Size: 20cm, Pot: 17cm, Price: €10.50")
                    ])
            else:
                # Sender not mapped to any supplier
                logger.warning(f"Received message from unmapped Viber ID: {sender_id}")
        
    elif isinstance(viber_request, ViberConversationStartedRequest):
        # New conversation started
        viber_bot.send_messages(viber_request.user.id, [
            TextMessage(text="Welcome to the Supplier Product Bot! To update product information, send messages in the format: Product: Plant name, Scientific name: Latin name, Size: 20cm, Pot: 17cm, Price: €10.50")
        ])
    
    elif isinstance(viber_request, ViberSubscribedRequest):
        # User subscribed to the bot
        viber_bot.send_messages(viber_request.user.id, [
            TextMessage(text="Thanks for subscribing to the Supplier Product Bot!")
        ])
    
    elif isinstance(viber_request, ViberUnsubscribedRequest):
        # User unsubscribed
        logger.info(f"User unsubscribed: {viber_request.user_id}")
    
    elif isinstance(viber_request, ViberFailedRequest):
        # Request failed
        logger.error(f"Failed request: {viber_request.message}")
    
    return jsonify({"status": "success"}), 200

@viber_blueprint.route('/viber-set-webhook', methods=['GET'])
def set_webhook():
    """
    Endpoint to set the Viber webhook URL.
    This should be called once when setting up the application or when the URL changes.
    """
    if not viber_bot:
        return jsonify({"status": "error", "message": "Viber bot not configured"}), 500
    
    # Get the current host URL
    host_url = request.host_url.rstrip('/')
    webhook_url = f"{host_url}/viber-webhook"
    
    try:
        # Set the webhook URL with Viber
        result = viber_bot.set_webhook(webhook_url)
        
        if result:
            return jsonify({
                "status": "success",
                "message": f"Webhook set to {webhook_url}",
                "result": result
            })
        else:
            return jsonify({
                "status": "error",
                "message": "Failed to set webhook, no result returned"
            }), 500
            
    except Exception as e:
        logger.error(f"Error setting Viber webhook: {str(e)}")
        return jsonify({
            "status": "error",
            "message": f"Error setting webhook: {str(e)}"
        }), 500

@viber_blueprint.route('/viber-mapping', methods=['GET', 'POST'])
def manage_supplier_mapping():
    """
    Endpoint to view and update the mapping between Viber IDs and suppliers.
    """
    if request.method == 'GET':
        # Return the current mapping
        return jsonify({
            "status": "success",
            "mapping": VIBER_SUPPLIER_MAPPING
        })
    elif request.method == 'POST':
        try:
            # Update the mapping with the provided data
            data = request.json
            
            if not data or not isinstance(data, dict):
                return jsonify({
                    "status": "error",
                    "message": "Invalid data format"
                }), 400
            
            # Update the global mapping
            for viber_id, supplier_id in data.items():
                VIBER_SUPPLIER_MAPPING[viber_id] = supplier_id
                
            # Store the mapping (this should be persisted to a database in a production environment)
            try:
                # A simple way to persist the mapping is to write it to a JSON file
                mapping_file = 'viber_supplier_mapping.json'
                with open(mapping_file, 'w') as f:
                    json.dump(VIBER_SUPPLIER_MAPPING, f)
                logger.info(f"Viber supplier mapping saved to {mapping_file}")
            except Exception as e:
                logger.warning(f"Could not persist Viber supplier mapping: {str(e)}")
                
            return jsonify({
                "status": "success",
                "mapping": VIBER_SUPPLIER_MAPPING
            })
        except Exception as e:
            logger.error(f"Error updating Viber mapping: {str(e)}")
            return jsonify({
                "status": "error",
                "message": str(e)
            }), 500

def register_viber_integration(app):
    """
    Register the Viber integration blueprint with the Flask app.
    
    Args:
        app: The Flask application instance
    """
    # Load previous mapping if it exists
    try:
        mapping_file = 'viber_supplier_mapping.json'
        if os.path.exists(mapping_file):
            with open(mapping_file, 'r') as f:
                global VIBER_SUPPLIER_MAPPING
                VIBER_SUPPLIER_MAPPING = json.load(f)
                logger.info(f"Loaded Viber supplier mapping from {mapping_file}")
    except Exception as e:
        logger.warning(f"Could not load Viber supplier mapping: {str(e)}")
        
    # Register the blueprint with the Flask app
    app.register_blueprint(viber_blueprint)
    logger.info("Registered Viber integration blueprint")
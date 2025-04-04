import logging
from datetime import datetime
from app import db
from models import Product, PriceList, ProductUpdateRequest

# Set up logging
try:
    from utils.logger import logger
except ImportError:
    import logging
    logger = logging.getLogger(__name__)

def find_or_create_product(product_data):
    """
    Find a product by its unique identifiers (name, scientific_name, pot)
    or create it if it doesn't exist.
    
    Args:
        product_data (dict): Dictionary containing product details
        
    Returns:
        tuple: (product, str message, bool is_new)
    """
    # Extract required fields
    name = product_data.get('name')
    scientific_name = product_data.get('scientific_name')
    pot = product_data.get('pot')
    sku = product_data.get('sku')
    
    # Validate required fields
    if not name:
        return None, "Product name is required", False
    
    # Create query based on available unique identifiers
    query = Product.query.filter(Product.name == name)
    
    if scientific_name:
        query = query.filter(Product.scientific_name == scientific_name)
    
    if pot:
        query = query.filter(Product.pot == pot)
        
    if sku:
        query = query.filter(Product.sku == sku)
    
    product = query.first()
    
    # If product doesn't exist, create it
    if not product:
        product = Product(
            name=name,
            scientific_name=scientific_name,
            pot=pot,
            sku=sku,
            category=product_data.get('category'),
            description=product_data.get('description')
        )
        db.session.add(product)
        db.session.commit()
        logger.info(f"Created new product: {name}")
        return product, "Product created successfully", True
    
    return product, "Product found in database", False

def create_or_update_price_list(customer_id, product_id, new_price, source_file=None):
    """
    Create a new price list entry or handle the update of an existing one.
    If a price change is detected, a pending update request is created.
    
    Args:
        customer_id (int): Customer ID
        product_id (int): Product ID
        new_price (float): New price from the import
        source_file (str, optional): Source file of the import
        
    Returns:
        tuple: (price_list, str message, bool is_new)
    """
    # Look for existing price list entry
    price_list = PriceList.query.filter_by(
        customer_id=customer_id,
        product_id=product_id
    ).first()
    
    # If no existing price list, create one
    if not price_list:
        price_list = PriceList(
            customer_id=customer_id,
            product_id=product_id,
            price=new_price,
            effective_date=datetime.now().date(),
            source_file=source_file
        )
        db.session.add(price_list)
        db.session.commit()
        logger.info(f"Created new price list entry for product {product_id}")
        return price_list, "Price list entry created", True
    
    # If price is different, create a pending update request
    if price_list.price != new_price:
        create_price_update_request(price_list, new_price, source_file)
        return price_list, "Price change detected - update pending approval", False
    
    return price_list, "No price change detected", False

def create_price_update_request(price_list, new_price, source_file=None):
    """
    Create a pending price update request
    
    Args:
        price_list (PriceList): Existing price list entry
        new_price (float): New price value
        source_file (str, optional): Source file of the import
        
    Returns:
        ProductUpdateRequest: The created update request
    """
    update_request = ProductUpdateRequest(
        product_id=price_list.product_id,
        price_list_id=price_list.id,
        old_price=price_list.price,
        new_price=new_price,
        status='Pending',
        source_file=source_file
    )
    db.session.add(update_request)
    db.session.commit()
    logger.info(f"Created price update request for product {price_list.product_id}: {price_list.price} -> {new_price}")
    return update_request

def approve_price_update(update_request_id):
    """
    Approve a pending price update request
    
    Args:
        update_request_id (int): ID of the update request
        
    Returns:
        bool: Success status
    """
    update_request = ProductUpdateRequest.query.get(update_request_id)
    if not update_request or update_request.status != 'Pending':
        return False
    
    # Update the price list with the new price
    price_list = PriceList.query.get(update_request.price_list_id)
    if price_list:
        price_list.price = update_request.new_price
        price_list.updated_at = datetime.utcnow()
        
    # Mark the update request as approved
    update_request.status = 'Approved'
    update_request.updated_at = datetime.utcnow()
    
    db.session.commit()
    logger.info(f"Approved price update for product {update_request.product_id}")
    return True

def reject_price_update(update_request_id):
    """
    Reject a pending price update request
    
    Args:
        update_request_id (int): ID of the update request
        
    Returns:
        bool: Success status
    """
    update_request = ProductUpdateRequest.query.get(update_request_id)
    if not update_request or update_request.status != 'Pending':
        return False
    
    # Mark the update request as rejected
    update_request.status = 'Rejected'
    update_request.updated_at = datetime.utcnow()
    
    db.session.commit()
    logger.info(f"Rejected price update for product {update_request.product_id}")
    return True
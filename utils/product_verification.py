import logging
import pandas as pd
from datetime import datetime
from app import db
from models import Product, PriceList
from utils.logger import logger
from utils.product_management import find_or_create_product, create_or_update_price_list

def verify_product_exists(product_data, create_if_missing=True):
    """
    Enhanced product verification that checks using various strategies.
    Uses more intelligent matching than the basic find_or_create_product.
    
    Args:
        product_data (dict): Dictionary containing product details
                             (name, scientific_name, pot, category, etc.)
        create_if_missing (bool): Whether to create the product if it doesn't exist
        
    Returns:
        tuple: (product, str message, bool is_new, bool was_created)
    """
    # Extract key data for searches
    name = product_data.get('name')
    scientific_name = product_data.get('scientific_name')
    pot = product_data.get('pot')
    sku = product_data.get('sku')
    
    # Validation to ensure we have the minimum fields needed
    if not name:
        return None, "Error: Product name is required for verification", False, False
    
    # Strategy 1: Try exact match first using the regular find_or_create function
    if create_if_missing:
        product, message, is_new = find_or_create_product(product_data)
        return product, message, is_new, is_new
    
    # If we're not auto-creating, use comprehensive search strategies
    product = None
    message = "Product not found"
    
    # Strategy 1: Exact match on name + scientific name + pot (if available)
    query = Product.query.filter(Product.name == name)
    if scientific_name:
        query = query.filter(Product.scientific_name == scientific_name)
    if pot:
        query = query.filter(Product.pot == pot)
    if sku:
        query = query.filter(Product.sku == sku)
    
    product = query.first()
    if product:
        return product, "Product found with exact match", False, False
    
    # Strategy 2: Case-insensitive search for name
    product = Product.query.filter(db.func.lower(Product.name) == name.lower()).first()
    if product:
        return product, "Product found with case-insensitive name match", False, False
    
    # Strategy 3: Partial match on name (within)
    product = Product.query.filter(Product.name.ilike(f"%{name}%")).first()
    if product:
        return product, "Product found with partial name match", False, False
    
    # Strategy 4: If scientific name exists, try matching on that
    if scientific_name:
        product = Product.query.filter(
            db.func.lower(Product.scientific_name) == scientific_name.lower()
        ).first()
        if product:
            return product, "Product found with scientific name match", False, False
    
    # Strategy 5: For pot-specific products, try finding match with same pot size
    if pot:
        product = Product.query.filter(
            db.func.lower(Product.name).ilike(f"%{name.lower()}%"),
            db.func.lower(Product.pot) == pot.lower()
        ).first()
        if product:
            return product, "Product found with name and pot match", False, False
    
    # No product found and not creating a new one
    return None, "Product not found in database", False, False

def batch_verify_products(product_list, create_missing=True, customer_id=None):
    """
    Batch verify multiple products, optionally creating any that are missing.
    
    Args:
        product_list (list): List of dictionaries containing product details
        create_missing (bool): Whether to create missing products
        customer_id (int, optional): Customer ID for price list association
        
    Returns:
        tuple: (
            verified_products (list): List of (product, was_created) tuples,
            stats (dict): Stats about the verification process
        )
    """
    verified_products = []
    stats = {
        'total': len(product_list),
        'found': 0,
        'created': 0,
        'error': 0,
        'price_added': 0,
        'price_updated': 0
    }
    
    logger.info(f"Batch verifying {len(product_list)} products")
    
    for product_data in product_list:
        try:
            # Verify or create the product
            product, message, is_new, was_created = verify_product_exists(
                product_data, 
                create_if_missing=create_missing
            )
            
            if product:
                verified_products.append((product, was_created))
                
                # Update stats based on result
                if was_created:
                    stats['created'] += 1
                    logger.info(f"Created new product: {product.name}")
                else:
                    stats['found'] += 1
                    logger.debug(f"Found existing product: {product.name}")
                
                # If customer_id and price are provided, create/update price list
                if customer_id and 'price' in product_data and product_data['price'] is not None:
                    try:
                        price_list, price_message, is_new_price = create_or_update_price_list(
                            customer_id=customer_id,
                            product_id=product.id,
                            new_price=float(product_data['price']),
                            source_file=product_data.get('source_file', 'batch_verification')
                        )
                        
                        if is_new_price:
                            stats['price_added'] += 1
                        elif "pending approval" in price_message:
                            stats['price_updated'] += 1
                        
                        logger.debug(f"Price list update for product {product.id}: {price_message}")
                    except (ValueError, TypeError) as e:
                        logger.warning(f"Invalid price for product {product.name}: {e}")
            else:
                stats['error'] += 1
                logger.warning(f"Product verification failed: {message}")
        
        except Exception as e:
            stats['error'] += 1
            logger.error(f"Error in product verification: {str(e)}")
    
    # Summary log
    logger.info(f"Batch verification complete. Found: {stats['found']}, Created: {stats['created']}, "
                f"Errors: {stats['error']}, Price lists added: {stats['price_added']}, "
                f"Price updates pending: {stats['price_updated']}")
    
    return verified_products, stats

def extract_products_from_excel(df):
    """
    Extract product data from a pandas DataFrame for batch verification.
    
    Args:
        df (DataFrame): Pandas DataFrame containing product data
        
    Returns:
        list: List of dictionaries with product details
    """
    product_list = []
    
    for _, row in df.iterrows():
        # Skip rows with no name
        if 'name' not in row or pd.isna(row['name']):
            continue
        
        # Create product data dictionary
        product_data = {
            'name': row['name'],
            'category': row.get('category') if 'category' in row and not pd.isna(row.get('category')) else None,
            'scientific_name': row.get('scientific_name') if 'scientific_name' in row and not pd.isna(row.get('scientific_name')) else None,
            'pot': row.get('pot') if 'pot' in row and not pd.isna(row.get('pot')) else None,
            'price': row.get('price') if 'price' in row and not pd.isna(row.get('price')) else None,
            'description': None  # Will be set below if scientific_name or pot exists
        }
        
        # Add description if scientific_name or pot exists
        if product_data['scientific_name'] or product_data['pot']:
            product_data['description'] = f"{product_data['scientific_name'] or ''} {product_data['pot'] or ''}".strip() or None
        
        product_list.append(product_data)
    
    return product_list
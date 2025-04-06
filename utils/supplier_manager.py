"""
Supplier management module with functions for searching and organizing supplier products.
"""
from datetime import datetime
from app import db
from models import SupplierProduct, Supplier
from sqlalchemy import or_
from utils.logger import logger

def search_supplier_products(query='', supplier_id=None, limit=100):
    """
    Search for supplier products with filters.
    
    Args:
        query (str): Search query for product name, scientific name, etc.
        supplier_id (int, optional): Filter by supplier ID
        limit (int, optional): Maximum number of results to return
        
    Returns:
        list: List of SupplierProduct objects matching the search criteria
    """
    # Start with a base query
    products_query = SupplierProduct.query
    
    # Add filter by supplier if specified
    if supplier_id:
        try:
            supplier_id = int(supplier_id)
            products_query = products_query.filter(SupplierProduct.supplier_id == supplier_id)
        except (ValueError, TypeError):
            logger.warning(f"Invalid supplier_id in search_supplier_products: {supplier_id}")
    
    # Add search filter if a query was provided
    if query and query.strip():
        search_query = f"%{query.strip()}%"
        products_query = products_query.filter(
            or_(
                SupplierProduct.product_name.ilike(search_query),
                SupplierProduct.scientific_name.ilike(search_query),
                SupplierProduct.pot_size.ilike(search_query),
                SupplierProduct.height.ilike(search_query),
                SupplierProduct.notes.ilike(search_query)
            )
        )
    
    # Add join to supplier to get supplier info for sorting
    products_query = products_query.join(Supplier)
    
    # Order by supplier name and then product name
    products_query = products_query.order_by(Supplier.name, SupplierProduct.product_name)
    
    # Apply limit
    if limit:
        products_query = products_query.limit(limit)
    
    # Execute query and return results
    return products_query.all()

def get_supplier_products_by_ids(product_ids):
    """
    Get supplier products by their IDs.
    
    Args:
        product_ids (list): List of supplier product IDs
        
    Returns:
        list: List of SupplierProduct objects with the given IDs
    """
    if not product_ids:
        return []
    
    # Convert all IDs to integers
    valid_ids = []
    for pid in product_ids:
        try:
            valid_ids.append(int(pid))
        except (ValueError, TypeError):
            logger.warning(f"Invalid product ID: {pid}")
    
    # Query and return results
    return SupplierProduct.query.filter(SupplierProduct.id.in_(valid_ids)).all()

def group_products_by_supplier(products):
    """
    Group a list of supplier products by their supplier.
    
    Args:
        products (list): List of SupplierProduct objects
        
    Returns:
        dict: Dictionary with supplier names as keys and lists of products as values
    """
    result = {}
    
    for product in products:
        supplier_name = product.supplier.name if product.supplier else "Unknown"
        
        if supplier_name not in result:
            result[supplier_name] = []
            
        result[supplier_name].append(product)
    
    return result

def update_supplier_product_last_detected(product_id):
    """
    Update the last_detected timestamp for a supplier product.
    
    Args:
        product_id (int): ID of the supplier product
        
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        product = SupplierProduct.query.get(product_id)
        if product:
            product.last_detected = datetime.utcnow()
            db.session.commit()
            logger.info(f"Updated last_detected for supplier product ID {product_id}")
            return True
        else:
            logger.warning(f"Supplier product ID {product_id} not found for updating last_detected")
            return False
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error updating last_detected for supplier product ID {product_id}: {str(e)}")
        return False
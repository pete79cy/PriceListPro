"""
Supplier management module with functions for searching and organizing supplier products.
"""
from datetime import datetime
from app import db
from models import SupplierProduct, Supplier, QuotationItem
from sqlalchemy import or_
from utils.logger import logger
from utils.db_utils import with_db_reconnect

def search_supplier_products(query='', supplier_id=None, show_duplicates=False, limit=100):
    """
    Search for supplier products with filters.
    
    Args:
        query (str): Search query for product name, scientific name, etc.
        supplier_id (int, optional): Filter by supplier ID
        show_duplicates (bool, optional): If True, only show flagged duplicates
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
    
    # Filter by flagged_duplicate status if requested
    if show_duplicates:
        products_query = products_query.filter(SupplierProduct.flagged_duplicate == True)
    
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

@with_db_reconnect(max_retries=3)
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

@with_db_reconnect(max_retries=3)
def update_supplier_from_quotation_item(quotation_item):
    """
    Update or create a supplier product record based on a quotation item.
    This helps to maintain an up-to-date product catalog from our quotes.
    
    Args:
        quotation_item (QuotationItem): The quotation item object
        
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        # Skip if no supplier information
        if not quotation_item.supplier:
            logger.info(f"No supplier information for quotation item {quotation_item.id}, skipping supplier update")
            return False
            
        # Find or create the supplier
        supplier = Supplier.query.filter(Supplier.name == quotation_item.supplier).first()
        if not supplier:
            supplier = Supplier(
                name=quotation_item.supplier,
                is_inhouse=False,  # Default to external supplier
                notes="Automatically created from quotation"
            )
            db.session.add(supplier)
            db.session.flush()  # Get ID without committing
            logger.info(f"Created new supplier '{quotation_item.supplier}' from quotation item {quotation_item.id}")
            
        # Look for an existing product with the same name/scientific name/pot from this supplier
        existing_product = None
        if quotation_item.scientific_name and quotation_item.pot_size:
            existing_product = SupplierProduct.query.filter(
                SupplierProduct.supplier_id == supplier.id,
                db.func.lower(SupplierProduct.scientific_name) == quotation_item.scientific_name.lower(),
                db.func.lower(SupplierProduct.pot_size) == quotation_item.pot_size.lower()
            ).first()
            
        # If not found by scientific name and pot, try with product name
        if not existing_product and quotation_item.description:
            existing_product = SupplierProduct.query.filter(
                SupplierProduct.supplier_id == supplier.id,
                db.func.lower(SupplierProduct.product_name) == quotation_item.description.lower()
            ).first()
            
        # Create or update the supplier product
        if existing_product:
            # Update existing product
            existing_product.price = quotation_item.selling_price
            existing_product.cost_price = quotation_item.cost_price if quotation_item.cost_price else existing_product.cost_price
            existing_product.last_detected = datetime.utcnow()
            
            # Update height if available
            if quotation_item.height:
                existing_product.height = quotation_item.height
                
            logger.info(f"Updated existing supplier product '{existing_product.product_name}' from quotation item {quotation_item.id}")
        else:
            # Create new supplier product
            new_product = SupplierProduct(
                supplier_id=supplier.id,
                product_name=quotation_item.description,
                scientific_name=quotation_item.scientific_name,
                pot_size=quotation_item.pot_size,
                height=quotation_item.height,
                price=quotation_item.selling_price,
                cost_price=quotation_item.cost_price,
                last_detected=datetime.utcnow(),
                notes="Created from quotation"
            )
            db.session.add(new_product)
            logger.info(f"Created new supplier product '{quotation_item.description}' from quotation item {quotation_item.id}")
            
        db.session.commit()
        return True
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error updating supplier from quotation item {quotation_item.id}: {str(e)}")
        return False
        
def update_suppliers_from_quotation(quotation):
    """
    Update or create supplier product records for all items in a quotation.
    
    Args:
        quotation: The Quotation object containing items to process
        
    Returns:
        dict: Results with success and error counts
    """
    results = {
        'success_count': 0,
        'error_count': 0,
        'updated_suppliers': []
    }
    
    if not quotation or not quotation.items:
        logger.warning("No items found in quotation")
        return results
        
    logger.info(f"Processing {len(quotation.items)} items from quotation {quotation.id}")
    
    # Process each item in the quotation
    for item in quotation.items:
        try:
            if update_supplier_from_quotation_item(item):
                results['success_count'] += 1
                if item.supplier and item.supplier not in results['updated_suppliers']:
                    results['updated_suppliers'].append(item.supplier)
            else:
                results['error_count'] += 1
        except Exception as e:
            results['error_count'] += 1
            logger.error(f"Error processing quotation item {item.id}: {str(e)}")
    
    logger.info(f"Finished processing quotation {quotation.id}: {results['success_count']} successes, {results['error_count']} errors")
    return results
"""
Supplier Manager - Functions for managing supplier data
"""
from datetime import datetime
from app import db
from models import Supplier, SupplierProduct, QuotationItem
from utils.logger import logger

def update_supplier_from_quotation_item(item):
    """
    Update or create supplier product data based on a quotation item
    
    Args:
        item (QuotationItem): The quotation item containing supplier information
    
    Returns:
        bool: Whether the operation was successful
    """
    if not item.supplier_name and not item.supplier_id:
        # Skip items without supplier information
        return False
        
    try:
        # Get or create the supplier
        supplier = None
        if item.supplier_id:
            supplier = Supplier.query.get(item.supplier_id)
        
        if not supplier and item.supplier_name:
            supplier = Supplier.query.filter_by(name=item.supplier_name).first()
            
            if not supplier:
                # Create a new supplier with the name
                supplier = Supplier(
                    name=item.supplier_name,
                    is_inhouse="in-house" in item.supplier_name.lower() if item.supplier_name else False
                )
                db.session.add(supplier)
                db.session.flush()  # Get the ID without committing yet
                logger.info(f"Created new supplier: {supplier.name}")
        
        if not supplier:
            logger.warning(f"Could not determine supplier for item {item.id}")
            return False
        
        # Set the supplier_id field to maintain the relationship
        if not item.supplier_id:
            item.supplier_id = supplier.id
            db.session.add(item)
        
        # Now check for existing supplier product or create a new one
        supplier_product = SupplierProduct.query.filter_by(
            supplier_id=supplier.id,
            product_name=item.description,
            scientific_name=item.scientific_name,
            height=item.height,
            pot_size=item.pot_size
        ).first()
        
        if supplier_product:
            # Update the existing product
            supplier_product.price = item.selling_price
            supplier_product.cost_price = item.cost_price
            supplier_product.last_detected = datetime.utcnow()
            logger.info(f"Updated supplier product: {supplier_product.product_name}")
        else:
            # Create a new supplier product
            supplier_product = SupplierProduct(
                supplier_id=supplier.id,
                product_name=item.description,
                scientific_name=item.scientific_name,
                height=item.height,
                pot_size=item.pot_size,
                price=item.selling_price,
                cost_price=item.cost_price,
                last_detected=datetime.utcnow()
            )
            db.session.add(supplier_product)
            logger.info(f"Created new supplier product: {supplier_product.product_name}")
        
        # Commit changes
        db.session.commit()
        return True
    
    except Exception as e:
        logger.error(f"Error updating supplier data: {str(e)}")
        db.session.rollback()
        return False

def update_suppliers_from_quotation(quotation):
    """
    Update all supplier data from a quotation
    
    Args:
        quotation (Quotation): The quotation containing items with supplier info
        
    Returns:
        dict: Summary of operations (success_count, error_count)
    """
    success_count = 0
    error_count = 0
    
    for item in quotation.items:
        if update_supplier_from_quotation_item(item):
            success_count += 1
        else:
            error_count += 1
    
    return {
        'success_count': success_count,
        'error_count': error_count
    }

def search_supplier_products(query, supplier_id=None, limit=50):
    """
    Search for supplier products based on keywords
    
    Args:
        query (str): The search query
        supplier_id (int, optional): Filter by supplier ID
        limit (int, optional): Maximum number of results to return
        
    Returns:
        list: Matching supplier products
    """
    if not query or len(query) < 2:
        # Return recent products if query is too short
        base_query = SupplierProduct.query.order_by(SupplierProduct.last_detected.desc())
        if supplier_id:
            base_query = base_query.filter_by(supplier_id=supplier_id)
        return base_query.limit(limit).all()
    
    # Convert query to lowercase for case-insensitive matching
    search_term = f"%{query.lower()}%"
    
    # Build the search query
    base_query = SupplierProduct.query.filter(
        db.or_(
            db.func.lower(SupplierProduct.product_name).like(search_term),
            db.func.lower(SupplierProduct.scientific_name).like(search_term),
            db.func.lower(SupplierProduct.height).like(search_term),
            db.func.lower(SupplierProduct.pot_size).like(search_term)
        )
    )
    
    # Add supplier filter if specified
    if supplier_id:
        base_query = base_query.filter_by(supplier_id=supplier_id)
    
    # Add ordering and limit
    results = base_query.order_by(SupplierProduct.last_detected.desc()).limit(limit).all()
    
    return results

def get_supplier_by_name_or_create(name):
    """
    Get a supplier by name or create a new one if not found
    
    Args:
        name (str): Supplier name
        
    Returns:
        Supplier: The supplier object (existing or new)
    """
    if not name:
        return None
        
    supplier = Supplier.query.filter(db.func.lower(Supplier.name) == name.lower()).first()
    
    if not supplier:
        is_inhouse = "in-house" in name.lower()
        supplier = Supplier(
            name=name,
            is_inhouse=is_inhouse
        )
        db.session.add(supplier)
        db.session.commit()
        logger.info(f"Created new supplier: {name}")
    
    return supplier
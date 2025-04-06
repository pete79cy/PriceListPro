"""
Utility functions for supplier management.

This module provides reusable functions for CRUD operations on suppliers,
with proper error handling, validation, and standardized return values.
"""
from datetime import datetime
from sqlalchemy.exc import IntegrityError
from app import db
from models import Supplier
from utils.logger import logger
from utils.validation import validate_email

def get_supplier_by_name_or_create(
    name, 
    contact_person=None, 
    email=None, 
    phone=None, 
    address=None, 
    notes=None, 
    is_inhouse=False
):
    """
    Get a supplier by name or create a new one if it doesn't exist.
    
    Args:
        name (str): The name of the supplier
        contact_person (str, optional): Contact person name
        email (str, optional): Contact email
        phone (str, optional): Contact phone number
        address (str, optional): Physical address
        notes (str, optional): Additional notes
        is_inhouse (bool, optional): Whether this is an in-house production
        
    Returns:
        tuple: (supplier, created) where supplier is the Supplier object and
               created is a boolean indicating if a new supplier was created or
               (None, False) if validation fails
    """
    # Basic validation - name is required
    if not name or not name.strip():
        logger.warning("Attempted to get or create supplier with empty name")
        return None, False
    
    # Validate email if provided
    if email and not validate_email(email):
        logger.warning(f"Attempted to create supplier with invalid email: {email}")
        return None, False
    
    # Normalize the name (strip whitespace)
    name = name.strip()
    
    # Check if supplier already exists (case-insensitive)
    supplier = Supplier.query.filter(db.func.lower(Supplier.name) == db.func.lower(name)).first()
    
    if supplier:
        logger.info(f"Found existing supplier: {supplier.name}")
        return supplier, False
    
    try:
        # Create new supplier
        supplier = Supplier(
            name=name,
            contact_person=contact_person,
            email=email,
            phone=phone,
            address=address,
            notes=notes,
            is_inhouse=is_inhouse,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        
        db.session.add(supplier)
        db.session.commit()
        
        logger.info(f"Created new supplier: {supplier.name}")
        return supplier, True
        
    except IntegrityError as e:
        # Handle the case where a supplier with this name might have been created
        # in another concurrent request (race condition)
        db.session.rollback()
        logger.error(f"Integrity error creating supplier '{name}': {str(e)}")
        
        # Try to find the supplier again
        supplier = Supplier.query.filter(db.func.lower(Supplier.name) == db.func.lower(name)).first()
        if supplier:
            return supplier, False
        
        # If still not found, propagate the error
        raise e
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error creating supplier '{name}': {str(e)}")
        raise e

def update_supplier(
    supplier_id,
    name=None, 
    contact_person=None, 
    email=None, 
    phone=None, 
    address=None, 
    notes=None, 
    is_inhouse=None
):
    """
    Update an existing supplier.
    
    Args:
        supplier_id (int): The ID of the supplier to update
        name (str, optional): New name for the supplier
        contact_person (str, optional): New contact person name
        email (str, optional): New contact email
        phone (str, optional): New contact phone number
        address (str, optional): New physical address
        notes (str, optional): New additional notes
        is_inhouse (bool, optional): New in-house production status
        
    Returns:
        tuple: (supplier, success, message) where supplier is the Supplier object,
               success is a boolean indicating if update was successful, and
               message is a string explaining any failure
    """
    # Get the supplier
    supplier = Supplier.query.get(supplier_id)
    
    if not supplier:
        return None, False, "Supplier not found"
    
    # Validate email if provided
    if email is not None and email and not validate_email(email):
        logger.warning(f"Attempted to update supplier with invalid email: {email}")
        return supplier, False, "Invalid email address format"
    
    try:
        # Update the supplier fields if provided
        if name is not None and name.strip():
            # Check if another supplier already has this name
            if supplier.name.lower() != name.strip().lower():
                existing = Supplier.query.filter(
                    db.and_(
                        db.func.lower(Supplier.name) == db.func.lower(name.strip()),
                        Supplier.id != supplier_id
                    )
                ).first()
                
                if existing:
                    return supplier, False, f"A supplier with the name '{name.strip()}' already exists"
                    
            supplier.name = name.strip()
            
        if contact_person is not None:
            supplier.contact_person = contact_person
            
        if email is not None:
            supplier.email = email
            
        if phone is not None:
            supplier.phone = phone
            
        if address is not None:
            supplier.address = address
            
        if notes is not None:
            supplier.notes = notes
            
        if is_inhouse is not None:
            supplier.is_inhouse = is_inhouse
        
        # Update the updated_at timestamp
        supplier.updated_at = datetime.utcnow()
        
        # Commit the changes
        db.session.commit()
        
        logger.info(f"Updated supplier ID {supplier_id}: {supplier.name}")
        return supplier, True, "Supplier updated successfully"
        
    except IntegrityError as e:
        db.session.rollback()
        logger.error(f"Integrity error updating supplier ID {supplier_id}: {str(e)}")
        return supplier, False, f"Database integrity error: {str(e)}"
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error updating supplier ID {supplier_id}: {str(e)}")
        return supplier, False, f"Error updating supplier: {str(e)}"

def delete_supplier(supplier_id):
    """
    Delete a supplier and all related records.
    
    Args:
        supplier_id (int): The ID of the supplier to delete
        
    Returns:
        tuple: (success, message) where success is a boolean indicating 
               if deletion was successful and message is a string with details
    """
    # Get the supplier
    supplier = Supplier.query.get(supplier_id)
    
    if not supplier:
        return False, "Supplier not found"
    
    try:
        # Count related products (for the message)
        product_count = len(supplier.products)
        
        # Delete the supplier (cascade will delete related products)
        db.session.delete(supplier)
        db.session.commit()
        
        logger.info(f"Deleted supplier ID {supplier_id}: {supplier.name}")
        
        # Provide detailed success message
        message = f"Supplier '{supplier.name}' deleted successfully"
        if product_count > 0:
            message += f" along with {product_count} related product(s)"
            
        return True, message
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error deleting supplier ID {supplier_id}: {str(e)}")
        return False, f"Error deleting supplier: {str(e)}"
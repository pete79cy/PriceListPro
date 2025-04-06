"""
Supplier Utilities - Functions for managing supplier data
"""
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from app import db
from models import Supplier
from utils.logger import logger

def get_supplier_by_name_or_create(name, contact_person=None, email=None, 
                                  phone=None, address=None, notes=None, 
                                  is_inhouse=False):
    """
    Get a supplier by name or create a new one if it doesn't exist
    
    Args:
        name (str): The supplier name (required)
        contact_person (str, optional): Contact person name
        email (str, optional): Contact email
        phone (str, optional): Contact phone number
        address (str, optional): Business address
        notes (str, optional): Additional notes
        is_inhouse (bool, optional): Whether this is an in-house supplier
        
    Returns:
        tuple: (supplier, created) - The supplier object and whether it was created
    """
    if not name or not name.strip():
        logger.warning("Attempted to get or create supplier with empty name")
        return None, False
    
    # Sanitize inputs
    name = name.strip()
    if contact_person: contact_person = contact_person.strip()
    if email: email = email.strip()
    if phone: phone = phone.strip()
    if address: address = address.strip()
    if notes: notes = notes.strip()
    
    try:
        # Check if supplier already exists
        existing_supplier = Supplier.query.filter(db.func.lower(Supplier.name) == name.lower()).first()
        
        if existing_supplier:
            logger.info(f"Found existing supplier: {existing_supplier.name}")
            return existing_supplier, False
            
        # Create new supplier
        supplier = Supplier(
            name=name,
            contact_person=contact_person,
            email=email,
            phone=phone,
            address=address,
            notes=notes,
            is_inhouse=is_inhouse
        )
        
        db.session.add(supplier)
        db.session.commit()
        logger.info(f"Created new supplier: {supplier.name}")
        
        return supplier, True
        
    except IntegrityError as e:
        db.session.rollback()
        logger.error(f"Integrity error creating supplier '{name}': {str(e)}")
        # Try to find the supplier in case of a race condition
        existing_supplier = Supplier.query.filter(db.func.lower(Supplier.name) == name.lower()).first()
        if existing_supplier:
            return existing_supplier, False
        return None, False
        
    except SQLAlchemyError as e:
        db.session.rollback()
        logger.error(f"Database error creating supplier '{name}': {str(e)}")
        return None, False
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Unexpected error creating supplier '{name}': {str(e)}")
        return None, False


def update_supplier(supplier_id, name=None, contact_person=None, email=None, 
                    phone=None, address=None, notes=None, is_inhouse=None):
    """
    Update an existing supplier
    
    Args:
        supplier_id (int): The ID of the supplier to update
        name (str, optional): New supplier name
        contact_person (str, optional): New contact person name
        email (str, optional): New contact email
        phone (str, optional): New contact phone number
        address (str, optional): New business address
        notes (str, optional): New additional notes
        is_inhouse (bool, optional): New in-house status
        
    Returns:
        tuple: (supplier, success, message) - The supplier object, success status, and message
    """
    try:
        supplier = Supplier.query.get(supplier_id)
        
        if not supplier:
            return None, False, "Supplier not found"
            
        # Update fields if provided
        if name is not None and name.strip():
            # Check if another supplier already has this name
            existing = Supplier.query.filter(
                db.func.lower(Supplier.name) == name.lower(),
                Supplier.id != supplier_id
            ).first()
            
            if existing:
                return supplier, False, f"A supplier with the name '{name}' already exists"
            
            supplier.name = name.strip()
            
        if contact_person is not None:
            supplier.contact_person = contact_person.strip() if contact_person else None
            
        if email is not None:
            supplier.email = email.strip() if email else None
            
        if phone is not None:
            supplier.phone = phone.strip() if phone else None
            
        if address is not None:
            supplier.address = address.strip() if address else None
            
        if notes is not None:
            supplier.notes = notes.strip() if notes else None
            
        if is_inhouse is not None:
            supplier.is_inhouse = is_inhouse
            
        db.session.commit()
        logger.info(f"Updated supplier ID {supplier_id}: {supplier.name}")
        
        return supplier, True, "Supplier updated successfully"
        
    except IntegrityError as e:
        db.session.rollback()
        logger.error(f"Integrity error updating supplier {supplier_id}: {str(e)}")
        return None, False, f"Database constraint error: {str(e)}"
        
    except SQLAlchemyError as e:
        db.session.rollback()
        logger.error(f"Database error updating supplier {supplier_id}: {str(e)}")
        return None, False, f"Database error: {str(e)}"
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Unexpected error updating supplier {supplier_id}: {str(e)}")
        return None, False, f"Unexpected error: {str(e)}"


def delete_supplier(supplier_id):
    """
    Delete a supplier by ID
    
    Args:
        supplier_id (int): The ID of the supplier to delete
        
    Returns:
        tuple: (success, message) - Success status and message
    """
    try:
        supplier = Supplier.query.get(supplier_id)
        
        if not supplier:
            return False, "Supplier not found"
            
        # Get the name for the message before deletion
        supplier_name = supplier.name
        
        # Check for related data that will be cascaded
        product_count = len(supplier.products)
        
        db.session.delete(supplier)
        db.session.commit()
        
        msg = f"Supplier '{supplier_name}' deleted successfully"
        if product_count > 0:
            msg += f", along with {product_count} related product(s)"
            
        logger.info(f"Deleted supplier ID {supplier_id}: {supplier_name}")
        return True, msg
        
    except SQLAlchemyError as e:
        db.session.rollback()
        logger.error(f"Database error deleting supplier {supplier_id}: {str(e)}")
        return False, f"Database error: {str(e)}"
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Unexpected error deleting supplier {supplier_id}: {str(e)}")
        return False, f"Unexpected error: {str(e)}"
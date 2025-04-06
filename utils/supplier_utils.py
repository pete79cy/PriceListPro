"""
Supplier utilities for the application.
This module provides functions to manage suppliers with data validation.
"""
import logging
import re
from datetime import datetime

from sqlalchemy.exc import IntegrityError
from app import db
from models import Supplier
from utils.validation import is_valid_email, sanitize_input

logger = logging.getLogger(__name__)

def get_supplier_by_name_or_create(name, email=None, phone=None, contact_person=None, address=None):
    """
    Get a supplier by name or create a new one if it doesn't exist.
    Validates email before adding to the database.
    
    Args:
        name (str): The name of the supplier
        email (str, optional): The email of the supplier
        phone (str, optional): The phone number of the supplier
        contact_person (str, optional): The contact person of the supplier
        address (str, optional): The address of the supplier
        
    Returns:
        tuple: (Supplier object, bool indicating if it was created)
    """
    # Sanitize inputs
    name = sanitize_input(name)
    email = sanitize_input(email) if email else None
    phone = sanitize_input(phone) if phone else None
    contact_person = sanitize_input(contact_person) if contact_person else None
    address = sanitize_input(address) if address else None
    
    if not name:
        logger.error("Cannot create supplier with empty name")
        return None, False
    
    # Check if email is valid
    if email and not is_valid_email(email):
        logger.warning(f"Invalid email for supplier {name}: {email}")
        email = None  # Clear invalid email
    
    # Try to find existing supplier
    supplier = Supplier.query.filter(Supplier.name == name).first()
    
    if supplier:
        created = False
        # Update supplier details if provided and different
        modified = False
        
        if email and email != supplier.email:
            supplier.email = email
            modified = True
            
        if phone and phone != supplier.phone:
            supplier.phone = phone
            modified = True
            
        if contact_person and contact_person != supplier.contact_person:
            supplier.contact_person = contact_person
            modified = True
            
        if address and address != supplier.address:
            supplier.address = address
            modified = True
            
        if modified:
            supplier.updated_at = datetime.utcnow()
            db.session.commit()
            logger.info(f"Updated supplier: {name}")
    else:
        # Create new supplier
        supplier = Supplier(
            name=name,
            email=email,
            phone=phone,
            contact_person=contact_person,
            address=address
        )
        
        try:
            db.session.add(supplier)
            db.session.commit()
            created = True
            logger.info(f"Created new supplier: {name}")
        except IntegrityError as e:
            db.session.rollback()
            logger.error(f"Failed to create supplier {name}: {str(e)}")
            return None, False
    
    return supplier, created

def update_supplier(supplier_id, name=None, email=None, phone=None, contact_person=None, address=None):
    """
    Update an existing supplier with validated information.
    
    Args:
        supplier_id (int): The ID of the supplier to update
        name (str, optional): New name for the supplier
        email (str, optional): New email for the supplier
        phone (str, optional): New phone number for the supplier
        contact_person (str, optional): New contact person for the supplier
        address (str, optional): New address for the supplier
        
    Returns:
        bool: True if successful, False otherwise
    """
    supplier = Supplier.query.get(supplier_id)
    if not supplier:
        logger.error(f"Supplier with ID {supplier_id} not found")
        return False
    
    modified = False
    
    # Update fields if provided
    if name:
        name = sanitize_input(name)
        if name and name != supplier.name:
            supplier.name = name
            modified = True
    
    if email is not None:  # Allow clearing email by passing empty string
        email = sanitize_input(email)
        if email and not is_valid_email(email):
            logger.warning(f"Invalid email for supplier {supplier.name}: {email}")
        elif email != supplier.email:
            supplier.email = email
            modified = True
    
    if phone is not None:
        phone = sanitize_input(phone)
        if phone != supplier.phone:
            supplier.phone = phone
            modified = True
    
    if contact_person is not None:
        contact_person = sanitize_input(contact_person)
        if contact_person != supplier.contact_person:
            supplier.contact_person = contact_person
            modified = True
    
    if address is not None:
        address = sanitize_input(address)
        if address != supplier.address:
            supplier.address = address
            modified = True
    
    if modified:
        supplier.updated_at = datetime.utcnow()
        try:
            db.session.commit()
            logger.info(f"Updated supplier: {supplier.name}")
            return True
        except IntegrityError as e:
            db.session.rollback()
            logger.error(f"Failed to update supplier {supplier.name}: {str(e)}")
            return False
    
    return True  # No changes needed

def delete_supplier(supplier_id):
    """
    Delete a supplier and all related products.
    
    Args:
        supplier_id (int): The ID of the supplier to delete
        
    Returns:
        bool: True if successful, False otherwise
    """
    supplier = Supplier.query.get(supplier_id)
    if not supplier:
        logger.error(f"Supplier with ID {supplier_id} not found")
        return False
    
    try:
        # Delete all supplier products first
        supplier_name = supplier.name  # Save for logging
        db.session.delete(supplier)
        db.session.commit()
        logger.info(f"Deleted supplier: {supplier_name}")
        return True
    except Exception as e:
        db.session.rollback()
        logger.error(f"Failed to delete supplier {supplier.name}: {str(e)}")
        return False
"""
Validation utilities for the application.
This module provides functions to validate user inputs.
"""
import logging
import re
from email_validator import validate_email, EmailNotValidError

# Set up logging
logger = logging.getLogger(__name__)

def is_valid_email(email):
    """
    Validate an email address.
    
    Args:
        email (str): The email address to validate
        
    Returns:
        bool: True if the email is valid, False otherwise
    """
    if not email:
        return False
        
    # Basic validation for common typos
    if ' ' in email or email.count('@') != 1:
        return False
    
    try:
        # Validate email with email_validator library
        validation = validate_email(email, check_deliverability=False)
        return True
    except EmailNotValidError as e:
        logger.debug(f"Invalid email: {email} - {str(e)}")
        return False

def sanitize_input(value, max_length=None):
    """
    Sanitize user input to prevent common issues.
    
    Args:
        value (str): The input value to sanitize
        max_length (int, optional): Maximum length for the value
        
    Returns:
        str: The sanitized value
    """
    if value is None:
        return None
    
    # Convert to string if not already
    value = str(value)
    
    # Trim whitespace
    value = value.strip()
    
    # Truncate to max_length if specified
    if max_length and len(value) > max_length:
        value = value[:max_length]
    
    return value

def sanitize_email(email):
    """
    Sanitize and normalize an email address.
    
    Args:
        email (str): The email address to sanitize
        
    Returns:
        str: The sanitized email address, or None if invalid
    """
    if not email:
        return None
    
    # Sanitize input first
    email = sanitize_input(email)
    
    # Convert to lowercase
    email = email.lower()
    
    # Remove any spaces
    email = email.replace(' ', '')
    
    # Validate the sanitized email
    if is_valid_email(email):
        return email
    else:
        return None
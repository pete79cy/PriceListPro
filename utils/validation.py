from email_validator import validate_email as validate_email_external, EmailNotValidError
import re

def validate_email(email):
    """
    Validate an email address.
    
    Args:
        email: The email address to validate
        
    Returns:
        True if the email is valid, False otherwise
    """
    if not email:
        return False
        
    # First try the email validator library 
    try:
        # Use the email-validator library for robust validation
        validate_email_external(email)
        return True
    except Exception:
        # If the library fails (possibly not installed), fall back to regex
        pass
        
    # Fallback to a simple regex pattern for basic validation
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))


def sanitize_input(text):
    """
    Sanitize input text to prevent injection attacks.
    
    Args:
        text: The text to sanitize
        
    Returns:
        Sanitized text string
    """
    if not text:
        return ""
        
    # Remove any HTML/script tags
    sanitized = re.sub(r'<[^>]*>', '', text)
    
    # Replace special characters
    sanitized = sanitized.replace('&', '&amp;')
    sanitized = sanitized.replace('<', '&lt;')
    sanitized = sanitized.replace('>', '&gt;')
    sanitized = sanitized.replace('"', '&quot;')
    sanitized = sanitized.replace("'", '&#x27;')
    
    return sanitized


def validate_phone(phone):
    """
    Validate a phone number.
    
    Args:
        phone: The phone number to validate
        
    Returns:
        True if the phone number is valid, False otherwise
    """
    if not phone:
        return False
        
    # Simple validation pattern for international phone numbers
    # Allows +, spaces, dashes, and parentheses
    pattern = r'^[+]?[\s./0-9()\-]{10,}$'
    return bool(re.match(pattern, phone))
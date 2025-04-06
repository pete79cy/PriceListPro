from email_validator import validate_email, EmailNotValidError

def is_valid_email(email):
    """
    Validates an email address using email_validator package.
    
    Args:
        email (str): The email address to validate
        
    Returns:
        bool: True if email is valid or empty, False otherwise
    """
    if not email or email.strip() == '':
        return True  # Empty email is considered valid (not required)
        
    try:
        # Validate the email
        validate_email(email)
        return True
    except EmailNotValidError:
        return False
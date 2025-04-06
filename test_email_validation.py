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
        
    # Fallback to a simple regex pattern for basic validation
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))

# Test with valid emails
valid_emails = [
    "user@example.com",
    "user.name@example.com",
    "user+tag@example.com",
    "user@subdomain.example.com"
]

# Test with invalid emails
invalid_emails = [
    "user@",
    "user@.com",
    "@example.com",
    "user@example",
    "user@exam_ple.com",
    "user@exam ple.com",
    "userexample.com"
]

print("Valid emails:")
for email in valid_emails:
    result = validate_email(email)
    print(f"{email}: {result}")

print("\nInvalid emails:")
for email in invalid_emails:
    result = validate_email(email)
    print(f"{email}: {result}")
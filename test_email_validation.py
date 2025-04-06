"""
Simple test script for email validation functionality.
Run this script directly to test the email validation.
"""
import sys
import logging

from utils.validation import is_valid_email

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_valid_emails():
    """Test a set of valid email addresses."""
    valid_emails = [
        "user@example.com",
        "user.name@example.com",
        "user+tag@example.com",
        "user@subdomain.example.com",
        "user@example.co.uk",
        "user-name@example.com",
        "USER@EXAMPLE.COM"
    ]
    
    results = []
    for email in valid_emails:
        result = is_valid_email(email)
        results.append(result)
        logger.info(f"Testing valid email: {email} -> {'Valid' if result else 'Invalid'}")
    
    return all(results)

def test_invalid_emails():
    """Test a set of invalid email addresses."""
    invalid_emails = [
        "user@",
        "@example.com",
        "user@.com",
        "user@example.",
        "user@exam ple.com",
        "user name@example.com",
        "user@example..com",
        "user@example_com",
        ".user@example.com",
        "user@-example.com"
    ]
    
    results = []
    for email in invalid_emails:
        result = not is_valid_email(email)  # Should return False for these
        results.append(result)
        logger.info(f"Testing invalid email: {email} -> {'Invalid (correct)' if result else 'Valid (incorrect)'}")
    
    return all(results)

def run_tests():
    """Run all tests and print results."""
    valid_result = test_valid_emails()
    invalid_result = test_invalid_emails()
    
    print("\n=== Email Validation Test Results ===")
    print(f"Valid email tests: {'PASSED' if valid_result else 'FAILED'}")
    print(f"Invalid email tests: {'PASSED' if invalid_result else 'FAILED'}")
    print(f"Overall: {'PASSED' if (valid_result and invalid_result) else 'FAILED'}")
    
    return valid_result and invalid_result

if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1)
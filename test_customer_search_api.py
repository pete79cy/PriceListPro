"""
Test script for the Customer Search API functionality.
This script tests the customer search API endpoint to verify it works correctly.
"""
import sys
import logging
import requests
import json

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Base URL for the application
BASE_URL = "http://localhost:5000"

def login(username, password):
    """
    Login to the application to get a session cookie for authenticated requests.
    
    Args:
        username (str): The username
        password (str): The password
        
    Returns:
        requests.Session: A session with authentication cookies
    """
    session = requests.Session()
    login_data = {
        'username': username,
        'password': password
    }
    response = session.post(f"{BASE_URL}/login", data=login_data)
    
    if response.url.endswith('/dashboard'):
        logger.info("Login successful")
        return session
    else:
        logger.error("Login failed")
        return None

def test_customer_search_by_name():
    """Test searching customers by name."""
    session = login('admin', 'admin123')
    if not session:
        return False
    
    # Test search by name
    response = session.get(f"{BASE_URL}/api/customers/search?q=test")
    
    if response.status_code != 200:
        logger.error(f"Search by name failed with status code: {response.status_code}")
        return False
    
    customers = response.json()
    logger.info(f"Found {len(customers)} customers with 'test' in name")
    
    # Check response format
    if len(customers) > 0:
        customer = customers[0]
        if not all(k in customer for k in ('id', 'name', 'email', 'category')):
            logger.error("Customer response missing required fields")
            return False
    
    return True

def test_customer_search_by_category():
    """Test searching customers by category."""
    session = login('admin', 'admin123')
    if not session:
        return False
    
    # Test search by category
    response = session.get(f"{BASE_URL}/api/customers/search?category=retail")
    
    if response.status_code != 200:
        logger.error(f"Search by category failed with status code: {response.status_code}")
        return False
    
    customers = response.json()
    logger.info(f"Found {len(customers)} customers in 'retail' category")
    
    return True

def test_combined_search():
    """Test searching customers by both name and category."""
    session = login('admin', 'admin123')
    if not session:
        return False
    
    # Test combined search
    response = session.get(f"{BASE_URL}/api/customers/search?q=plant&category=wholesale")
    
    if response.status_code != 200:
        logger.error(f"Combined search failed with status code: {response.status_code}")
        return False
    
    customers = response.json()
    logger.info(f"Found {len(customers)} customers with 'plant' in name and 'wholesale' category")
    
    return True

def run_tests():
    """Run all tests and summarize results."""
    tests = [
        ('Search by name', test_customer_search_by_name),
        ('Search by category', test_customer_search_by_category),
        ('Combined search', test_combined_search)
    ]
    
    results = []
    for name, test_func in tests:
        logger.info(f"Running test: {name}")
        try:
            result = test_func()
            results.append(result)
            logger.info(f"Test '{name}': {'PASSED' if result else 'FAILED'}\n")
        except Exception as e:
            logger.error(f"Test '{name}' raised an exception: {str(e)}")
            results.append(False)
    
    print("\n=== Customer Search API Test Results ===")
    for i, (name, _) in enumerate(tests):
        print(f"{name}: {'PASSED' if results[i] else 'FAILED'}")
    
    print(f"Overall: {'PASSED' if all(results) else 'FAILED'}")
    
    return all(results)

if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1)
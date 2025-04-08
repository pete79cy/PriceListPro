"""
Test script for the OpenAI utilities.

This script:
1. Tests the health check function
2. Tests the OpenAI client initialization
3. Tests the connection test function
"""
import os
from services.openai_utils import openai_health_check, get_openai_client, test_openai_connection

def test_health_check():
    """Test the OpenAI health check function"""
    print("\n=== Testing openai_health_check() ===")
    result = openai_health_check()
    print(f"Health check result: {result}")
    return result

def test_get_client():
    """Test the OpenAI client initialization function"""
    print("\n=== Testing get_openai_client() ===")
    client, error = get_openai_client()
    if error:
        print(f"Error getting client: {error}")
        return False
    print(f"Client initialized successfully: {client}")
    return True

def test_connection():
    """Test the OpenAI connection test function"""
    print("\n=== Testing test_openai_connection() ===")
    success, message = test_openai_connection()
    print(f"Connection test result: {success}")
    print(f"Message: {message}")
    return success

def main():
    """Run all tests"""
    # Check environment
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("WARNING: OPENAI_API_KEY environment variable not set")
        print("Tests will fail unless the key is properly configured.")
    
    # Run tests
    health_ok = test_health_check()
    client_ok = test_get_client()
    conn_ok = test_connection()
    
    # Summarize results
    print("\n=== Test Results ===")
    print(f"Health Check: {'✅ PASS' if health_ok else '❌ FAIL'}")
    print(f"Client Init: {'✅ PASS' if client_ok else '❌ FAIL'}")
    print(f"Connection Test: {'✅ PASS' if conn_ok else '❌ FAIL'}")
    
    if health_ok and client_ok and conn_ok:
        print("\n✅ All tests passed! The OpenAI integration is working correctly.")
        return True
    else:
        print("\n❌ Some tests failed. Check the logs above for details.")
        return False

if __name__ == "__main__":
    main()
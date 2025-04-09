"""
Test script for OpenAI health check utilities.
This script tests the health check and API functionality.
"""

import os
import sys
import logging
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO,
                   format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Import the utilities module
try:
    from services.openai_utils import openai_health_check, get_openai_client, test_openai_connection
    logger.info("Successfully imported OpenAI utilities")
except ImportError as e:
    logger.error(f"Error importing OpenAI utilities: {str(e)}")
    sys.exit(1)

def test_health_check():
    """Test the OpenAI API health check function"""
    logger.info("Testing OpenAI health check...")
    
    # This should return True if the API key is valid and the service is operational
    result = openai_health_check()
    
    if result:
        logger.info(f"✅ OpenAI API health check passed!")
        return True
    else:
        logger.error(f"❌ OpenAI API health check failed")
        return False

def test_client_creation():
    """Test the OpenAI client creation function"""
    logger.info("Testing OpenAI client creation...")
    
    # Get the client and error if any
    client, error = get_openai_client()
    
    if not error and client:
        logger.info(f"✅ OpenAI client creation successful")
        return True
    else:
        logger.error(f"❌ OpenAI client creation failed: {error}")
        return False

def test_connection():
    """Test the OpenAI connection test function"""
    logger.info("Testing OpenAI connection test...")
    
    # This should test a simple completion API call
    success, message = test_openai_connection()
    
    if success:
        logger.info(f"✅ OpenAI connection test passed: {message}")
        return True
    else:
        logger.error(f"❌ OpenAI connection test failed: {message}")
        return False

def main():
    """Main test function"""
    logger.info("Starting OpenAI utilities test")
    
    # Test health check first
    health_check_passed = test_health_check()
    if not health_check_passed:
        logger.error("Health check failed, cannot proceed with other tests")
        return 1
        
    # Test individual components
    client_passed = test_client_creation()
    connection_passed = test_connection()
    
    # Summarize results
    logger.info("\n=== TEST RESULTS ===")
    logger.info(f"Health Check: {'✅ PASSED' if health_check_passed else '❌ FAILED'}")
    logger.info(f"Client Creation: {'✅ PASSED' if client_passed else '❌ FAILED'}")
    logger.info(f"Connection Test: {'✅ PASSED' if connection_passed else '❌ FAILED'}")
    
    # Return success if all tests passed
    if health_check_passed and client_passed and connection_passed:
        logger.info("✅ All tests passed successfully!")
        return 0
    else:
        logger.warning("⚠️ Some tests failed")
        return 1

if __name__ == "__main__":
    sys.exit(main())
"""
OpenAI utility functions for the plant pricing system.

This module provides centralized OpenAI functionality including:
- Health checks for the OpenAI API
- Standardized API call functions with error handling
- Utility functions for common OpenAI operations
"""
import os
from openai import OpenAI
from utils.logger import logger

def openai_health_check():
    """
    Check if the OpenAI API is available and working correctly.
    
    Returns:
        bool: True if the OpenAI API is healthy, False otherwise
    """
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        logger.warning("OpenAI API key not found in environment variables")
        return False
    
    try:
        # Initialize client with robust settings
        client = OpenAI(api_key=api_key, timeout=10.0)
        
        # Test model listing as a way to verify API access
        models = client.models.list()
        model_count = len(models.data)
        
        logger.info(f"✅ OpenAI health check passed. {model_count} models available.")
        return True
        
    except Exception as e:
        logger.error(f"❌ OpenAI health check failed: {str(e)}")
        return False

def get_openai_client(timeout=30.0):
    """
    Get a configured OpenAI client with error handling.
    
    Args:
        timeout (float): Request timeout in seconds
    
    Returns:
        tuple: (client, error_message) - client is None if there was an error
    """
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        return None, "OpenAI API key not configured"
    
    try:
        client = OpenAI(api_key=api_key, timeout=timeout)
        return client, None
    except Exception as e:
        error_message = f"Error initializing OpenAI client: {str(e)}"
        logger.error(error_message)
        return None, error_message

def test_openai_connection():
    """
    Test if the OpenAI API key is valid and the connection is working.
    
    Returns:
        tuple: (success, message) - success is a boolean indicating if the test passed
    """
    client, error = get_openai_client()
    if error:
        return False, error
    
    try:
        # Test a simple model query to validate the API key
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": "Test connection"}
            ],
            max_tokens=10,
            temperature=0.3,
        )
        
        # If we got here, the API key is working for completions
        logger.info("OpenAI API test successful: chat completions working")
        
        try:
            # Try listing models as a secondary test
            models = client.models.list()
            model_count = len(models.data)
            
            logger.info(f"OpenAI API models test successful. Found {model_count} models.")
            return True, f"Connection successful! Found {model_count} available models."
            
        except Exception as model_error:
            # Even if model listing fails, if we got a completion that's good enough
            logger.warning(f"Model listing failed but completions work: {str(model_error)}")
            return True, "Connection successful! Your API key is valid for completions."
            
    except Exception as e:
        error_message = str(e)
        logger.error(f"OpenAI API test failed: {str(e)}")
        return False, f"API connection failed: {str(e)}"
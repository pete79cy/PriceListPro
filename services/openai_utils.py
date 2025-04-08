"""
OpenAI service utilities for API health checks and integration.
"""
import os
from openai import OpenAI
from utils.logger import logger

def openai_health_check() -> bool:
    """
    Check if OpenAI API is healthy and configured correctly.
    
    Returns:
        bool: True if OpenAI API is healthy, False otherwise
    """
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        logger.warning("OpenAI API key is missing.")
        return False

    try:
        client = OpenAI(api_key=api_key, timeout=10.0)
        models = client.models.list()
        logger.info(f"✅ OpenAI health check passed. {len(models.data)} models available.")
        return True
    except Exception as e:
        logger.error(f"❌ OpenAI health check failed: {str(e)}")
        return False
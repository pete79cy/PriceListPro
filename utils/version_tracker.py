"""
Version tracking utilities for the application.
This module provides functions to track the version of the application.
"""
import logging
from datetime import datetime

# Set up logging
logger = logging.getLogger(__name__)

# Current version information
VERSION = {
    'major': 1,
    'minor': 2,
    'patch': 0,
    'build': datetime.now().strftime('%Y%m%d')
}

def get_current_version():
    """
    Get the current version of the application.
    
    Returns:
        str: A string representation of the current version
    """
    return f"{VERSION['major']}.{VERSION['minor']}.{VERSION['patch']}-{VERSION['build']}"

def log_deployment():
    """
    Log information about the current deployment.
    """
    version = get_current_version()
    logger.info(f"Application deployed with version {version}")
    logger.info(f"Deployment timestamp: {datetime.now().isoformat()}")
    
    # Log key features enabled
    logger.info("Key features enabled:")
    logger.info(" - Email validation")
    logger.info(" - Customer categories")
    logger.info(" - Customer contact history")
    logger.info(" - Enhanced customer search API")
    logger.info(" - Admin dashboard")
    
    return version
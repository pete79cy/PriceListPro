import logging
import os
from datetime import datetime

# Create logs directory if it doesn't exist
os.makedirs('logs', exist_ok=True)

# Configure logging
def setup_logger():
    """Set up logger for the application"""
    # Create a logger
    logger = logging.getLogger('plant_pricing_system')
    logger.setLevel(logging.DEBUG)
    
    # Create a file handler with a unique name including timestamp
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    file_handler = logging.FileHandler(f'logs/app_{timestamp}.log')
    file_handler.setLevel(logging.DEBUG)
    
    # Create a console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    
    # Create a formatter and add it to the handlers
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)
    
    # Add the handlers to the logger
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    
    return logger

# Create and export the logger
logger = setup_logger()
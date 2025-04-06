"""
Logger setup for the application.
"""
import logging

# Create a custom logger
logger = logging.getLogger('plant_pricing_system')

# Check if handlers are already configured to avoid duplicate log messages
if not logger.handlers:
    # Set the level of the logger
    logger.setLevel(logging.INFO)
    
    # Create a handler to send log messages to the console
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    
    # Create a formatter for the logs
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    console_handler.setFormatter(formatter)
    
    # Add the handler to the logger
    logger.addHandler(console_handler)
    
    # Prevent propagation to root logger to avoid duplicate logs
    logger.propagate = False
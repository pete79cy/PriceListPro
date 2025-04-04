"""
Plant Pricing System Backend
----------------------------
This package contains the backend code for the Plant Pricing System.
"""

import os
import logging

# Import our custom logger
try:
    from utils.logger import logger
    logger.info("Backend module loaded")
except ImportError:
    # This can happen on first load before utils directory exists
    logging.basicConfig(level=logging.DEBUG)
    logger = logging.getLogger("plant_pricing_system")
    logger.info("Backend module loaded with basic logging configuration")
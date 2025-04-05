"""Test pattern matching for Viber integration."""

import re
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_pattern():
    """Test regex pattern for Greek arrival message."""
    message = "Νέα παραλαβή: ΦΙΚΟΣ ΕΛΑΣΤΙΚΑ ΤΡΙΧΡΩΜΟΣ (Ficus elastica) ύψος 45-50cm σε γλάστρα 17cm, κόστος €12,90"
    
    pattern = r'Νέα\s+παραλαβή:\s+(.*?)\s+\('
    logger.info(f"Testing pattern: {pattern}")
    
    match = re.search(pattern, message)
    if match:
        product_name = match.group(1).strip()
        logger.info(f"Matched! Product name: {product_name}")
    else:
        logger.warning(f"No match for pattern in message: {message}")
        
    pattern2 = r'Νέα παραλαβή:\s+([^(]+)'
    logger.info(f"Testing alternative pattern: {pattern2}")
    
    match2 = re.search(pattern2, message)
    if match2:
        product_name = match2.group(1).strip()
        logger.info(f"Matched! Product name: {product_name}")
    else:
        logger.warning(f"No match for alternative pattern in message: {message}")
        
    # Test for non-Latin character issues
    logger.info(f"Length of message: {len(message)}")
    for i, char in enumerate(message):
        logger.info(f"Char {i}: '{char}' (Unicode: {ord(char)})")
        if 10 <= i <= 30:  # Just show a portion to avoid overwhelming logs
            logger.info(f"  Is alphabetic: {char.isalpha()}, Is space: {char.isspace()}")
    
    # Test a hardcoded substring extraction
    prefix = "Νέα παραλαβή: "
    if message.startswith(prefix):
        product_part = message[len(prefix):message.find("(")].strip()
        logger.info(f"Direct substring extraction: {product_part}")
    else:
        logger.warning("Expected prefix not found at start of message")

if __name__ == "__main__":
    test_pattern()
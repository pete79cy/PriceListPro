"""
Test the enhanced message parser with an unstructured message format.
This script sends a test message to the Viber webhook endpoint in a format
that's less structured than the standard format.
"""

import json
import logging
import requests

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_unstructured_message():
    """
    Test an unstructured message format with the "New arrival:" prefix.
    """
    # Example message with the "New arrival:" prefix - trying alternative syntax
    message_text = "Νέα παραλαβή: ΦΙΚΟΣ ΕΛΑΣΤΙΚΑ ΤΡΙΧΡΩΜΟΣ (Ficus elastica) ύψος 45-50cm σε γλάστρα 17cm, κόστος €12,90"
    
    # Create a fake Viber message for testing
    test_data = {
        "event": "message",
        "sender": {
            "id": "test-sender-id"
        },
        "chat_id": "test-conversation-id",
        "message": {
            "type": "text",
            "text": message_text
        }
    }
    
    # Send the test request to our local server
    try:
        # Add a test header to indicate this is a test request
        headers = {
            'Content-Type': 'application/json',
            'X-Viber-Content-Signature': 'fake-signature-for-testing'
        }
        
        # Make the POST request to the webhook endpoint
        response = requests.post(
            'http://localhost:5000/viber-webhook', 
            json=test_data, 
            headers=headers
        )
        
        # Log the response
        logger.info(f"Response status code: {response.status_code}")
        
        # Try to parse the response as JSON
        try:
            response_json = response.json()
            logger.info(f"Response data: {json.dumps(response_json, indent=2)}")
        except json.JSONDecodeError:
            logger.info(f"Response text: {response.text}")
            
    except Exception as e:
        logger.error(f"Error sending test request: {str(e)}")

if __name__ == "__main__":
    test_unstructured_message()
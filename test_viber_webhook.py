import requests
import json
import time

# URL of the webhook endpoint
webhook_url = "http://localhost:5000/viber-webhook"

# Sample message in the Viber webhook format
# We're simulating updating ΛΑΝΤΑΝΑ price from 3.5 to 4.5
message_payload = {
    "event": "message",
    "timestamp": int(time.time()),
    "chat_id": "test-viber-conversation-id",  # This is our mapped conversation ID
    "sender": {
        "id": "test-sender-id",
        "name": "Test Supplier"
    },
    "message": {
        "type": "text",
        "text": "Product: ΛΑΝΤΑΝΑ, Scientific name: Lantana montevidensis, Size: 20cm, Pot: 17cm, Price: €4.50",
        "timestamp": int(time.time())
    },
    "silent": False
}

# Fake signature - the app won't verify this in test mode
headers = {
    "Content-Type": "application/json",
    "X-Viber-Content-Signature": "fake-signature-for-testing"
}

# Send the request
try:
    response = requests.post(webhook_url, json=message_payload, headers=headers)
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.text}")
except Exception as e:
    print(f"Error: {str(e)}")
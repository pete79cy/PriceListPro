import requests
import json
import time

# URL of the webhook endpoint
webhook_url = "http://localhost:5000/viber-webhook"

# Create a new product that doesn't exist yet
message_payload = {
    "event": "message",
    "timestamp": int(time.time()),
    "chat_id": "test-viber-conversation-id",  # This is our mapped conversation ID for Moesis (ID 5)
    "sender": {
        "id": "test-sender-id",
        "name": "Test Supplier"
    },
    "message": {
        "type": "text",
        "text": "Product: ΚΥΚΑΣ ΡΕΒΟΛΟΥΤΑ, Scientific name: Cycas revoluta, Size: 100-120cm, Pot: 25cm, Price: €65.00",
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

# Verify the new product was created by querying the database
# This requires a direct database connection, which we're not doing in this script
print("\nRun the following SQL query to verify the product was created:")
print("SELECT * FROM supplier_product WHERE supplier_id = 5 AND product_name = 'ΚΥΚΑΣ ΡΕΒΟΛΟΥΤΑ';")
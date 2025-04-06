"""
Test script for the customer search API endpoint.
This script demonstrates how to use the new /api/customers/search endpoint 
to perform searches for customers by name, email, or phone number.
"""
import requests
import json
import sys

# Configuration
BASE_URL = "http://localhost:5000"  # Adjust this if your server is running elsewhere
SEARCH_API = "/api/customers/search"
USERNAME = "admin"  # Replace with your admin username
PASSWORD = "admin"  # Replace with your admin password

def login(session):
    """Log in to get a valid session"""
    response = session.post(
        f"{BASE_URL}/login", 
        data={"username": USERNAME, "password": PASSWORD}
    )
    if response.status_code != 200:
        print(f"Login failed with status code: {response.status_code}")
        sys.exit(1)
    return response.status_code == 200

def search_customers(session, query):
    """Search for customers using the API"""
    response = session.get(
        f"{BASE_URL}{SEARCH_API}",
        params={"q": query}
    )
    if response.status_code != 200:
        print(f"Search failed with status code: {response.status_code}")
        print(response.text)
        return []
    
    return response.json()

def main():
    """Main function to demonstrate the customer search API"""
    # Create a session to maintain cookies
    session = requests.Session()
    
    # Login first
    if not login(session):
        print("Failed to log in. Check your credentials.")
        return
    
    # Get search query from command line or use default
    search_query = sys.argv[1] if len(sys.argv) > 1 else ""
    
    if not search_query:
        print("Please provide a search query as a command-line argument.")
        print("Usage: python test_customer_search_api.py <search_query>")
        return
    
    # Perform search
    print(f"Searching for customers matching: '{search_query}'")
    results = search_customers(session, search_query)
    
    # Display results
    if results:
        print(f"Found {len(results)} matching customers:")
        for i, customer in enumerate(results, 1):
            print(f"{i}. {customer['name']} (ID: {customer['id']})")
            print(f"   Email: {customer['email']}")
            print(f"   Phone: {customer['phone']}")
            print(f"   Category: {customer['category']}")
            print(f"   Address: {customer['address']}")
            print(f"   Created: {customer['created_at']}")
            print()
    else:
        print("No matching customers found.")

if __name__ == "__main__":
    main()
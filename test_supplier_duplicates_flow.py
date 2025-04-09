"""
Test script to verify the supplier duplicates flow functionality.
This script:
1. Tests the /healthcheck endpoint to verify the OpenAI API is available
2. Tests the analyze_supplier_duplicates endpoint with a POST request
3. Verifies the redirect to supplier_duplicate_results works properly
4. Creates a test supplier and products if needed for testing
"""
import os
import sys
import json
import random
import requests
import time
from datetime import datetime

# Base URL for local testing
BASE_URL = "http://localhost:5000"

def create_test_supplier_if_needed():
    """Create a test supplier and products if they don't exist"""
    try:
        # Check if supplier with ID 1 exists
        response = requests.get(f"{BASE_URL}/api_suppliers")
        if response.status_code == 200:
            suppliers = response.json()
            
            # If no suppliers exist, create one
            if not suppliers:
                print("Creating test supplier...")
                response = requests.post(f"{BASE_URL}/add_supplier", data={
                    'name': f'Test Supplier {datetime.now().strftime("%Y%m%d%H%M%S")}',
                    'email': 'test@example.com',
                    'phone': '1234567890'
                })
                if response.status_code != 200 and response.status_code != 302:
                    print(f"Error creating supplier: {response.status_code}")
                    return None
                
                # Get the newly created supplier
                response = requests.get(f"{BASE_URL}/api_suppliers")
                if response.status_code != 200:
                    print(f"Error getting suppliers: {response.status_code}")
                    return None
                
                suppliers = response.json()
                
            if not suppliers:
                print("Still no suppliers available")
                return None
                
            # Get the first supplier
            supplier_id = suppliers[0]['id']
            
            # Now check if this supplier has products
            response = requests.get(f"{BASE_URL}/supplier_products?supplier_id={supplier_id}")
            if response.status_code != 200:
                print(f"Error checking supplier products: {response.status_code}")
            
            # Create a few test products with similar names to test duplicate detection
            print(f"Creating test products for supplier {supplier_id}...")
            
            # Product pairs with similar names for duplicate detection
            product_pairs = [
                ("Monstera Deliciosa", "Monstera deliciosa"),
                ("Pennisetum Alopecuroides", "Pennisetum alopecuroides 'Little bunny'"),
                ("Philodendron Birkin", "Philodendron 'Birkin'")
            ]
            
            for pair in product_pairs:
                for i, name in enumerate(pair):
                    # Add variation to pricing
                    base_price = 5.0 + random.random() * 5.0
                    
                    response = requests.post(f"{BASE_URL}/add_supplier_product", data={
                        'supplier_id': supplier_id,
                        'product_name': name,
                        'scientific_name': name.lower(),
                        'pot_size': f"{10 + i*5}cm",
                        'height': f"{30 + i*10}cm",
                        'price': base_price,
                        'cost_price': base_price * 0.8
                    })
                    if response.status_code != 200 and response.status_code != 302:
                        print(f"Error adding product: {response.status_code}")
            
            print(f"Test data created successfully for supplier {supplier_id}")
            return supplier_id
            
    except Exception as e:
        print(f"Error in create_test_supplier: {str(e)}")
        return None


def test_healthcheck():
    """Test the /healthcheck endpoint"""
    print("\n=== Testing /healthcheck endpoint ===")
    try:
        response = requests.get(f"{BASE_URL}/healthcheck")
        if response.status_code == 200:
            result = response.json()
            print(f"Healthcheck response: {result}")
            print(f"OpenAI API healthy: {result.get('openai_healthy', False)}")
            return result.get('openai_healthy', False)
        else:
            print(f"Error in healthcheck: {response.status_code}")
            return False
    except Exception as e:
        print(f"Exception in healthcheck: {str(e)}")
        return False


def test_analyze_supplier_duplicates(supplier_id):
    """Test the analyze_supplier_duplicates endpoint"""
    print(f"\n=== Testing /analyze_supplier_duplicates/{supplier_id} endpoint ===")
    try:
        response = requests.post(
            f"{BASE_URL}/analyze_supplier_duplicates/{supplier_id}", 
            data={'threshold': 0.8}, 
            allow_redirects=False  # Don't follow redirects to check status code
        )
        
        print(f"Status code: {response.status_code}")
        
        if response.status_code == 302:
            redirect_url = response.headers.get('Location')
            print(f"Successfully redirected to: {redirect_url}")
            
            # Now follow the redirect manually to check the results page
            if redirect_url:
                print(f"\n=== Following redirect to {redirect_url} ===")
                results_response = requests.get(f"{BASE_URL}{redirect_url}")
                print(f"Results page status code: {results_response.status_code}")
                
                if results_response.status_code == 200:
                    # Check if we got an HTML response with results
                    if "Duplicate Analysis Results" in results_response.text:
                        print("Results page rendered successfully!")
                        return True
                    else:
                        print("Results page doesn't contain expected content")
        else:
            print(f"Unexpected status code: {response.status_code}")
            print(f"Response: {response.text}")
        
        return False
    except Exception as e:
        print(f"Exception in analyze_supplier_duplicates: {str(e)}")
        return False


def main():
    """Run all tests"""
    # 1. Test healthcheck
    openai_healthy = test_healthcheck()
    if not openai_healthy:
        print("ERROR: OpenAI API is not healthy. Please check your API key.")
        print("Set your OpenAI API key in the OPENAI_API_KEY environment variable.")
        return False
    
    # 2. Create test data if needed
    supplier_id = create_test_supplier_if_needed()
    if not supplier_id:
        print("ERROR: Could not create test data.")
        return False
    
    # 3. Test analyze_supplier_duplicates
    duplicates_flow_working = test_analyze_supplier_duplicates(supplier_id)
    if not duplicates_flow_working:
        print("ERROR: Supplier duplicates analysis flow is not working properly.")
        return False
    
    # All tests passed
    print("\n=== All tests passed! ===")
    print("The supplier duplicates detection system is working properly.")
    return True


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
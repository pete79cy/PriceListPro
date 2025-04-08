"""
Test script for OpenAI integration endpoints.

This script tests:
1. The `/healthcheck` endpoint for API health status
2. The `/analyze_supplier_duplicates/<id>` endpoint for duplicate detection
"""
import requests
import json
import sys

def test_healthcheck():
    """Test the OpenAI API health check endpoint"""
    print("\n\n=== Testing OpenAI Health Check ===")
    response = requests.get("http://localhost:5000/healthcheck")
    
    print(f"Status Code: {response.status_code}")
    if response.status_code == 200:
        print("Response: ", json.dumps(response.json(), indent=2))
        if response.json().get("openai_healthy") == True:
            print("✅ OpenAI API is healthy")
        else:
            print("❌ OpenAI API is not healthy")
    else:
        print(f"❌ Error: {response.text}")
    
    return response.status_code == 200

def test_analyze_supplier_duplicates(supplier_id=1, threshold=0.8):
    """Test the supplier duplicate analysis endpoint"""
    print(f"\n\n=== Testing Supplier Duplicate Analysis (ID: {supplier_id}, Threshold: {threshold}) ===")
    
    response = requests.post(
        f"http://localhost:5000/analyze_supplier_duplicates/{supplier_id}?threshold={threshold}"
    )
    
    print(f"Status Code: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"Supplier ID: {data.get('supplier_id')}")
        print(f"Threshold: {data.get('threshold')}")
        
        results = data.get("results", [])
        if not results:
            print("No duplicates found")
        else:
            print(f"Found {len(results)} potential duplicate pairs:")
            for idx, item in enumerate(results, 1):
                print(f"\nDuplicate Pair #{idx}:")
                print(f"  Product 1: {item.get('product1', {}).get('name')} (ID: {item.get('product1', {}).get('id')})")
                print(f"  Product 2: {item.get('product2', {}).get('name')} (ID: {item.get('product2', {}).get('id')})")
                print(f"  Is Duplicate: {item.get('is_duplicate', False)}")
                
                suggestion = item.get('suggestion', '')
                # Print first 100 chars of suggestion
                print(f"  Suggestion: {suggestion[:100]}..." if len(suggestion) > 100 else f"  Suggestion: {suggestion}")
        
        print(f"\n✅ Successfully retrieved supplier duplicate analysis")
    else:
        print(f"❌ Error: {response.text}")
    
    return response.status_code == 200

if __name__ == "__main__":
    # Get supplier ID from command line if provided
    supplier_id = 1
    threshold = 0.8
    if len(sys.argv) > 1:
        supplier_id = sys.argv[1]
    if len(sys.argv) > 2:
        threshold = float(sys.argv[2])
    
    # Run tests
    health_ok = test_healthcheck()
    duplicates_ok = test_analyze_supplier_duplicates(supplier_id, threshold)
    
    # Print summary
    print("\n\n=== Test Summary ===")
    print(f"OpenAI Health Check: {'✅ PASSED' if health_ok else '❌ FAILED'}")
    print(f"Supplier Duplicate Analysis: {'✅ PASSED' if duplicates_ok else '❌ FAILED'}")
    
    # Exit with appropriate status code
    if health_ok and duplicates_ok:
        print("\nAll tests passed! ✅")
        sys.exit(0)
    else:
        print("\nSome tests failed! ❌")
        sys.exit(1)
"""
Test the enhanced message parser for Viber integration.
This script tests the extract_product_info function with various message formats.
"""

import sys
import json
from viber_integration import extract_product_info

# Test cases - different message formats
test_messages = [
    # Structured format
    {
        "description": "Structured format with all fields",
        "message": "Product: ΛΑΝΤΑΝΑ, Scientific name: Lantana camara, Size: 30cm, Pot: 17cm, Price: €4.50"
    },
    {
        "description": "Structured format with comma in price",
        "message": "Product: ΑΓΚΑΒΕ, Scientific name: Agave americana, Height: 60cm, Pot: 21cm, Price: €12,50"
    },
    # Semi-structured formats 
    {
        "description": "Scientific name in parentheses",
        "message": "ΑΛΟΕ ΒΕΡΑ (Aloe vera) 40cm pot 15cm, price €7.80"
    },
    {
        "description": "Greek format with size and pot",
        "message": "ΟΡΤΑΝΣΙΑ ύψος 30-35cm γλάστρα 19cm, τιμή €9.50"
    },
    {
        "description": "Height range format",
        "message": "ΕΥΚΑΛΥΠΤΟΣ 150-180cm σε γλάστρα 24cm €22.50"
    },
    # Unstructured formats
    {
        "description": "New stock format",
        "message": "Νέα παραλαβή: ΔΙΕΦΕΝΜΠΑΧΙΑ (Dieffenbachia amoena), ύψος 30-35cm, γλάστρα 15cm, €5.20"
    },
    {
        "description": "Minimal information",
        "message": "ΚΥΚΑΣ ΡΕΒΟΛΟΥΤΑ 40cm €8.50"
    },
    {
        "description": "Complex product name",
        "message": "ΦΙΚΟΣ ΛΥΡΑΤΑ - Θαμνώδης 30cm γλάστρα 19cm €11.90"
    },
    # Edge cases
    {
        "description": "Missing price - should fail",
        "message": "ΕΛΙΑ ύψος 40cm γλάστρα 17cm"
    },
    {
        "description": "Missing product name - should extract from beginning",
        "message": "Διαθέσιμο: 30-35cm γλάστρα 15cm, τιμή €6.70"
    }
]

def run_tests():
    """Run the tests and print the results."""
    print("\n=== Testing Viber Message Parser ===\n")
    
    results = {
        "total": len(test_messages),
        "passed": 0,
        "failed": 0,
        "details": []
    }
    
    for i, test in enumerate(test_messages):
        print(f"Test {i+1}: {test['description']}")
        print(f"Message: {test['message']}")
        
        # Extract product info
        product_info = extract_product_info(test['message'])
        
        if product_info and 'product_name' in product_info and 'price' in product_info:
            result = "PASSED"
            results["passed"] += 1
            print(f"Result: {result}")
            print(f"Extracted: {json.dumps(product_info, indent=2, ensure_ascii=False)}")
            
            results["details"].append({
                "test_case": test,
                "result": result,
                "extracted_info": product_info
            })
        else:
            result = "FAILED"
            results["failed"] += 1
            print(f"Result: {result}")
            print(f"Extraction failed, returned: {product_info}")
            
            results["details"].append({
                "test_case": test,
                "result": result,
                "extracted_info": product_info
            })
        
        print("-" * 50)
    
    # Print summary
    print("\n=== Summary ===")
    print(f"Total tests: {results['total']}")
    print(f"Passed: {results['passed']}")
    print(f"Failed: {results['failed']}")
    print(f"Success rate: {results['passed'] / results['total'] * 100:.1f}%")
    
    return results

if __name__ == "__main__":
    try:
        results = run_tests()
        
        # You can uncomment this to write results to a file
        # with open('test_results.json', 'w', encoding='utf-8') as f:
        #     json.dump(results, f, indent=2, ensure_ascii=False)
        
        # Exit with proper code (0 if all tests passed, 1 if any failed)
        sys.exit(0 if results["failed"] == 0 else 1)
    except Exception as e:
        print(f"Error running tests: {str(e)}")
        sys.exit(1)
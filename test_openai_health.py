"""
Simple test script to check if the OpenAI API is healthy via the /healthcheck endpoint.
"""
import requests

# Base URL for local testing
BASE_URL = "http://0.0.0.0:5000"

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

def test_analyze_duplicates_api():
    """Test the analyze_supplier_duplicates endpoint directly"""
    print("\n=== Testing direct API call to /analyze_supplier_duplicates/1 ===")
    try:
        response = requests.post(
            f"{BASE_URL}/analyze_supplier_duplicates/1", 
            data={'threshold': 0.8},
            allow_redirects=False
        )
        
        print(f"Status code: {response.status_code}")
        
        if response.status_code == 302:
            redirect_url = response.headers.get('Location')
            print(f"Successfully redirected to: {redirect_url}")
            return True
        else:
            print(f"Response: {response.text[:200]}...")  # Show first 200 chars
            return False
    except Exception as e:
        print(f"Exception in test_analyze_duplicates_api: {str(e)}")
        return False

if __name__ == "__main__":
    openai_healthy = test_healthcheck()
    if not openai_healthy:
        print("\nWARNING: OpenAI API is not healthy. Please check your API key.")
    
    analyze_working = test_analyze_duplicates_api()
    if analyze_working:
        print("\nSUCCESS: The supplier duplicates detection API is working correctly!")
    else:
        print("\nERROR: The supplier duplicates detection API is not working correctly.")
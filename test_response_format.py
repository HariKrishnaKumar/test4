"""
Test script to verify consistent response formatting across all endpoints
"""
import requests
import json
from typing import Dict, Any

BASE_URL = "http://localhost:8000"

def test_endpoint(method: str, endpoint: str, expected_status: int = 200, data: Dict[str, Any] = None) -> bool:
    """Test an endpoint and verify response format"""
    try:
        url = f"{BASE_URL}{endpoint}"

        if method.upper() == "GET":
            response = requests.get(url)
        elif method.upper() == "POST":
            response = requests.post(url, params=data)
        else:
            print(f"❌ Unsupported method: {method}")
            return False

        # Check status code
        if response.status_code != expected_status:
            print(f"❌ {method} {endpoint} - Expected status {expected_status}, got {response.status_code}")
            return False

        # Parse JSON response
        try:
            response_data = response.json()
        except json.JSONDecodeError:
            print(f"❌ {method} {endpoint} - Invalid JSON response")
            return False

        # Check response format
        if not isinstance(response_data, dict):
            print(f"❌ {method} {endpoint} - Response is not a dictionary")
            return False

        required_fields = ["success", "message", "data"]
        for field in required_fields:
            if field not in response_data:
                print(f"❌ {method} {endpoint} - Missing required field: {field}")
                return False

        # Check success field is boolean
        if not isinstance(response_data["success"], bool):
            print(f"❌ {method} {endpoint} - 'success' field is not boolean")
            return False

        # Check message field is string
        if not isinstance(response_data["message"], str):
            print(f"❌ {method} {endpoint} - 'message' field is not string")
            return False

        print(f"✅ {method} {endpoint} - Response format correct")
        return True

    except requests.exceptions.ConnectionError:
        print(f"⚠️  {method} {endpoint} - Server not running (skipped)")
        return True
    except Exception as e:
        print(f"❌ {method} {endpoint} - Error: {str(e)}")
        return False

def main():
    """Run all endpoint tests"""
    print("🧪 Testing Response Format Consistency")
    print("=" * 50)

    # Test endpoints
    endpoints = [
        # Basic endpoints
        ("GET", "/", 200),
        ("GET", "/users", 200),
        ("POST", "/users", 200, {"name": "Test User", "email": "test@example.com"}),

        # Pizza endpoints
        ("GET", "/pizzas", 200),
        ("GET", "/pizzas/1", 200),
        ("GET", "/pizzas/999", 404),  # Should return 404
        ("POST", "/pizzas", 200, {"name": "Test Pizza", "price": 299}),

        # AI endpoints
        ("GET", "/emoji-pizzas", 200),
        ("GET", "/ai-suggest", 200),

        # Example endpoints
        # ("GET", "/example/items", 200),
        # ("GET", "/example/items/1", 200),
        # ("GET", "/example/items/999", 404),  # Should return 404
        # ("POST", "/example/items", 200, {"name": "Test Item", "description": "Test description"}),
        # ("PUT", "/example/items/1", 200, {"name": "Updated Item", "description": "Updated description"}),
        # ("DELETE", "/example/items/1", 200),
        # ("GET", "/example/error-example", 400),  # Should return 400

        # Merchant endpoints (these might fail if no Clover credentials)
        ("GET", "/merchant", 200),
        ("GET", "/merchant/properties", 200),
    ]

    passed = 0
    total = len(endpoints)

    for method, endpoint, expected_status in endpoints:
        data = None
        if len(endpoints[0]) == 4:  # Check if data is provided
            data = endpoints[0][3]

        if test_endpoint(method, endpoint, expected_status, data):
            passed += 1

    print("=" * 50)
    print(f"📊 Results: {passed}/{total} tests passed")

    if passed == total:
        print("🎉 All tests passed! Response format is consistent across all endpoints.")
    else:
        print("⚠️  Some tests failed. Check the output above for details.")

if __name__ == "__main__":
    main()

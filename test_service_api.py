#!/usr/bin/env python3
"""
Test script for Service Selection API
This script demonstrates how to use the service selection endpoints
"""

import requests
import json

# Base URL for the API
BASE_URL = "http://localhost:8000"

def test_service_selection():
    """Test the service selection functionality"""

    print("=== Testing Service Selection API ===\n")

    # Test 1: Text input - direct service selection
    print("1. Testing text input service selection...")
    text_payload = {
        "user_id": "user_1",
        "service_text": "Delivery",
        "input_type": "text"
    }

    try:
        response = requests.post(f"{BASE_URL}/service/select", json=text_payload)
        print(f"Status: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}\n")
    except Exception as e:
        print(f"Error: {e}\n")

    # Test 2: Voice input - AI service detection
    print("2. Testing voice input service detection...")
    voice_payload = {
        "user_id": "user_2",
        "service_text": "I want delivery at my house",
        "input_type": "voice"
    }

    try:
        response = requests.post(f"{BASE_URL}/service/select", json=voice_payload)
        print(f"Status: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}\n")
    except Exception as e:
        print(f"Error: {e}\n")

    # Test 3: Get user services
    print("3. Testing get user services...")
    try:
        response = requests.get(f"{BASE_URL}/service/user/user_1")
        print(f"Status: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}\n")
    except Exception as e:
        print(f"Error: {e}\n")

    # Test 4: Get available services
    print("4. Testing get available services...")
    try:
        response = requests.get(f"{BASE_URL}/service/available")
        print(f"Status: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}\n")
    except Exception as e:
        print(f"Error: {e}\n")

    # Test 5: Service detection (for testing)
    print("5. Testing service detection...")
    try:
        response = requests.post(f"{BASE_URL}/service/detect", params={"text": "I'll pick it up myself"})
        print(f"Status: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}\n")
    except Exception as e:
        print(f"Error: {e}\n")

def test_example_scenarios():
    """Test the example scenarios from the requirements"""

    print("=== Testing Example Scenarios ===\n")

    scenarios = [
        {
            "name": "Delivery - I want delivery at my house",
            "text": "I want delivery at my house",
            "expected": "Should detect Delivery service"
        },
        {
            "name": "Delivery - Please deliver my order to my home",
            "text": "Please deliver my order to my home",
            "expected": "Should detect Delivery service"
        },
        {
            "name": "Pickup - I'll pick it up myself",
            "text": "I'll pick it up myself",
            "expected": "Should detect Pickup service"
        },
        {
            "name": "Pickup - I want takeaway",
            "text": "I want takeaway",
            "expected": "Should detect Pickup service"
        },
        {
            "name": "Catering - I need catering for my event",
            "text": "I need catering for my event",
            "expected": "Should detect Catering service"
        },
        {
            "name": "Catering - Can you provide food service for a party?",
            "text": "Can you provide food service for a party?",
            "expected": "Should detect Catering service"
        },
        {
            "name": "Events - I want to book for an event",
            "text": "I want to book for an event",
            "expected": "Should detect Events service"
        },
        {
            "name": "Events - I'm planning an event, can you handle it?",
            "text": "I'm planning an event, can you handle it?",
            "expected": "Should detect Events service"
        }
    ]

    for i, scenario in enumerate(scenarios, 1):
        print(f"{i}. {scenario['name']}")
        print(f"   Text: '{scenario['text']}'")
        print(f"   Expected: {scenario['expected']}")

        payload = {
            "user_id": f"user_{i + 10}",  # Use different user IDs
            "service_text": scenario['text'],
            "input_type": "voice"
        }

        try:
            response = requests.post(f"{BASE_URL}/service/select", json=payload)
            if response.status_code == 200:
                data = response.json()
                print(f"   Result: Primary service = '{data.get('selected_service')}', Detected = {data.get('detected_services')}")
            else:
                print(f"   Error: {response.status_code} - {response.text}")
        except Exception as e:
            print(f"   Error: {e}")

        print()

def test_user_service_management():
    """Test user service management functionality"""

    print("=== Testing User Service Management ===\n")

    # Test 1: Add multiple services for a user
    print("1. Adding multiple services for user_100...")
    services_to_add = [
        {"service_text": "Delivery", "input_type": "text"},
        {"service_text": "I need catering for my event", "input_type": "voice"},
        {"service_text": "Pickup", "input_type": "text"}
    ]

    for i, service_data in enumerate(services_to_add, 1):
        payload = {
            "user_id": "user_100",
            **service_data
        }

        try:
            response = requests.post(f"{BASE_URL}/service/select", json=payload)
            if response.status_code == 200:
                data = response.json()
                print(f"   ✅ Added service {i}: {data.get('selected_service')}")
            else:
                print(f"   ❌ Failed to add service {i}: {response.status_code}")
        except Exception as e:
            print(f"   ❌ Error adding service {i}: {e}")

    print()

    # Test 2: Get all services for user
    print("2. Getting all services for user_100...")
    try:
        response = requests.get(f"{BASE_URL}/service/user/user_100")
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Found {data.get('total_services')} services:")
            for service in data.get('services', []):
                print(f"      - {service.get('service_name')} (Input: {service.get('input_type')}, selected at: {service.get('selected_at')})")
        else:
            print(f"   ❌ Error: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Error: {e}")

    print()

    # Test 3: Get latest service for user
    print("3. Getting latest service for user_100...")
    try:
        response = requests.get(f"{BASE_URL}/service/user/user_100/latest")
        if response.status_code == 200:
            data = response.json()
            service = data.get('service', {})
            print(f"   ✅ Latest service: {service.get('service_name')} (Input: {service.get('input_type')}, selected at: {service.get('selected_at')})")
        else:
            print(f"   ❌ Error: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Error: {e}")

    print()

def test_error_cases():
    """Test error handling"""

    print("=== Testing Error Cases ===\n")

    # Test 1: Empty service text
    print("1. Testing empty service text...")
    payload = {
        "user_id": "user_1",
        "service_text": "",
        "input_type": "text"
    }

    try:
        response = requests.post(f"{BASE_URL}/service/select", json=payload)
        print(f"   Status: {response.status_code}")
        if response.status_code != 200:
            print(f"   ✅ Correctly rejected empty text: {response.json().get('detail')}")
        else:
            print(f"   ❌ Should have rejected empty text")
    except Exception as e:
        print(f"   Error: {e}")

    print()

    # Test 2: Invalid input type
    print("2. Testing invalid input type...")
    payload = {
        "user_id": "user_1",
        "service_text": "Delivery",
        "input_type": "invalid"
    }

    try:
        response = requests.post(f"{BASE_URL}/service/select", json=payload)
        print(f"   Status: {response.status_code}")
        if response.status_code != 200:
            print(f"   ✅ Correctly rejected invalid input type: {response.json().get('detail')}")
        else:
            print(f"   ❌ Should have rejected invalid input type")
    except Exception as e:
        print(f"   Error: {e}")

    print()

    # Test 3: Non-existent user
    print("3. Testing with non-existent user...")
    payload = {
        "user_id": "user_99999",
        "service_text": "Delivery",
        "input_type": "text"
    }

    try:
        response = requests.post(f"{BASE_URL}/service/select", json=payload)
        print(f"   Status: {response.status_code}")
        print(f"   Response: {json.dumps(response.json(), indent=2)}")
    except Exception as e:
        print(f"   Error: {e}")

    print()

if __name__ == "__main__":
    print("Service Selection API Test Script")
    print("Make sure the FastAPI server is running on http://localhost:8000")
    print("=" * 50)

    # Run basic tests
    test_service_selection()

    # Run example scenarios
    test_example_scenarios()

    # Run user service management tests
    test_user_service_management()

    # Run error case tests
    test_error_cases()

    print("Test completed!")

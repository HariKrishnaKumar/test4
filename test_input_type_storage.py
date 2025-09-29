#!/usr/bin/env python3
"""
Test script to verify input_type storage in both language and service APIs
"""

import requests
import json

BASE_URL = "http://localhost:8000"

def test_language_input_type_storage():
    """Test that input_type is stored in sessions table for language selection"""

    print("=== Testing Language Input Type Storage ===\n")

    # Test 1: Text input
    print("1. Testing text input language selection...")
    text_payload = {
        "session_id": "test_lang_text_1",
        "user_id": 1,
        "language_text": "Spanish",
        "input_type": "text"
    }

    try:
        response = requests.post(f"{BASE_URL}/language/select", json=text_payload)
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Text input successful: {data.get('message')}")
            print(f"Selected Language: {data.get('selected_language')}")
        else:
            print(f"❌ Error: {response.text}")
    except Exception as e:
        print(f"❌ Exception: {e}")

    print()

    # Test 2: Voice input
    print("2. Testing voice input language selection...")
    voice_payload = {
        "session_id": "test_lang_voice_1",
        "user_id": 2,
        "language_text": "I can speak French and German",
        "input_type": "voice"
    }

    try:
        response = requests.post(f"{BASE_URL}/language/select", json=voice_payload)
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Voice input successful: {data.get('message')}")
            print(f"Selected Language: {data.get('selected_language')}")
            print(f"Detected Languages: {data.get('detected_languages')}")
        else:
            print(f"❌ Error: {response.text}")
    except Exception as e:
        print(f"❌ Exception: {e}")

    print()

    # Test 3: Get session language (to verify input_type is stored)
    print("3. Getting session language to verify storage...")
    try:
        response = requests.get(f"{BASE_URL}/language/session/test_lang_text_1")
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Session language retrieved: {data.get('language')}")
            # Note: The current API doesn't return input_type, but it's stored in DB
        else:
            print(f"❌ Error: {response.text}")
    except Exception as e:
        print(f"❌ Exception: {e}")

    print()

def test_service_input_type_storage():
    """Test that input_type is stored in user_services table for service selection"""

    print("=== Testing Service Input Type Storage ===\n")

    # Test 1: Text input
    print("1. Testing text input service selection...")
    text_payload = {
        "user_id": "test_service_text_1",
        "service_text": "Delivery",
        "input_type": "text"
    }

    try:
        response = requests.post(f"{BASE_URL}/service/select", json=text_payload)
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Text input successful: {data.get('message')}")
            print(f"Selected Service: {data.get('selected_service')}")
        else:
            print(f"❌ Error: {response.text}")
    except Exception as e:
        print(f"❌ Exception: {e}")

    print()

    # Test 2: Voice input
    print("2. Testing voice input service selection...")
    voice_payload = {
        "user_id": "test_service_voice_1",
        "service_text": "I want delivery at my house",
        "input_type": "voice"
    }

    try:
        response = requests.post(f"{BASE_URL}/service/select", json=voice_payload)
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Voice input successful: {data.get('message')}")
            print(f"Selected Service: {data.get('selected_service')}")
            print(f"Detected Services: {data.get('detected_services')}")
        else:
            print(f"❌ Error: {response.text}")
    except Exception as e:
        print(f"❌ Exception: {e}")

    print()

    # Test 3: Get user services (to verify input_type is stored)
    print("3. Getting user services to verify input_type storage...")
    try:
        response = requests.get(f"{BASE_URL}/service/user/test_service_text_1")
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ User services retrieved:")
            for service in data.get('services', []):
                print(f"  - Service: {service.get('service_name')}")
                print(f"    Input Type: {service.get('input_type')}")
                print(f"    Selected At: {service.get('selected_at')}")
        else:
            print(f"❌ Error: {response.text}")
    except Exception as e:
        print(f"❌ Exception: {e}")

    print()

    # Test 4: Get voice input user services
    print("4. Getting voice input user services...")
    try:
        response = requests.get(f"{BASE_URL}/service/user/test_service_voice_1")
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ User services retrieved:")
            for service in data.get('services', []):
                print(f"  - Service: {service.get('service_name')}")
                print(f"    Input Type: {service.get('input_type')}")
                print(f"    Selected At: {service.get('selected_at')}")
        else:
            print(f"❌ Error: {response.text}")
    except Exception as e:
        print(f"❌ Exception: {e}")

    print()

def test_multiple_input_types():
    """Test multiple input types for the same user"""

    print("=== Testing Multiple Input Types for Same User ===\n")

    user_id = "test_multi_input_user"

    # Add services with different input types
    services = [
        {"service_text": "Pickup", "input_type": "text"},
        {"service_text": "I need catering for my event", "input_type": "voice"},
        {"service_text": "Events", "input_type": "text"},
        {"service_text": "I want to book for an event", "input_type": "voice"}
    ]

    for i, service_data in enumerate(services, 1):
        print(f"{i}. Adding service: {service_data['service_text']} ({service_data['input_type']})")

        payload = {
            "user_id": user_id,
            **service_data
        }

        try:
            response = requests.post(f"{BASE_URL}/service/select", json=payload)
            if response.status_code == 200:
                data = response.json()
                print(f"   ✅ Success: {data.get('selected_service')}")
            else:
                print(f"   ❌ Error: {response.status_code}")
        except Exception as e:
            print(f"   ❌ Exception: {e}")

    print()

    # Get all services for this user
    print("Getting all services for this user...")
    try:
        response = requests.get(f"{BASE_URL}/service/user/{user_id}")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Found {data.get('total_services')} services:")
            for service in data.get('services', []):
                print(f"  - {service.get('service_name')} (Input: {service.get('input_type')})")
        else:
            print(f"❌ Error: {response.text}")
    except Exception as e:
        print(f"❌ Exception: {e}")

if __name__ == "__main__":
    print("Input Type Storage Test Script")
    print("Make sure the FastAPI server is running on http://localhost:8000")
    print("=" * 60)

    # Test language input type storage
    test_language_input_type_storage()

    # Test service input type storage
    test_service_input_type_storage()

    # Test multiple input types
    test_multiple_input_types()

    print("Input type storage test completed!")
    print("\nNote: Check the database directly to verify input_type values are stored correctly.")


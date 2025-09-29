#!/usr/bin/env python3
"""
Test script for Language Selection API
This script demonstrates how to use the language selection endpoints
"""

import requests
import json

# Base URL for the API
BASE_URL = "http://localhost:8000"

def test_language_selection():
    """Test the language selection functionality"""

    print("=== Testing Language Selection API ===\n")

    # Test 1: Text input - direct language selection
    print("1. Testing text input language selection...")
    text_payload = {
        "session_id": "test_session_123",
        "user_id": 1,
        "language_text": "Spanish",
        "input_type": "text"
    }

    try:
        response = requests.post(f"{BASE_URL}/language/select", json=text_payload)
        print(f"Status: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}\n")
    except Exception as e:
        print(f"Error: {e}\n")

    # Test 2: Voice input - AI language detection
    print("2. Testing voice input language detection...")
    voice_payload = {
        "session_id": "test_session_456",
        "user_id": 2,
        "language_text": "I can speak French, but I also understand German",
        "input_type": "voice"
    }

    try:
        response = requests.post(f"{BASE_URL}/language/select", json=voice_payload)
        print(f"Status: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}\n")
    except Exception as e:
        print(f"Error: {e}\n")

    # Test 3: Get session language
    print("3. Testing get session language...")
    try:
        response = requests.get(f"{BASE_URL}/language/session/test_session_123")
        print(f"Status: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}\n")
    except Exception as e:
        print(f"Error: {e}\n")

    # Test 4: Get available languages
    print("4. Testing get available languages...")
    try:
        response = requests.get(f"{BASE_URL}/language/available")
        print(f"Status: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}\n")
    except Exception as e:
        print(f"Error: {e}\n")

    # Test 5: Language detection (for testing)
    print("5. Testing language detection...")
    try:
        response = requests.post(f"{BASE_URL}/language/detect", params={"text": "I don't know Chinese"})
        print(f"Status: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}\n")
    except Exception as e:
        print(f"Error: {e}\n")

def test_example_scenarios():
    """Test the example scenarios from the requirements"""

    print("=== Testing Example Scenarios ===\n")

    scenarios = [
        {
            "name": "Scenario 1: I don't know Chinese",
            "text": "I don't know Chinese",
            "expected": "Should detect English as primary language"
        },
        {
            "name": "Scenario 2: My language is Spanish",
            "text": "My language is Spanish",
            "expected": "Should detect Spanish as primary language"
        },
        {
            "name": "Scenario 3: Multiple languages",
            "text": "I can speak French, but I also understand German",
            "expected": "Should detect French and German, with French as primary"
        },
        {
            "name": "Scenario 4: Know all languages",
            "text": "I know all languages",
            "expected": "Should default to English"
        }
    ]

    for i, scenario in enumerate(scenarios, 1):
        print(f"{i}. {scenario['name']}")
        print(f"   Text: '{scenario['text']}'")
        print(f"   Expected: {scenario['expected']}")

        payload = {
            "session_id": f"test_scenario_{i}",
            "user_id": i,
            "language_text": scenario['text'],
            "input_type": "voice"
        }

        try:
            response = requests.post(f"{BASE_URL}/language/select", json=payload)
            if response.status_code == 200:
                data = response.json()
                print(f"   Result: Primary language = '{data.get('selected_language')}', Detected = {data.get('detected_languages')}")
            else:
                print(f"   Error: {response.status_code} - {response.text}")
        except Exception as e:
            print(f"   Error: {e}")

        print()

if __name__ == "__main__":
    print("Language Selection API Test Script")
    print("Make sure the FastAPI server is running on http://localhost:8000")
    print("=" * 50)

    # Run basic tests
    test_language_selection()

    # Run example scenarios
    test_example_scenarios()

    print("Test completed!")

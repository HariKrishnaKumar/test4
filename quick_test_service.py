#!/usr/bin/env python3
"""
Quick test for Service Selection API
"""

import requests
import json

BASE_URL = "http://localhost:8000"

def quick_test():
    print("=== Quick Service API Test ===\n")

    # Test 1: Text input
    print("1. Testing text input...")
    payload = {
        "user_id": "test_user_1",
        "service_text": "Delivery",
        "input_type": "text"
    }

    try:
        response = requests.post(f"{BASE_URL}/service/select", json=payload)
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Success: {data.get('message')}")
            print(f"Selected Service: {data.get('selected_service')}")
        else:
            print(f"❌ Error: {response.text}")
    except Exception as e:
        print(f"❌ Exception: {e}")

    print()

    # Test 2: Voice input
    print("2. Testing voice input...")
    payload = {
        "user_id": "test_user_2",
        "service_text": "I want delivery at my house",
        "input_type": "voice"
    }

    try:
        response = requests.post(f"{BASE_URL}/service/select", json=payload)
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Success: {data.get('message')}")
            print(f"Selected Service: {data.get('selected_service')}")
            print(f"Detected Services: {data.get('detected_services')}")
        else:
            print(f"❌ Error: {response.text}")
    except Exception as e:
        print(f"❌ Exception: {e}")

    print()

    # Test 3: Get available services
    print("3. Testing get available services...")
    try:
        response = requests.get(f"{BASE_URL}/service/available")
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            services = response.json()
            print(f"✅ Found {len(services)} available services:")
            for service in services:
                print(f"  - {service.get('service_name')}: {service.get('service_description')}")
        else:
            print(f"❌ Error: {response.text}")
    except Exception as e:
        print(f"❌ Exception: {e}")

if __name__ == "__main__":
    quick_test()


#!/usr/bin/env python3
"""
Example of integrating language selection with the existing conversation flow
"""

import requests
import json

BASE_URL = "http://localhost:8000"

def example_conversation_flow():
    """
    Example showing how language selection integrates with conversation flow
    """

    print("=== Language Selection Integration Example ===\n")

    # Step 1: User starts a new session
    session_id = "user_session_123"
    user_id = 1

    print("1. User starts new session...")
    print(f"   Session ID: {session_id}")
    print(f"   User ID: {user_id}\n")

    # Step 2: Language selection via voice
    print("2. User selects language via voice...")
    voice_payload = {
        "session_id": session_id,
        "user_id": user_id,
        "language_text": "I can speak French, but I also understand German",
        "input_type": "voice"
    }

    try:
        response = requests.post(f"{BASE_URL}/language/select", json=voice_payload)
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Language selected: {data['selected_language']}")
            print(f"   📝 Detected languages: {data['detected_languages']}")
            print(f"   💾 Session updated with language preference\n")
        else:
            print(f"   ❌ Error: {response.status_code} - {response.text}\n")
            return
    except Exception as e:
        print(f"   ❌ Error: {e}\n")
        return

    # Step 3: Get session language (for verification)
    print("3. Verifying session language...")
    try:
        response = requests.get(f"{BASE_URL}/language/session/{session_id}")
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Session language: {data['language']}\n")
        else:
            print(f"   ❌ Error: {response.status_code} - {response.text}\n")
    except Exception as e:
        print(f"   ❌ Error: {e}\n")

    # Step 4: Continue with conversation (using existing voice routes)
    print("4. Continuing with conversation using selected language...")
    print("   (This would integrate with existing voice/answer endpoint)")

    # Example of how the existing voice endpoint would use the language
    voice_answer_payload = {
        "session_id": session_id,
        "user_id": user_id,
        "question_key": "food_preference",
        "voice_text": "Je préfère la nourriture végétarienne"  # French text
    }

    print(f"   Voice answer payload: {json.dumps(voice_answer_payload, indent=2)}")
    print("   (The existing voice processing would now know the user prefers French)\n")

    # Step 5: Language change example
    print("5. User changes language preference...")
    text_payload = {
        "session_id": session_id,
        "user_id": user_id,
        "language_text": "English",
        "input_type": "text"
    }

    try:
        response = requests.post(f"{BASE_URL}/language/select", json=text_payload)
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Language changed to: {data['selected_language']}\n")
        else:
            print(f"   ❌ Error: {response.status_code} - {response.text}\n")
    except Exception as e:
        print(f"   ❌ Error: {e}\n")

    print("=== Integration Example Complete ===")

def example_multiple_language_scenarios():
    """
    Example showing different language selection scenarios
    """

    print("\n=== Multiple Language Scenarios ===\n")

    scenarios = [
        {
            "name": "Single Language Selection",
            "text": "My language is Spanish",
            "input_type": "voice"
        },
        {
            "name": "Multiple Language Detection",
            "text": "I can speak French, but I also understand German",
            "input_type": "voice"
        },
        {
            "name": "Negative Language Statement",
            "text": "I don't know Chinese",
            "input_type": "voice"
        },
        {
            "name": "All Languages Statement",
            "text": "I know all languages",
            "input_type": "voice"
        },
        {
            "name": "Direct Text Selection",
            "text": "Italian",
            "input_type": "text"
        }
    ]

    for i, scenario in enumerate(scenarios, 1):
        print(f"{i}. {scenario['name']}")
        print(f"   Input: '{scenario['text']}' ({scenario['input_type']})")

        payload = {
            "session_id": f"scenario_{i}",
            "user_id": i,
            "language_text": scenario['text'],
            "input_type": scenario['input_type']
        }

        try:
            response = requests.post(f"{BASE_URL}/language/select", json=payload)
            if response.status_code == 200:
                data = response.json()
                print(f"   ✅ Result: {data['selected_language']}")
                if data.get('detected_languages'):
                    print(f"   📝 Detected: {data['detected_languages']}")
            else:
                print(f"   ❌ Error: {response.status_code}")
        except Exception as e:
            print(f"   ❌ Error: {e}")

        print()

if __name__ == "__main__":
    print("Language Selection Integration Examples")
    print("Make sure the FastAPI server is running on http://localhost:8000")
    print("=" * 60)

    # Run integration example
    example_conversation_flow()

    # Run multiple language scenarios
    example_multiple_language_scenarios()

    print("All examples completed!")

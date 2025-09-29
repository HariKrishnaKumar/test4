import uuid
from datetime import datetime
from typing import Dict, List

# Constants
SUPPORTED_LANGUAGES = {
    'en': 'English', 'es': 'Spanish', 'fr': 'French', 'it': 'Italian',
    'de': 'German', 'pt': 'Portuguese', 'ru': 'Russian', 'ja': 'Japanese',
    'ko': 'Korean', 'zh': 'Chinese'
}

DIETARY_PREFERENCES = ['vegetarian', 'non-vegetarian', 'vegan']
CUISINES = ['chinese', 'italian', 'japanese', 'mexican', 'indian', 'thai', 'american', 'mediterranean']
HUNGER_LEVELS = ['snacks', 'hungry', 'super hungry', 'just a bite']

class Utils:
    @staticmethod
    def generate_conversation_id() -> str:
        """Generate unique conversation ID"""
        return f"conv_{int(datetime.now().timestamp())}_{str(uuid.uuid4())[:8]}"

    @staticmethod
    def get_current_timestamp() -> str:
        """Get current timestamp in ISO format"""
        return datetime.now().isoformat()

    @staticmethod
    def validate_dietary_preference(preference: str) -> str:
        """Validate and normalize dietary preference"""
        if not preference:
            return None
        return preference.lower() if preference.lower() in DIETARY_PREFERENCES else None

    @staticmethod
    def validate_cuisine(cuisine: str) -> str:
        """Validate and normalize cuisine"""
        if not cuisine:
            return None
        return cuisine.lower() if cuisine.lower() in CUISINES else None

    @staticmethod
    def validate_hunger_level(hunger: str) -> str:
        """Validate and normalize hunger level"""
        if not hunger:
            return None
        return hunger.lower() if hunger.lower() in HUNGER_LEVELS else None

    @staticmethod
    def get_language_name(code: str) -> str:
        """Get language name from code"""
        return SUPPORTED_LANGUAGES.get(code.lower(), 'English')

    @staticmethod
    def validate_language(code: str) -> bool:
        """Check if language code is supported"""
        print(SUPPORTED_LANGUAGES)
        return code.lower() in SUPPORTED_LANGUAGES

    @staticmethod
    def get_all_options() -> Dict:
        """Get all available options"""
        return {
            "dietary_preferences": DIETARY_PREFERENCES,
            "cuisines": CUISINES,
            "hunger_levels": HUNGER_LEVELS,
            "supported_languages": SUPPORTED_LANGUAGES
        }

# language_service.py
from typing import Optional, List, Dict
import google.generativeai as genai
import os
from sqlalchemy.orm import Session
import json
from models.language import Language
from models.conversation import Session as SessionModel
from dotenv import load_dotenv
import re

load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

class LanguageService:
    """Service for processing language selection with AI support"""

    def __init__(self):
        self.api_key = GEMINI_API_KEY
        if not self.api_key:
            raise ValueError("GEMINI_API_KEY not found in environment variables")

        # Configure Gemini
        genai.configure(api_key=self.api_key)
        self.model = genai.GenerativeModel('gemini-2.5-pro')

    def detect_languages_from_text(self, text: str) -> List[str]:
        """
        Detect languages from user text using AI
        Returns a list of detected languages
        """
        prompt = f"""You are a language detection assistant. Analyze the following text and extract all mentioned languages.

User text: "{text}"

Instructions:
1. Identify all languages mentioned in the text
2. Return only the language names in English (e.g., "English", "Spanish", "French", "German", "Chinese")
3. If multiple languages are mentioned, return them as a comma-separated list
4. If no specific language is mentioned, return "English" as default
5. Return only the language names, nothing else

Examples:
- "I speak Spanish" -> Spanish
- "I know French and German" -> French, German
- "I don't know Chinese" -> English
- "My language is Spanish" -> Spanish
- "I can speak French, but I also understand German" -> French, German
- "I know all languages" -> English

Response:"""

        try:
            response = self.model.generate_content(prompt)
            languages_text = response.text.strip()

            # Parse the response and clean up
            languages = [lang.strip() for lang in languages_text.split(',')]
            languages = [lang for lang in languages if lang and lang.lower() != 'none']

            # If no languages detected, default to English
            if not languages:
                languages = ['English']

            return languages

        except Exception as e:
            print(f"Language detection error: {str(e)}")
            return ['English']  # Default fallback

    def get_primary_language(self, languages: List[str]) -> str:
        """
        Get the primary language from a list of languages
        For session storage, we'll use the first language mentioned
        """
        if not languages:
            return 'English'

        # Return the first language as primary
        return languages[0]

    def validate_language(self, language_name: str) -> bool:
        """
        Validate if the language name is valid
        """
        if not language_name or not language_name.strip():
            return False

        # Basic validation - check if it's a reasonable language name
        language_name = language_name.strip()
        if len(language_name) < 2 or len(language_name) > 50:
            return False

        # Check for common language patterns
        common_languages = [
            'English', 'Spanish', 'French', 'German', 'Italian', 'Portuguese',
            'Chinese', 'Japanese', 'Korean', 'Arabic', 'Hindi', 'Russian',
            'Dutch', 'Swedish', 'Norwegian', 'Danish', 'Finnish', 'Polish',
            'Czech', 'Hungarian', 'Greek', 'Turkish', 'Hebrew', 'Thai',
            'Vietnamese', 'Indonesian', 'Malay', 'Filipino', 'Tagalog'
        ]

        # Check if it matches any common language (case insensitive)
        for lang in common_languages:
            if language_name.lower() == lang.lower():
                return True

        # If not in common list, still allow it (user might specify a dialect or variant)
        return True

    def get_language_code(self, language_name: str) -> str:
        """
        Get ISO 639-1 language code for a language name
        """
        language_codes = {
            'English': 'en',
            'Spanish': 'es',
            'French': 'fr',
            'German': 'de',
            'Italian': 'it',
            'Portuguese': 'pt',
            'Chinese': 'zh',
            'Japanese': 'ja',
            'Korean': 'ko',
            'Arabic': 'ar',
            'Hindi': 'hi',
            'Russian': 'ru',
            'Dutch': 'nl',
            'Swedish': 'sv',
            'Norwegian': 'no',
            'Danish': 'da',
            'Finnish': 'fi',
            'Polish': 'pl',
            'Czech': 'cs',
            'Hungarian': 'hu',
            'Greek': 'el',
            'Turkish': 'tr',
            'Hebrew': 'he',
            'Thai': 'th',
            'Vietnamese': 'vi',
            'Indonesian': 'id',
            'Malay': 'ms',
            'Filipino': 'fil',
            'Tagalog': 'tl'
        }

        return language_codes.get(language_name, 'en')  # Default to English

    def save_language_to_session(self, db: Session, session_id: str, user_id: Optional[int], language_name: str, input_type: str = None) -> bool:
        """
        Save language selection to session table
        """
        try:
            # Get or create session
            session = db.query(SessionModel).filter(SessionModel.id == session_id).first()

            if not session:
                # Create new session
                session = SessionModel(
                    id=session_id,
                    user_id=user_id,
                    language=language_name,
                    input_type=input_type
                )
                db.add(session)
            else:
                # Update existing session
                session.language = language_name
                session.input_type = input_type
                if user_id:
                    session.user_id = user_id

            db.commit()
            return True

        except Exception as e:
            print(f"Error saving language to session: {str(e)}")
            db.rollback()
            return False

    def get_language_from_session(self, db: Session, session_id: str) -> Optional[str]:
        """
        Get language from session
        """
        try:
            session = db.query(SessionModel).filter(SessionModel.id == session_id).first()
            return session.language if session else None
        except Exception as e:
            print(f"Error getting language from session: {str(e)}")
            return None

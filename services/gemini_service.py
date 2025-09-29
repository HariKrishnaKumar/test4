# gemini_service.py
from typing import Optional, List, Dict
import google.generativeai as genai
import os
from sqlalchemy.orm import Session
import json
from models.conversation import AnswerMaster
from dotenv import load_dotenv

load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

class GeminiAnalyzer:
    """Service for analyzing user text and matching with predefined answers using Gemini AI"""

    def __init__(self):
        self.api_key = GEMINI_API_KEY
        if not self.api_key:
            raise ValueError("GEMINI_API_KEY not found in environment variables")

        # Configure Gemini
        genai.configure(api_key=self.api_key)
        self.model = genai.GenerativeModel('gemini-2.5-pro')

    def analyze_user_response(
        self,
        user_text: str,
        question_key: str,
        available_answers: List[Dict[str, str]]
    ) -> Optional[str]:
        """
        Analyze user text and return the most suitable answer key using Gemini AI

        Args:
            user_text: The user's free text response
            question_key: The question being answered
            available_answers: List of dicts with 'answer_key' and 'answer_text'

        Returns:
            The answer_key that best matches the user's response
        """

        if not available_answers:
            return None

        # Prepare the answer options for the prompt
        answer_options = "\n".join([
            f"- {ans['answer_key']}: {ans['answer_text']}"
            for ans in available_answers
        ])

        prompt = f"""You are an intelligent assistant that categorizes user responses into predefined categories.

Given the user's message, determine which category it best fits into.

User Message: "{user_text}"

Available Categories:
{answer_options}

Instructions:
1. Analyze the user's message carefully
2. Match it with the most appropriate category from the list
3. Return ONLY the category key (answer_key), nothing else
4. If the user is asking for suggestions, recommendations, or general questions (not selecting a category), return "SUGGESTION_REQUEST"
5. If no category matches well and it's not a suggestion request, return "NONE"

Response:"""

        try:
            response = self.model.generate_content(prompt)
            answer = response.text.strip()

            # Validate that the returned answer_key exists in our options
            valid_keys = [ans['answer_key'] for ans in available_answers]
            if answer in valid_keys:
                return answer
            elif answer == "NONE":
                return "SORRY_DONT_UNDERSTAND"
            elif answer == "SUGGESTION_REQUEST":
                return "SUGGESTION_REQUEST"
            else:
                # If Gemini returns something unexpected, return sorry message
                print(f"Gemini returned unexpected answer: {answer}")
                return "SORRY_DONT_UNDERSTAND"

        except Exception as e:
            print(f"Gemini API error: {str(e)}")
            return None

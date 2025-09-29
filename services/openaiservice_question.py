# openai_service.py
from typing import Optional, List, Dict
import openai
from sqlalchemy.orm import Session
import json
import os
from models.conversation import AnswerMaster
from dotenv import load_dotenv

load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

class OpenAIAnalyzer:
    """Service for analyzing user text and matching with predefined answers"""
    def __init__(self):
        self.api_key = OPENAI_API_KEY
        if not self.api_key:
            raise ValueError("OPENAI_API_KEY not found in environment variables")

    def analyze_user_response(
        self,
        user_text: str,
        question_key: str,
        available_answers: List[Dict[str, str]]
    ) -> Optional[str]:
        """
        Analyze user text and return the most suitable answer key

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
4. If no category matches well, return "NONE"

Response:"""

        try:
            client = openai.OpenAI(api_key=self.api_key)
            response = client.chat.completions.create(
                model="gpt-4o-mini",  # or "gpt-4" for better accuracy
                messages=[
                    {"role": "system", "content": "You are a classification assistant. Return only the category key."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.1,  # Low temperature for consistent classification
                max_tokens=50
            )

            answer = response.choices[0].message.content.strip()

            # Validate that the returned answer_key exists in our options
            valid_keys = [ans['answer_key'] for ans in available_answers]
            if answer in valid_keys:
                return answer
            elif answer == "NONE":
                return None
            else:
                # If OpenAI returns something unexpected, return None
                return None

        except Exception as e:
            print(f"OpenAI API error: {str(e)}")
            return None

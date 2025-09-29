from sqlalchemy.orm import Session
from typing import Optional, Dict, Any
from datetime import datetime
from models.conversation import ConversationEntry, QuestionMaster, AnswerMaster
from app.schemas.conversation import ConversationEntryCreate, ConversationEntryResponse
from helpers.validators import validate_question_key, validate_answer_key, get_active_answers_for_question
from helpers.voice_matcher import match_voice_to_answer
from services.openaiservice_question import OpenAIAnalyzer
from services.gemini_service import GeminiAnalyzer
from services.food_suggestion_service import FoodSuggestionService


class ConversationService:
    """Service layer for handling conversation entries"""

    def __init__(self):
        ai_analyzer = OpenAIAnalyzer()

    @staticmethod
    def create_conversation_entry(
        db: Session,
        entry_data: ConversationEntryCreate
    ) -> ConversationEntryResponse:
        """Create a new conversation entry with AI analysis"""

        # Create AI analyzer instance
        ai_analyzer = OpenAIAnalyzer()

        print("=== RAW entry_data ===", entry_data)
        print("=== entry_data.dict() ===", entry_data.dict())
        print("=== responseText specifically ===", entry_data.responseText)
        print("=== responseText type ===", type(entry_data.responseText))
        print("=== answer_key specifically ===", entry_data.answer_key)
        print("=== answer_key type ===", type(entry_data.answer_key))

        # Validate question exists
        if not validate_question_key(db, entry_data.question_key):
            raise ValueError(f"Invalid question key: {entry_data.question_key}")

        # entry_dict = entry_data.dict()
        # print(f"response_text in dict: {entry_dict.get('response_text')}")


        # print("=== DEBUG: Raw entry_data ===")
        # print(f"Type: {type(entry_data)}")
        # print(f"entry_data: {entry_data}")
        # print(f"entry_data.dict(): {entry_data.dict()}")
        # print(f"response_text specifically: {entry_data.response_text}")
        # print(f"response_text type: {type(entry_data.response_text)}")

        # Let's also check all fields
        print("=== All fields ===")
        for field_name in entry_data.__fields__.keys():
            field_value = getattr(entry_data, field_name, 'NOT_FOUND')
            # print(f"{field_name}: {field_value} (type: {type(field_value)})")

        # Validate answer if provided (either manually or by AI)
        if entry_data.answer_key:
            if not validate_answer_key(db, entry_data.answer_key, entry_data.question_key):
                # print(f"Invalid answer_key: {entry_data.answer_key}, setting to None")
                entry_data.answer_key = None

        # Get the dict first
        entry_dict = entry_data.dict()

        # Ensure response_text is set (use responseText if response_text is not provided)
        if not entry_dict.get('response_text') and entry_dict.get('responseText'):
            entry_dict['response_text'] = entry_dict['responseText']

        # Debug: Print the final entry_dict before database creation
        print(f"=== Final entry_dict before DB creation ===")
        print(f"answer_key: {entry_dict.get('answer_key')}")
        print(f"response_text: {entry_dict.get('response_text')}")
        print(f"responseText: {entry_dict.get('responseText')}")

        try:
            # Create conversation entry with explicit field mapping
            print("=== Creating entry with data ===")
            print(f"entry_dict: {entry_dict}")

            # Check if response_text is in the dict
            print(f"response_text in dict: {entry_dict.get('response_text')}")

            db_entry = ConversationEntry(
                session_id=entry_dict.get('session_id'),
                user_id=entry_dict.get('user_id'),
                question_key=entry_dict['question_key'],
                answer_key=entry_dict.get('answer_key'),
                custom_input=entry_dict.get('custom_input'),
                response_text=entry_dict.get('response_text'),
                select_type=entry_dict.get('select_type'),
                created_at=datetime.now()
            )

            print(f"=== DB Entry before save ===")
            print(f"db_entry.response_text: {db_entry.response_text}")

            db.add(db_entry)
            db.commit()
            db.refresh(db_entry)
            print("Entry created successfully with ID:", db_entry.id)

            return ConversationEntryResponse.from_orm(db_entry)

        except Exception as e:
            db.rollback()
            print(f"Database error: {str(e)}")
            raise ValueError(f"Failed to create conversation entry: {str(e)}")

    @staticmethod
    def analyze_text_only(
        db: Session,
        question_key: str,
        user_text: str
    ) -> Optional[str]:
        """
        Standalone method to analyze text and return matching answer_key
        without creating a conversation entry
        """

        # Create AI analyzer instance
        ai_analyzer = OpenAIAnalyzer()

        # Validate question exists
        if not validate_question_key(db, question_key):
            raise ValueError(f"Invalid question key: {question_key}")

        # Get available answers
        available_answers = get_active_answers_for_question(db, question_key)

        if not available_answers:
            return None

        # Use OpenAI to analyze
        return ai_analyzer.analyze_user_response(
            user_text=user_text,
            question_key=question_key,
            available_answers=available_answers
        )

    @staticmethod
    def process_select_answer(
        db: Session,
        session_id: Optional[str],
        user_id: Optional[int],
        question_key: str,
        answer_key: str,
        response_text: Optional[str] = None
    ) -> ConversationEntryResponse:
        """Process a select-type answer"""

        # If response_text is provided, use Gemini AI to find the best answer
        if response_text:
            print(f"=== Gemini AI Analysis for Select Mode ===")
            print(f"User input: {response_text}")
            print(f"Question: {question_key}")

            try:
                ai_analyzer = GeminiAnalyzer()
                available_answers = get_active_answers_for_question(db, question_key)

                if available_answers:
                    # available_answers is already in the correct format (list of dicts)
                    answer_list = available_answers

                    print(f"Available answers: {answer_list}")

                    # Use Gemini AI to find the best matching answer
                    ai_matched_answer = ai_analyzer.analyze_user_response(
                        user_text=response_text,
                        question_key=question_key,
                        available_answers=answer_list
                    )

                    print(f"Gemini AI matched answer: {ai_matched_answer}")

                    # Handle different AI responses
                    if ai_matched_answer == "SORRY_DONT_UNDERSTAND":
                        print("Gemini couldn't understand the input, using sorry message")
                        answer_key = "SORRY_DONT_UNDERSTAND"
                    elif ai_matched_answer == "SUGGESTION_REQUEST":
                        print("User requested suggestions, will provide food recommendations")
                        answer_key = "SUGGESTION_REQUEST"
                    elif ai_matched_answer and ai_matched_answer not in ["SORRY_DONT_UNDERSTAND", "SUGGESTION_REQUEST"]:
                        answer_key = ai_matched_answer
                        print(f"Using Gemini AI matched answer: {answer_key}")
                    else:
                        print(f"Using original answer_key: {answer_key}")
            except Exception as e:
                print(f"Gemini AI error, falling back to original answer_key: {str(e)}")
                print(f"Using original answer_key: {answer_key}")
        else:
            print(f"No response_text provided, using original answer_key: {answer_key}")

        print(f"=== Final answer_key before creating entry_data: {answer_key}")

        entry_data = ConversationEntryCreate(
            session_id=session_id,
            user_id=user_id,
            question_key=question_key,
            answer_key=answer_key,
            responseText=response_text,  # Use responseText field name
            select_type="select"
        )

        # Get user language from session
        user_language = ConversationService.get_user_language(db, session_id)

        # Handle special cases before creating conversation entry
        if answer_key == "SORRY_DONT_UNDERSTAND":
            return ConversationService._handle_sorry_response(entry_data)
        elif answer_key == "SUGGESTION_REQUEST":
            return ConversationService._handle_suggestion_request(db, entry_data, response_text)

        # For normal responses, add language info to the response
        conversation_entry = ConversationService.create_conversation_entry(db, entry_data)

        # Add language info to the response (this will be handled by the route)
        return conversation_entry

    @staticmethod
    def process_voice_answer(
        db: Session,
        session_id: Optional[str],
        user_id: Optional[int],
        question_key: str,
        voice_text: str,
        response_text: str
    ) -> Dict[str, Any]:
        """Process a voice-type answer"""

        # Use Gemini AI to find the best matching answer from voice_text
        print(f"=== Gemini AI Analysis for Voice Mode ===")
        print(f"Voice text: {voice_text}")
        print(f"Question: {question_key}")

        matched_answer_key = None
        try:
            ai_analyzer = GeminiAnalyzer()
            available_answers = get_active_answers_for_question(db, question_key)

            if available_answers:
                # available_answers is already in the correct format (list of dicts)
                answer_list = available_answers

                print(f"Available answers: {answer_list}")

                # Use Gemini AI to find the best matching answer
                matched_answer_key = ai_analyzer.analyze_user_response(
                    user_text=voice_text,
                    question_key=question_key,
                    available_answers=answer_list
                )

                print(f"Gemini AI matched answer: {matched_answer_key}")

                # Handle special cases for voice mode
                if matched_answer_key == "SORRY_DONT_UNDERSTAND":
                    print("Gemini couldn't understand the voice input")
                elif matched_answer_key == "SUGGESTION_REQUEST":
                    print("User requested suggestions via voice")
        except Exception as e:
            print(f"Gemini AI error: {str(e)}")
            matched_answer_key = None

        entry_data = ConversationEntryCreate(
            session_id=session_id,
            user_id=user_id,
            question_key=question_key,
            answer_key=matched_answer_key,
            custom_input=voice_text,
            responseText=response_text,  # Use responseText field name
            select_type="voice"
        )

        # Get user language from session for all cases
        user_language = ConversationService.get_user_language(db, session_id)

        # Handle special cases before creating conversation entry
        if matched_answer_key == "SORRY_DONT_UNDERSTAND":
            conversation_entry = ConversationService._handle_sorry_response(entry_data)
        elif matched_answer_key == "SUGGESTION_REQUEST":
            # Get food suggestions
            suggestion_response = ConversationService.get_food_suggestions(
                db=db,
                user_text=voice_text,
                user_language=user_language
            )

            print(f"=== Suggestion Response Generated ===")
            print(f"User Language: {user_language}")
            print(f"Suggestion Response: {suggestion_response}")

            # Create conversation entry with suggestion response
            entry_data.responseText = suggestion_response
            print(f"=== Entry Data Before DB Creation ===")
            print(f"entry_data.responseText: {entry_data.responseText}")

            conversation_entry = ConversationService.create_conversation_entry(db, entry_data)
        else:
            conversation_entry = ConversationService.create_conversation_entry(db, entry_data)

        # Return entry with match status and language info
        return {
            "conversation_entry": conversation_entry,
            "matched": matched_answer_key is not None,
            "matched_answer_key": matched_answer_key,
            "voice_text": voice_text,
            "user_language": user_language
        }

    @staticmethod
    def get_next_question(
        db: Session,
        session_id: str,
        current_question_key: Optional[str] = None
    ) -> Optional[QuestionMaster]:
        """Get the next question in the wizard flow"""

        if current_question_key:
            # Get current question order
            current_question = db.query(QuestionMaster).filter(
                QuestionMaster.question_key == current_question_key
            ).first()

            if current_question:
                # Get next question by order
                next_question = db.query(QuestionMaster).filter(
                    QuestionMaster.question_order > current_question.question_order,
                    QuestionMaster.is_active == True
                ).order_by(QuestionMaster.question_order).first()

                return next_question
        else:
            # Get first question
            return db.query(QuestionMaster).filter(
                QuestionMaster.is_active == True
            ).order_by(QuestionMaster.question_order).first()

        return None

    @staticmethod
    def get_conversation_history(
        db: Session,
        session_id: str
    ) -> list:
        """Get conversation history for a session"""

        entries = db.query(ConversationEntry).filter(
            ConversationEntry.session_id == session_id
        ).order_by(ConversationEntry.created_at).all()

        return [ConversationEntryResponse.from_orm(entry) for entry in entries]

    @staticmethod
    def _handle_sorry_response(entry_data: ConversationEntryCreate) -> ConversationEntryResponse:
        """Handle cases where AI couldn't understand the user input"""
        sorry_message = "Sorry, I don't understand your request. Could you please rephrase or select from the available options?"

        # Create a special response for sorry cases
        return ConversationEntryResponse(
            id=0,  # Temporary ID for sorry responses
            session_id=entry_data.session_id,
            user_id=entry_data.user_id,
            question_key=entry_data.question_key,
            answer_key="SORRY_DONT_UNDERSTAND",
            custom_input=entry_data.custom_input,
            responseText=sorry_message,
            created_at=datetime.now()
        )

    @staticmethod
    def _handle_suggestion_request(db: Session, entry_data: ConversationEntryCreate, user_text: str) -> ConversationEntryResponse:
        """Handle food suggestion requests"""
        try:
            # Extract dietary preference from user text
            dietary_preference = ConversationService._extract_dietary_preference(user_text)

            # Get food suggestions
            suggestion_service = FoodSuggestionService(db)
            suggestions = suggestion_service.get_suggestions_by_dietary_preference(dietary_preference, limit=5)

            # Format the response
            suggestion_response = suggestion_service.format_suggestions_response(suggestions, dietary_preference)

            # Create response
            return ConversationEntryResponse(
                id=0,  # Temporary ID for suggestion responses
                session_id=entry_data.session_id,
                user_id=entry_data.user_id,
                question_key=entry_data.question_key,
                answer_key="SUGGESTION_REQUEST",
                custom_input=entry_data.custom_input,
                responseText=suggestion_response,
                created_at=datetime.now()
            )

        except Exception as e:
            print(f"Error handling suggestion request: {str(e)}")
            # Fallback to sorry response
            return ConversationService._handle_sorry_response(entry_data)

    @staticmethod
    def _extract_dietary_preference(user_text: str) -> str:
        """Extract dietary preference from user text"""
        user_text_lower = user_text.lower()

        if 'vegan' in user_text_lower:
            return 'vegan'
        elif 'non-veg' in user_text_lower or 'non veg' in user_text_lower or 'nonvegetarian' in user_text_lower:
            return 'non-veg'
        elif 'veg' in user_text_lower or 'vegetarian' in user_text_lower:
            return 'veg'
        else:
            # Default to vegetarian if unclear
            return 'veg'

    @staticmethod
    def get_user_language(db: Session, session_id: str) -> str:
        """Get user language from sessions table"""
        try:
            from models.conversation import Session
            session = db.query(Session).filter(Session.id == session_id).first()
            if session and session.language:
                return session.language
            return "en"  # Default to English
        except Exception as e:
            print(f"Error getting user language: {str(e)}")
            return "en"  # Default to English

    @staticmethod
    def get_food_suggestions(db: Session, user_text: str, user_language: str = "en") -> str:
        """Get food suggestions with language support"""
        try:
            # Extract dietary preference from user text
            dietary_preference = ConversationService._extract_dietary_preference(user_text)

            # Get food suggestions
            suggestion_service = FoodSuggestionService(db)
            suggestions = suggestion_service.get_suggestions_by_dietary_preference(dietary_preference, limit=5)

            # Format the response with language support
            suggestion_response = suggestion_service.format_suggestions_response_with_language(
                suggestions, dietary_preference, user_language
            )

            return suggestion_response

        except Exception as e:
            print(f"Error getting food suggestions: {str(e)}")
            return "Sorry, I couldn't get food suggestions at the moment. Please try again later."

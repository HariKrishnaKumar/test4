# models/response_master.py
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Text, Float, Boolean, func, Enum
from sqlalchemy.orm import relationship
from datetime import datetime
from database.database import Base
import enum


class InputMethod(enum.Enum):
    VOICE = "voice"
    TEXT = "text"


class ConversationStatus(enum.Enum):
    ACTIVE = "active"
    COMPLETED = "completed"
    ABANDONED = "abandoned"


class QuestionMaster(Base):
    """Master table for predefined questions"""
    __tablename__ = 'question_masters'

    id = Column(Integer, primary_key=True, index=True)
    question_key = Column(String(100), nullable=False, unique=True)  # e.g., "dietary_preference", "cuisine_type", "hunger_level"
    question_text = Column(Text, nullable=False)  # "What is your dietary preference?"
    question_order = Column(Integer, nullable=False)  # Sequence of questions
    is_active = Column(Boolean, default=True)
    language = Column(String(10), default='en')

    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())

    # Relationships
    responses = relationship("UserResponse", back_populates="question")


class UserResponse(Base):
    """User responses to questions"""
    __tablename__ = 'user_responses'

    id = Column(Integer, primary_key=True, index=True)
    device_id = Column(String(255), nullable=False, index=True)
    session_id = Column(Integer, ForeignKey('conversation_sessions.id'), nullable=False, index=True)

    question_id = Column(Integer, ForeignKey('question_masters.id'), nullable=False)

    # User response details
    user_input = Column(Text, nullable=False)  # "I want vegetarian spicy food"
    input_method = Column(Enum(InputMethod), nullable=False)  # voice or text

    # AI processing
    ai_response = Column(Text, nullable=True)  # AI's response to user
    extracted_preferences = Column(Text, nullable=True)  # JSON string of extracted preferences

    # Conversation flow
    sequence_no = Column(Integer, nullable=False)  # Order within session
    is_satisfied = Column(Boolean, default=False)  # Whether question was fully answered
    needs_clarification = Column(Boolean, default=False)

    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())

    # Relationships
    question = relationship("QuestionMaster", back_populates="responses")
    session = relationship("ConversationSession", back_populates="responses")


class ConversationSession(Base):
    """Track conversation sessions"""
    __tablename__ = 'conversation_sessions'

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String(255), nullable=False, unique=True, index=True)
    device_id = Column(String(255), nullable=False, index=True)

    # Session details
    # status = Column(Enum(ConversationStatus), default=ConversationStatus.ACTIVE)
    status = Column(String(50), default="ACTIVE")  # Fixed: Changed from Enum to String
    current_question_id = Column(Integer, ForeignKey('question_masters.id'), nullable=True)
    total_questions = Column(Integer, default=0)
    completed_questions = Column(Integer, default=0)

    # Final preferences (JSON string)
    final_preferences = Column(Text, nullable=True)  # Consolidated user preferences

    # Timestamps
    started_at = Column(DateTime, server_default=func.now())
    completed_at = Column(DateTime, nullable=True)
    last_activity_at = Column(DateTime, server_default=func.now())

    # Relationships
    responses = relationship("UserResponse", back_populates="session")
    current_question = relationship("QuestionMaster", foreign_keys=[current_question_id])


class FoodPreference(Base):
    """Extracted and structured food preferences"""
    __tablename__ = 'food_preferences'

    id = Column(Integer, primary_key=True, index=True)
    device_id = Column(String(255), nullable=False, index=True)
    session_id = Column(String(255), ForeignKey('conversation_sessions.session_id'), nullable=False)

    # Preference categories
    dietary_type = Column(String(100), nullable=True)  # vegetarian, non-veg, vegan
    cuisine_preference = Column(String(100), nullable=True)  # chinese, italian, indian
    spice_level = Column(String(50), nullable=True)  # mild, medium, spicy
    hunger_level = Column(String(50), nullable=True)  # light, moderate, very hungry

    # Additional preferences
    allergies = Column(Text, nullable=True)  # JSON array of allergies
    dislikes = Column(Text, nullable=True)  # JSON array of dislikes
    special_requests = Column(Text, nullable=True)  # Any special requirements

    # Price and timing preferences
    budget_range = Column(String(50), nullable=True)  # low, medium, high
    preferred_meal_time = Column(String(50), nullable=True)  # breakfast, lunch, dinner

    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())


# Legacy model - keeping for backward compatibility
class ResponseMaster(Base):
    __tablename__ = 'response_masters'

    id = Column(Integer, primary_key=True, index=True)
    device_id = Column(Text, nullable=False)
    session_id = Column(String(255), nullable=True)
    sequence_no = Column(String(64), nullable=False)
    language = Column(String(100), nullable=False)
    conversation_request = Column(Text, nullable=False)
    conversation_response = Column(Text, nullable=False)

    # Timestamps
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())


# Legacy model - keeping for backward compatibility
class ConversationLog(Base):
    __tablename__ = 'conversation_logs'

    id = Column(Integer, primary_key=True, index=True)
    page_no = Column(String(100), nullable=False)
    message_text = Column(Text, nullable=False)
    language = Column(String(100), nullable=False)
    response_text = Column(Text, nullable=False)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())

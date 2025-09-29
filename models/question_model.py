"""
SQLAlchemy models based on the migration file
"""
from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime
from sqlalchemy.sql import func

Base = declarative_base()


class User(Base):
    """User model"""
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, autoincrement=True)
    # Add other user fields as per your existing users table
    # username = Column(String(100), unique=True, nullable=False)
    # email = Column(String(255), unique=True, nullable=False)
    # password_hash = Column(String(255), nullable=False)
    device_info = Column(String(255), nullable=True)
    # created_at = Column(DateTime, server_default=func.now())
    # updated_at = Column(DateTime, nullable=True)

    # Relationships
    sessions = relationship("Session", back_populates="user")
    conversation_entries = relationship("ConversationEntry", back_populates="user")


class Session(Base):
    """Session model for user conversations"""
    __tablename__ = "sessions"

    id = Column(String(100), primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    language = Column(String(10), nullable=False)
    created_at = Column(DateTime, server_default=func.now())

    # Relationships
    user = relationship("User", back_populates="sessions")
    conversation_entries = relationship("ConversationEntry", back_populates="session")


class QuestionMaster(Base):
    """Question Master model - stores English questions"""
    __tablename__ = "question_masters"

    id = Column(Integer, primary_key=True, autoincrement=True)
    question_key = Column(String(100), unique=True, nullable=False)
    question_text = Column(Text, nullable=False)
    question_order = Column(Integer, nullable=False)
    type = Column(String(50), nullable=True)
    is_active = Column(Boolean, server_default="1", default=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, nullable=True)

    # Relationships
    translations = relationship("QuestionTranslation", back_populates="question")
    answers = relationship("AnswerMaster", back_populates="question")
    conversation_entries = relationship("ConversationEntry", back_populates="question")


class QuestionTranslation(Base):
    """Question Translation model - stores translated questions"""
    __tablename__ = "question_translations"

    id = Column(Integer, primary_key=True, autoincrement=True)
    question_key = Column(String(100), ForeignKey("question_masters.question_key"), nullable=False)
    language = Column(String(10), nullable=False)
    translated_text = Column(Text, nullable=False)
    variant = Column(String(50), nullable=True)

    # Relationships
    question = relationship("QuestionMaster", back_populates="translations")

    # Composite unique constraint (handled by migration)
    __table_args__ = (
        # This is already handled in the migration with uq_question_lang
    )


class AnswerMaster(Base):
    """Answer Master model - stores English answers"""
    __tablename__ = "answer_masters"

    id = Column(Integer, primary_key=True, autoincrement=True)
    answer_key = Column(String(100), unique=True, nullable=False)
    question_key = Column(String(100), ForeignKey("question_masters.question_key"), nullable=False)
    answer_text = Column(Text, nullable=False)
    answer_order = Column(Integer, nullable=True)
    is_active = Column(Boolean, server_default="1", default=True)
    created_at = Column(DateTime, server_default=func.now())

    # Relationships
    question = relationship("QuestionMaster", back_populates="answers")
    translations = relationship("AnswerTranslation", back_populates="answer")
    conversation_entries = relationship("ConversationEntry", back_populates="answer")


class AnswerTranslation(Base):
    """Answer Translation model - stores translated answers"""
    __tablename__ = "answer_translations"

    id = Column(Integer, primary_key=True, autoincrement=True)
    answer_key = Column(String(100), ForeignKey("answer_masters.answer_key"), nullable=False)
    language = Column(String(10), nullable=False)
    translated_text = Column(Text, nullable=False)
    variant = Column(String(50), nullable=True)

    # Relationships
    answer = relationship("AnswerMaster", back_populates="translations")

    # Composite unique constraint (handled by migration)
    __table_args__ = (
        # This is already handled in the migration with uq_answer_lang
    )


class ConversationEntry(Base):
    """Conversation Entry model - stores user responses and conversation flow"""
    __tablename__ = "conversation_entries"

    id = Column(Integer, primary_key=True, autoincrement=True)
    session_id = Column(String(100), ForeignKey("sessions.id"), nullable=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    question_key = Column(String(100), ForeignKey("question_masters.question_key"), nullable=False)
    answer_key = Column(String(100), ForeignKey("answer_masters.answer_key"), nullable=True)
    custom_input = Column(Text, nullable=True)  # For free-text responses
    response_text = Column(Text, nullable=True)  # Processed/formatted response
    created_at = Column(DateTime, server_default=func.now())

    # Relationships
    session = relationship("Session", back_populates="conversation_entries")
    user = relationship("User", back_populates="conversation_entries")
    question = relationship("QuestionMaster", back_populates="conversation_entries")
    answer = relationship("AnswerMaster", back_populates="conversation_entries")


# Index definitions (these are created by the migration, so they're just for reference)
"""
Indexes created by migration:
- idx_sessions_user_id on sessions(user_id)
- idx_question_masters_active on question_masters(is_active)
- idx_question_masters_order on question_masters(question_order)
- idx_question_translations_lang on question_translations(language)
- idx_answer_masters_question on answer_masters(question_key)
- idx_answer_masters_active on answer_masters(is_active)
- idx_answer_translations_lang on answer_translations(language)
- idx_conversation_entries_session on conversation_entries(session_id)
- idx_conversation_entries_user on conversation_entries(user_id)
- idx_conversation_entries_question on conversation_entries(question_key)
- idx_conversation_entries_created on conversation_entries(created_at)
"""


# Helper function to get model classes by name
def get_model_class(model_name: str):
    """Get model class by name"""
    model_mapping = {
        'User': User,
        'Session': Session,
        'QuestionMaster': QuestionMaster,
        'QuestionTranslation': QuestionTranslation,
        'AnswerMaster': AnswerMaster,
        'AnswerTranslation': AnswerTranslation,
        'ConversationEntry': ConversationEntry,
    }
    return model_mapping.get(model_name)

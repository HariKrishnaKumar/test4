# app/schemas/conversation.py
from pydantic import BaseModel, Field, validator
from typing import Optional, List
from datetime import datetime

class ConversationEntryCreate(BaseModel):
    session_id: Optional[str] = None
    user_id: Optional[int] = None
    question_key: str
    answer_key: Optional[str] = None
    custom_input: Optional[str] = None
    responseText: Optional[str] = None
    select_type: str = Field(..., pattern="^(select|voice)$")

    @validator('answer_key', pre=True)
    def convert_null_string(cls, v):
        """Convert string 'null' or JSON null to None"""
        if v == 'null' or v == 'NULL' or v is None:
            return None
        return v

    @validator('responseText', pre=True)
    def convert_null_string_response(cls, v):
        """Convert string 'null' or JSON null to None for response_text too"""
        if v == 'null' or v == 'NULL' or v is None:
            return None
        return v

    class Config:
        from_attributes = True

class AnswerResponse(BaseModel):
    answer_key: str
    answer_text: str
    answer_order: Optional[int] = None

    class Config:
        from_attributes = True

class QuestionResponse(BaseModel):
    question_key: str
    question_text: str
    question_order: int
    type: Optional[str] = None
    answers: List[AnswerResponse] = []

    class Config:
        from_attributes = True

class ConversationEntryBase(BaseModel):
    session_id: Optional[str] = None
    user_id: Optional[int] = None
    question_key: str
    answer_key: Optional[str] = None
    custom_input: Optional[str] = None
    responseText: Optional[str] = None

class ConversationEntryResponse(ConversationEntryBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True

class SelectAnswerRequest(BaseModel):
    session_id: Optional[str] = None
    user_id: Optional[int] = None
    question_key: str
    answer_key: Optional[str] = None  # Changed from str to Optional[str]
    responseText: Optional[str] = None

    @validator('answer_key', pre=True)
    def convert_null_string(cls, v):
        """Convert string 'null' or JSON null to None"""
        if v == 'null' or v == 'NULL' or v is None:
            return None
        return v

    @validator('responseText', pre=True)
    def convert_null_string_response(cls, v):
        """Convert string 'null' or JSON null to None for response_text too"""
        if v == 'null' or v == 'NULL' or v is None:
            return None
        return v

class VoiceAnswerRequest(BaseModel):
    session_id: Optional[str] = None
    user_id: Optional[int] = None
    question_key: str
    voice_text: Optional[str]

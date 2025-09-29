from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.sql import func
from sqlalchemy.ext.declarative import declarative_base
from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, List

Base = declarative_base()

class Language(Base):
    __tablename__ = 'languages'

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    language_name = Column(String(100), nullable=False, unique=True)
    language_code = Column(String(10), nullable=True)  # ISO 639-1 code
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

# Pydantic Models for API
class LanguageBase(BaseModel):
    language_name: str
    language_code: Optional[str] = None

class LanguageCreate(LanguageBase):
    pass

class LanguageResponse(LanguageBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class LanguageSelectionRequest(BaseModel):
    session_id: str
    user_id: Optional[int] = None
    language_text: str
    input_type: str = Field(..., pattern="^(text|voice)$")  # text or voice input

class LanguageSelectionResponse(BaseModel):
    success: bool
    message: str
    selected_language: Optional[str] = None
    session_id: str
    user_id: Optional[int] = None
    detected_languages: Optional[List[str]] = None  # For multiple language detection

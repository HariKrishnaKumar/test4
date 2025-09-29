from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, List

# Import the same Base from conversation.py to ensure consistency
from models.conversation import Base

class Service(Base):
    __tablename__ = 'services'

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    service_name = Column(String(100), nullable=False, unique=True)
    service_description = Column(String(255), nullable=True)
    is_active = Column(String(10), default='true')  # 'true' or 'false' as string
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    user_services = relationship("UserService", back_populates="service")

class UserService(Base):
    __tablename__ = 'user_services'

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(String(100), ForeignKey('users.id'), nullable=False)
    service_id = Column(Integer, ForeignKey('services.id'), nullable=False)
    input_type = Column(String(10), nullable=True)  # 'text' or 'voice'
    selected_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships - using string references to avoid import issues
    service = relationship("Service", back_populates="user_services")

# Pydantic Models for API
class ServiceBase(BaseModel):
    service_name: str
    service_description: Optional[str] = None
    is_active: str = 'true'

class ServiceCreate(ServiceBase):
    pass

class ServiceResponse(ServiceBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class ServiceSelectionRequest(BaseModel):
    user_id: str
    service_text: str
    input_type: str = Field(..., pattern="^(text|voice)$")  # text or voice input

class ServiceSelectionResponse(BaseModel):
    success: bool
    message: str
    selected_service: Optional[str] = None
    user_id: str
    detected_services: Optional[List[str]] = None  # For multiple service detection
    service_id: Optional[int] = None

class UserServiceResponse(BaseModel):
    id: int
    user_id: str
    service_id: int
    service_name: str
    input_type: Optional[str] = None
    selected_at: datetime

    class Config:
        from_attributes = True

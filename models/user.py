from sqlalchemy import Column, Integer, String, Boolean, DateTime
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from database.database import Base

class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, index=True)
    mobile_number = Column(String(15), unique=True, nullable=False)
    otp = Column(String(6), nullable=True)  # store OTP temporarily
    is_verified = Column(Boolean, default=False)
    name = Column(String(100), nullable=True)
    alternate_contact = Column(String(15), nullable=True)
    floor_or_office = Column(String(255), nullable=True)
    is_guest = Column(Boolean, default=True)
    device_info = Column(String(255), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    address = Column(String(200), nullable=True)
    token = Column(String(500), nullable=True)  # For storing user tokens

    # Note: Removed invalid relationships to non-existent models
    # If you need relationships to Session or ConversationEntry models,
    # create those models first and then add the relationships back

from pydantic import BaseModel, EmailStr, constr
from typing import Optional


class MobileLogin(BaseModel):
    mobile: str

class OTPVerify(BaseModel):
    mobile: str
    otp: str

class OTPVerifyRequest(BaseModel):
    mobile: str
    otp: str

class RegisterRequest(BaseModel):
    name: str
    mobile: constr(pattern=r'^[6-9]\d{9}$')  # ✅ Use pattern in Pydantic v2
    email: EmailStr
    password: constr(min_length=6)


class UpdateProfile(BaseModel):
    full_name: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[str] = None

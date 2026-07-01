from pydantic import BaseModel, Field, EmailStr
from datetime import date
from typing import Optional


class Token(BaseModel):
    """JWT token response"""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    """Token payload data"""
    user_id: int
    email: str


class LoginRequest(BaseModel):
    """Login request — uses email instead of username"""
    email: EmailStr = Field(..., description="Registered email address")
    password: str = Field(..., description="Password")


class LoginResponse(BaseModel):
    """Login response"""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    user_id: int
    name: str          # Full display name
    email: str         # Auth identifier, stored in session
    message: str = "Login successful"


class RefreshTokenRequest(BaseModel):
    """Refresh token request"""
    refresh_token: str = Field(..., description="Refresh token")


class UserProfile(BaseModel):
    """User profile response"""
    id: int
    name: str           # Full display name
    email: Optional[str] = None
    dob: date
    mobile: int
    is_active: bool = True
    health_conditions: list = []

    class Config:
        from_attributes = True
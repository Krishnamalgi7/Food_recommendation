from pydantic import BaseModel, Field
from datetime import date


class Token(BaseModel):
    """JWT token response"""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    """Token payload data"""
    user_id: int
    username: str


class LoginRequest(BaseModel):
    """Login request"""
    name: str = Field(..., description="Username")
    password: str = Field(..., description="Password")


class LoginResponse(BaseModel):
    """Login response"""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    user_id: int
    name: str
    message: str = "Login successful"


class RefreshTokenRequest(BaseModel):
    """Refresh token request"""
    refresh_token: str = Field(..., description="Refresh token")


class UserProfile(BaseModel):
    """User profile response"""
    id: int
    name: str
    dob: date
    mobile: int
    health_conditions: list = []

    class Config:
        from_attributes = True
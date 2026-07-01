from pydantic import BaseModel, Field, validator, EmailStr
from datetime import date, datetime
from typing import Optional
import re


class UserCreate(BaseModel):
    name: str = Field(..., min_length=2, max_length=100, description="Full name (2-100 characters)")
    email: EmailStr = Field(..., description="Email address used for login")
    password: str = Field(..., min_length=8, max_length=100, description="Password (minimum 8 characters)")
    dob: str = Field(..., description="Date of birth in DD/MM/YYYY format")
    mobile: int = Field(..., description="Mobile number")

    @validator('name')
    def validate_name(cls, v):
        v = v.strip()
        if not v:
            raise ValueError('Full name cannot be empty')
        if not re.match(r'^[a-zA-Z0-9 _-]+$', v):
            raise ValueError('Name can only contain letters, numbers, spaces, underscores, and hyphens')
        return v

    @validator('password')
    def validate_password(cls, v):
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters long')
        if not any(c.isalpha() for c in v):
            raise ValueError('Password must contain at least one letter')
        if not any(c.isdigit() for c in v):
            raise ValueError('Password must contain at least one number')
        if not re.search(r'[!@#$%^&*(),.?":{}|<>_\-+=]', v):
            raise ValueError('Password must contain at least one special character (!@#$%^&*(),.?":{}|<>_-+=)')
        return v

    @validator('dob')
    def validate_dob(cls, v):
        try:
            dob_date = datetime.strptime(v, "%d/%m/%Y").date()
        except ValueError:
            raise ValueError('Date of birth must be in DD/MM/YYYY format (e.g., 15/06/1995)')

        today = date.today()
        if dob_date >= today:
            raise ValueError('Date of birth must be in the past')

        age = today.year - dob_date.year - ((today.month, today.day) < (dob_date.month, dob_date.day))
        if age < 13:
            raise ValueError('User must be at least 13 years old')
        if age > 120:
            raise ValueError('Invalid date of birth - age cannot exceed 120 years')

        return dob_date  # Return as date object for database storage

    @validator('mobile')
    def validate_mobile(cls, v):
        mobile_str = str(v)
        if v <= 0:
            raise ValueError('Mobile number must be positive')
        if len(mobile_str) < 10 or len(mobile_str) > 15:
            raise ValueError('Mobile number must be between 10 and 15 digits')
        if not mobile_str.isdigit():
            raise ValueError('Mobile number must contain only digits')
        return v


class UserResponse(BaseModel):
    id: int = Field(..., description="User ID")
    name: str = Field(..., description="Full name")
    email: Optional[str] = Field(None, description="Email address")
    dob: date = Field(..., description="Date of birth")
    mobile: int = Field(..., description="Mobile number")

    class Config:
        from_attributes = True


class UserUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=2, max_length=100, description="Full name")
    email: Optional[EmailStr] = Field(None, description="Email address")
    password: Optional[str] = Field(None, min_length=8, max_length=100, description="New password")
    dob: Optional[str] = Field(None, description="Date of birth in DD/MM/YYYY format")
    mobile: Optional[int] = Field(None, description="Mobile number")

    @validator('name')
    def validate_name(cls, v):
        if v is not None:
            v = v.strip()
            if not v:
                raise ValueError('Full name cannot be empty')
            if not re.match(r'^[a-zA-Z0-9 _-]+$', v):
                raise ValueError('Name can only contain letters, numbers, spaces, underscores, and hyphens')
        return v

    @validator('password')
    def validate_password(cls, v):
        if v is not None:
            if len(v) < 8:
                raise ValueError('Password must be at least 8 characters long')
            if not any(c.isalpha() for c in v):
                raise ValueError('Password must contain at least one letter')
            if not any(c.isdigit() for c in v):
                raise ValueError('Password must contain at least one number')
            if not re.search(r'[!@#$%^&*(),.?":{}|<>_\-+=]', v):
                raise ValueError('Password must contain at least one special character')
        return v

    @validator('dob')
    def validate_dob(cls, v):
        if v is not None:
            try:
                dob_date = datetime.strptime(v, "%d/%m/%Y").date()
            except ValueError:
                raise ValueError('Date of birth must be in DD/MM/YYYY format (e.g., 15/06/1995)')

            today = date.today()
            if dob_date >= today:
                raise ValueError('Date of birth must be in the past')

            age = today.year - dob_date.year - ((today.month, today.day) < (dob_date.month, dob_date.day))
            if age < 13:
                raise ValueError('User must be at least 13 years old')
            if age > 120:
                raise ValueError('Invalid date of birth - age cannot exceed 120 years')

            return dob_date
        return v

    @validator('mobile')
    def validate_mobile(cls, v):
        if v is not None:
            mobile_str = str(v)
            if v <= 0:
                raise ValueError('Mobile number must be positive')
            if len(mobile_str) < 10 or len(mobile_str) > 15:
                raise ValueError('Mobile number must be between 10 and 15 digits')
            if not mobile_str.isdigit():
                raise ValueError('Mobile number must contain only digits')
        return v


class PasswordChange(BaseModel):
    old_password: str = Field(..., description="Current password")
    new_password: str = Field(..., min_length=8, description="New password")

    @validator('new_password')
    def validate_new_password(cls, v):
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters long')
        if not any(c.isalpha() for c in v):
            raise ValueError('Password must contain at least one letter')
        if not any(c.isdigit() for c in v):
            raise ValueError('Password must contain at least one number')
        if not re.search(r'[!@#$%^&*(),.?":{}|<>_\-+=]', v):
            raise ValueError('Password must contain at least one special character')
        return v

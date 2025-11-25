from pydantic import BaseModel, Field, validator
from datetime import date, datetime
from typing import Optional
import re


class UserCreate(BaseModel):
    name: str = Field(..., min_length=2, max_length=50, description="Username (2-50 characters)")
    password: str = Field(..., min_length=8, max_length=100, description="Password (minimum 8 characters)")
    dob: str = Field(..., description="Date of birth in DD/MM/YYYY format")
    mobile: int = Field(..., description="Mobile number")

    @validator('name')
    def validate_name(cls, v):
        # Remove extra whitespace
        v = v.strip()
        if not v:
            raise ValueError('Username cannot be empty')

        # Check for valid characters (letters, numbers, spaces, underscores, hyphens)
        if not re.match(r'^[a-zA-Z0-9 _-]+$', v):
            raise ValueError('Username can only contain letters, numbers, spaces, underscores, and hyphens')

        # Must start with a letter
        if not v[0].isalpha():
            raise ValueError('Username must start with a letter')

        return v

    @validator('password')
    def validate_password(cls, v):
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters long')

        # Check for at least one letter
        if not any(c.isalpha() for c in v):
            raise ValueError('Password must contain at least one letter')

        # Check for at least one number
        if not any(c.isdigit() for c in v):
            raise ValueError('Password must contain at least one number')

        # Check for at least one special character
        if not re.search(r'[!@#$%^&*(),.?":{}|<>_\-+=]', v):
            raise ValueError('Password must contain at least one special character (!@#$%^&*(),.?":{}|<>_-+=)')

        return v

    @validator('dob')
    def validate_dob(cls, v):
        # Parse DD/MM/YYYY format
        try:
            dob_date = datetime.strptime(v, "%d/%m/%Y").date()
        except ValueError:
            raise ValueError('Date of birth must be in DD/MM/YYYY format (e.g., 15/06/1995)')

        today = date.today()

        if dob_date >= today:
            raise ValueError('Date of birth must be in the past')

        # Calculate age
        age = today.year - dob_date.year - ((today.month, today.day) < (dob_date.month, dob_date.day))

        if age < 13:
            raise ValueError('User must be at least 13 years old')

        if age > 120:
            raise ValueError('Invalid date of birth - age cannot exceed 120 years')

        return dob_date  # Return as date object for database storage

    @validator('mobile')
    def validate_mobile(cls, v):
        mobile_str = str(v)

        # Check if it's positive
        if v <= 0:
            raise ValueError('Mobile number must be positive')

        # More flexible validation - accept 10-15 digit numbers
        if len(mobile_str) < 10 or len(mobile_str) > 15:
            raise ValueError('Mobile number must be between 10 and 15 digits')

        # Check if all digits
        if not mobile_str.isdigit():
            raise ValueError('Mobile number must contain only digits')

        # Optional: Check if it's an Indian number (starts with 6-9 and is 10 digits)
        # Commenting this out to be more flexible
        # if len(mobile_str) == 10 and not mobile_str[0] in ['6', '7', '8', '9']:
        #     raise ValueError('Indian mobile number must start with 6-9')

        return v


class UserResponse(BaseModel):
    id: int = Field(..., description="User ID")
    name: str = Field(..., description="Username")
    dob: date = Field(..., description="Date of birth")
    mobile: int = Field(..., description="Mobile number")

    class Config:
        from_attributes = True


class UserUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=2, max_length=50, description="Username (2-50 characters)")
    password: Optional[str] = Field(None, min_length=8, max_length=100,
                                    description="New password (minimum 8 characters)")
    dob: Optional[str] = Field(None, description="Date of birth in DD/MM/YYYY format")
    mobile: Optional[int] = Field(None, description="Mobile number")

    @validator('name')
    def validate_name(cls, v):
        if v is not None:
            v = v.strip()
            if not v:
                raise ValueError('Username cannot be empty')

            if not re.match(r'^[a-zA-Z0-9 _-]+$', v):
                raise ValueError('Username can only contain letters, numbers, spaces, underscores, and hyphens')

            if not v[0].isalpha():
                raise ValueError('Username must start with a letter')

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


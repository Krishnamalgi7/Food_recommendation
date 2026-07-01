from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field, EmailStr
from datetime import datetime

from backend.utils.database import get_db
from backend.utils.auth import hash_password, verify_password, get_current_user
from backend.models.custom_tables import User, UserConditionAssociation
from backend.schema.user import UserCreate, UserResponse, UserUpdate, PasswordChange
from backend.utils.logger import CustomLogger

LOGGER = CustomLogger()

router = APIRouter(
    prefix='/users',
    tags=['Users']
)


class UserCreateWithCondition(BaseModel):
    """User creation with health condition — email is the auth identifier"""
    name: str = Field(..., min_length=2, max_length=100, description="Full display name")
    email: EmailStr = Field(..., description="Email address used for login")
    password: str = Field(..., min_length=8, max_length=100)
    dob: str = Field(..., description="Date of birth in DD/MM/YYYY format")
    mobile: int = Field(...)
    condition_id: int = Field(..., description="Health condition ID")


@router.post('/', response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def create_user(request: UserCreate, db: Session = Depends(get_db)):
    """Create a new user (basic, without health condition)"""
    try:
        # Uniqueness check: email
        if db.query(User).filter(User.email == request.email).first():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )

        # Uniqueness check: mobile
        if db.query(User).filter(User.mobile == request.mobile).first():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Mobile number already registered"
            )

        # Parse DOB (validator already converts it to a date object)
        dob_date = request.dob if not isinstance(request.dob, str) else datetime.strptime(request.dob, "%d/%m/%Y").date()

        db_user = User(
            name=request.name,
            email=str(request.email),
            password=hash_password(request.password),
            dob=dob_date,
            mobile=request.mobile,
            is_active=True
        )

        db.add(db_user)
        db.commit()
        db.refresh(db_user)

        LOGGER.info(f"User '{request.name}' ({request.email}) created successfully with ID: {db_user.id}")
        return db_user

    except HTTPException:
        raise
    except Exception as ex:
        LOGGER.error(f"Creating User Failed: {str(ex)}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create user"
        )


@router.post('/register-with-condition', response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def create_user_with_condition(request: UserCreateWithCondition, db: Session = Depends(get_db)):
    """Create a new user with a health condition in one step"""
    try:
        # Uniqueness check: email
        if db.query(User).filter(User.email == request.email).first():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )

        # Uniqueness check: mobile
        if db.query(User).filter(User.mobile == request.mobile).first():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Mobile number already registered"
            )

        # Parse DOB
        try:
            dob_date = datetime.strptime(request.dob, "%d/%m/%Y").date()
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Date of birth must be in DD/MM/YYYY format"
            )

        db_user = User(
            name=request.name,
            email=str(request.email),
            password=hash_password(request.password),
            dob=dob_date,
            mobile=request.mobile,
            is_active=True
        )

        db.add(db_user)
        db.flush()  # get db_user.id before committing

        user_condition = UserConditionAssociation(
            user_id=db_user.id,
            condition_id=request.condition_id
        )
        db.add(user_condition)
        db.commit()
        db.refresh(db_user)

        LOGGER.info(f"User '{request.name}' ({request.email}) created with condition ID: {request.condition_id}")
        return db_user

    except HTTPException:
        raise
    except Exception as ex:
        LOGGER.error(f"Creating User with condition failed: {str(ex)}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create user: {str(ex)}"
        )


@router.get('/me', response_model=UserResponse)
def get_current_user_info(current_user: User = Depends(get_current_user)):
    """Get current user information"""
    return current_user


@router.put('/me', response_model=UserResponse)
def update_user_profile(
        request: UserUpdate,
        current_user: User = Depends(get_current_user),
        db: Session = Depends(get_db)
):
    """Update user profile details (Name, Email, DOB, Mobile)"""
    try:
        if request.name and request.name != current_user.name:
            current_user.name = request.name

        if request.email and str(request.email) != current_user.email:
            if db.query(User).filter(User.email == str(request.email)).first():
                raise HTTPException(status_code=400, detail="Email already registered")
            current_user.email = str(request.email)

        if request.dob:
            if isinstance(request.dob, str):
                current_user.dob = datetime.strptime(request.dob, "%d/%m/%Y").date()
            else:
                current_user.dob = request.dob

        if request.mobile and request.mobile != current_user.mobile:
            if db.query(User).filter(User.mobile == request.mobile).first():
                raise HTTPException(status_code=400, detail="Mobile number already registered")
            current_user.mobile = request.mobile

        db.commit()
        db.refresh(current_user)

        LOGGER.info(f"User {current_user.email} updated profile")
        return current_user

    except HTTPException:
        raise
    except Exception as ex:
        db.rollback()
        LOGGER.error(f"Profile update failed: {str(ex)}")
        raise HTTPException(status_code=500, detail=f"Failed to update profile: {str(ex)}")


@router.put('/change-password')
def change_password(
        password_data: PasswordChange,
        current_user: User = Depends(get_current_user),
        db: Session = Depends(get_db)
):
    """Securely change user password"""
    if not verify_password(password_data.old_password, current_user.password):
        raise HTTPException(status_code=400, detail="Incorrect old password")

    current_user.password = hash_password(password_data.new_password)

    try:
        db.commit()
        LOGGER.info(f"User {current_user.email} changed password")
        return {"message": "Password updated successfully"}
    except Exception as e:
        db.rollback()
        LOGGER.error(f"Password change failed: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to update password")


@router.delete('/me')
def delete_user(
        current_user: User = Depends(get_current_user),
        db: Session = Depends(get_db)
):
    """Deactivate current user account"""
    try:
        current_user.is_active = False
        db.commit()
        return {"message": "Account deactivated successfully"}
    except Exception as ex:
        db.rollback()
        raise HTTPException(status_code=500, detail="Failed to deactivate account")
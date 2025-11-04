from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field

from backend.utils.database import get_db
from backend.utils.auth import hash_password, get_current_user
from backend.models.custom_tables import User, UserConditionAssociation
from backend.schema.user import UserCreate, UserResponse, UserUpdate
from backend.utils.logger import CustomLogger

LOGGER = CustomLogger()

router = APIRouter(
    prefix='/users',
    tags=['Users']
)


class UserCreateWithCondition(BaseModel):
    """User creation with health condition"""
    name: str = Field(..., min_length=2, max_length=50)
    password: str = Field(..., min_length=8, max_length=100)
    dob: str = Field(..., description="Date of birth in DD/MM/YYYY format")
    mobile: int = Field(...)
    condition_id: int = Field(..., description="Health condition ID")


@router.post('/', response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def create_user(request: UserCreate, db: Session = Depends(get_db)):
    """Create a new user (basic)"""
    try:
        existing_user = db.query(User).filter(User.name == request.name).first()
        if existing_user:
            LOGGER.error(f"Username '{request.name}' already exists")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username already exists"
            )

        existing_mobile = db.query(User).filter(User.mobile == request.mobile).first()
        if existing_mobile:
            LOGGER.error(f"Mobile number already registered")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Mobile number already registered"
            )

        hashed_password = hash_password(request.password)

        db_user = User(
            name=request.name,
            password=hashed_password,
            dob=request.dob,
            mobile=request.mobile,
            is_active=True
        )

        db.add(db_user)
        db.commit()
        db.refresh(db_user)

        LOGGER.info(f"User '{request.name}' created successfully with ID: {db_user.id}")
        return db_user

    except HTTPException:
        raise
    except Exception as ex:
        LOGGER.error(f"Creating User Failed due to -{str(ex)}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create user"
        )


@router.post('/register-with-condition', response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def create_user_with_condition(request: UserCreateWithCondition, db: Session = Depends(get_db)):
    """Create a new user with health condition"""
    try:
        # Check if user exists
        existing_user = db.query(User).filter(User.name == request.name).first()
        if existing_user:
            LOGGER.error(f"Username '{request.name}' already exists")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username already exists"
            )

        existing_mobile = db.query(User).filter(User.mobile == request.mobile).first()
        if existing_mobile:
            LOGGER.error(f"Mobile number already registered")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Mobile number already registered"
            )

        # Parse DOB (DD/MM/YYYY format)
        from datetime import datetime
        try:
            dob_date = datetime.strptime(request.dob, "%d/%m/%Y").date()
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Date of birth must be in DD/MM/YYYY format"
            )

        # Hash password
        hashed_password = hash_password(request.password)

        # Create user
        db_user = User(
            name=request.name,
            password=hashed_password,
            dob=dob_date,
            mobile=request.mobile,
            is_active=True
        )

        db.add(db_user)
        db.flush()  # Get user ID without committing

        # Add health condition association
        user_condition = UserConditionAssociation(
            user_id=db_user.id,
            condition_id=request.condition_id
        )
        db.add(user_condition)

        db.commit()
        db.refresh(db_user)

        LOGGER.info(f"User '{request.name}' created with condition ID: {request.condition_id}")
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
def update_user(
        request: UserUpdate,
        current_user: User = Depends(get_current_user),
        db: Session = Depends(get_db)
):
    """Update current user information"""
    try:
        if request.name is not None:
            existing = db.query(User).filter(
                User.name == request.name,
                User.id != current_user.id
            ).first()
            if existing:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Username already exists"
                )
            current_user.name = request.name

        if request.password is not None:
            current_user.password = hash_password(request.password)

        if request.dob is not None:
            current_user.dob = request.dob

        if request.mobile is not None:
            existing = db.query(User).filter(
                User.mobile == request.mobile,
                User.id != current_user.id
            ).first()
            if existing:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Mobile number already registered"
                )
            current_user.mobile = request.mobile

        db.commit()
        db.refresh(current_user)

        LOGGER.info(f"User {current_user.id} updated successfully")
        return current_user

    except HTTPException:
        raise
    except Exception as ex:
        db.rollback()
        LOGGER.error(f"Updating user failed: {str(ex)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update user"
        )


@router.delete('/me')
def delete_user(
        current_user: User = Depends(get_current_user),
        db: Session = Depends(get_db)
):
    """Deactivate current user account"""
    try:
        current_user.is_active = False
        db.commit()

        LOGGER.info(f"User {current_user.id} deactivated")
        return {"message": "Account deactivated successfully"}

    except Exception as ex:
        db.rollback()
        LOGGER.error(f"Deactivating user failed: {str(ex)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to deactivate account"
        )
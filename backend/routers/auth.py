from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from backend.utils.database import get_db
from backend.utils.auth import (
    verify_password,
    create_access_token,
    create_refresh_token,
    decode_token,
    get_current_user
)
from backend.models.custom_tables import User, UserConditionAssociation, HealthCondition
from backend.schema.auth import (
    LoginRequest,
    LoginResponse,
    RefreshTokenRequest,
    Token,
    UserProfile
)
from backend.utils.logger import CustomLogger

LOGGER = CustomLogger()

router = APIRouter(
    prefix='/auth',
    tags=['Authentication']
)


@router.post('/login', response_model=LoginResponse)
def login(request: LoginRequest, db: Session = Depends(get_db)):
    """User login endpoint"""
    try:
        user = db.query(User).filter(User.name == request.name).first()

        if not user:
            LOGGER.warning(f"Login attempt with non-existent username: {request.name}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect username or password"
            )

        if not verify_password(request.password, user.password):
            LOGGER.warning(f"Failed login attempt for user: {request.name}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect username or password"
            )

        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="User account is inactive"
            )

        access_token = create_access_token(data={"sub": user.id, "username": user.name})
        refresh_token = create_refresh_token(data={"sub": user.id})

        LOGGER.info(f"User {request.name} logged in successfully")

        return LoginResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            user_id=user.id,
            name=user.name
        )

    except HTTPException:
        raise
    except Exception as ex:
        LOGGER.error(f"Login failed: {str(ex)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Login failed"
        )


@router.post('/refresh', response_model=Token)
def refresh_token(request: RefreshTokenRequest):
    """Refresh access token using refresh token"""
    try:
        payload = decode_token(request.refresh_token)

        if payload.get("type") != "refresh":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token type"
            )

        user_id = payload.get("sub")
        username = payload.get("username")

        access_token = create_access_token(data={"sub": user_id, "username": username})
        new_refresh_token = create_refresh_token(data={"sub": user_id})

        return Token(
            access_token=access_token,
            refresh_token=new_refresh_token
        )

    except Exception as ex:
        LOGGER.error(f"Token refresh failed: {str(ex)}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not refresh token"
        )


@router.get('/me', response_model=UserProfile)
def get_profile(
        current_user: User = Depends(get_current_user),
        db: Session = Depends(get_db)
):
    """Get current user profile"""
    try:
        user_conditions = db.query(UserConditionAssociation).filter(
            UserConditionAssociation.user_id == current_user.id
        ).all()

        conditions = []
        for uc in user_conditions:
            condition = db.query(HealthCondition).filter(
                HealthCondition.id == uc.condition_id
            ).first()
            if condition:
                conditions.append(condition.name)

        profile = UserProfile(
            id=current_user.id,
            name=current_user.name,
            dob=current_user.dob,
            mobile=current_user.mobile,
            health_conditions=conditions
        )

        return profile

    except Exception as ex:
        LOGGER.error(f"Error fetching profile: {str(ex)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch profile"
        )


@router.post('/logout')
def logout(current_user: User = Depends(get_current_user)):
    """Logout user (client should delete tokens)"""
    LOGGER.info(f"User {current_user.name} logged out")
    return {"message": "Logged out successfully"}
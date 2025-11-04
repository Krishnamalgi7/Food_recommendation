from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from backend.utils.database import get_db
from backend.utils.auth import get_current_user
from backend.models.custom_tables import User, UserConditionAssociation, HealthCondition
from backend.schema.recommendation import (
    RecommendationRequest,
    RecommendationResponse,
    FoodRecommendation,
    UserConditionRequest,
    UserConditionResponse
)
from backend.services.knn_recommender import recommender
from backend.utils.logger import CustomLogger

LOGGER = CustomLogger()

router = APIRouter(
    prefix='/recommendations',
    tags=['Recommendations']
)


@router.post('/user-conditions', response_model=UserConditionResponse)
def add_user_conditions(
        request: UserConditionRequest,
        current_user: User = Depends(get_current_user),
        db: Session = Depends(get_db)
):
    """Add health conditions to user profile"""
    try:
        db.query(UserConditionAssociation).filter(
            UserConditionAssociation.user_id == current_user.id
        ).delete()

        conditions = db.query(HealthCondition).filter(
            HealthCondition.id.in_(request.condition_ids)
        ).all()

        if len(conditions) != len(request.condition_ids):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="One or more invalid condition IDs"
            )

        for condition_id in request.condition_ids:
            association = UserConditionAssociation(
                user_id=current_user.id,
                condition_id=condition_id
            )
            db.add(association)

        db.commit()

        condition_names = [c.name for c in conditions]

        LOGGER.info(f"Added {len(condition_names)} conditions for user {current_user.id}")

        return UserConditionResponse(
            user_id=current_user.id,
            conditions=condition_names,
            message=f"Successfully added {len(condition_names)} health condition(s)"
        )

    except HTTPException:
        raise
    except Exception as ex:
        db.rollback()
        LOGGER.error(f"Error adding user conditions: {str(ex)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to add health conditions"
        )


@router.get('/user-conditions')
def get_user_conditions(
        current_user: User = Depends(get_current_user),
        db: Session = Depends(get_db)
):
    """Get user's health conditions"""
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
                conditions.append({
                    'id': condition.id,
                    'name': condition.name,
                    'description': condition.description
                })

        return {
            'user_id': current_user.id,
            'conditions': conditions,
            'total_count': len(conditions)
        }

    except Exception as ex:
        LOGGER.error(f"Error fetching user conditions: {str(ex)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch health conditions"
        )


@router.post('/generate', response_model=RecommendationResponse)
def generate_recommendations(
        request: RecommendationRequest,
        current_user: User = Depends(get_current_user),
        db: Session = Depends(get_db)
):
    """Generate personalized food recommendations"""
    try:
        user_conditions_count = db.query(UserConditionAssociation).filter(
            UserConditionAssociation.user_id == current_user.id
        ).count()

        if user_conditions_count == 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Please add your health conditions first to get personalized recommendations"
            )

        recommendations = recommender.recommend_foods(
            user_id=current_user.id,
            db=db,
            n_recommendations=request.n_recommendations,
            category_filter=request.category_filter
        )

        nutrient_requirements = recommender.get_user_nutrient_requirements(
            user_id=current_user.id,
            db=db
        )

        LOGGER.info(f"Generated {len(recommendations)} recommendations for user {current_user.id}")

        return RecommendationResponse(
            user_id=current_user.id,
            recommendations=[FoodRecommendation(**rec) for rec in recommendations],
            total_count=len(recommendations),
            nutrient_requirements=nutrient_requirements
        )

    except HTTPException:
        raise
    except Exception as ex:
        LOGGER.error(f"Error generating recommendations: {str(ex)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate recommendations: {str(ex)}"
        )


@router.get('/categories')
def get_food_categories(db: Session = Depends(get_db)):
    """Get list of available food categories"""
    try:
        from backend.models.custom_tables import Food

        categories = db.query(Food.category).distinct().all()
        categories = [c[0] for c in categories if c[0]]

        return {
            'categories': sorted(categories),
            'total_count': len(categories)
        }

    except Exception as ex:
        LOGGER.error(f"Error fetching categories: {str(ex)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch categories"
        )
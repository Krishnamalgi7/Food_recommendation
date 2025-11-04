from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.orm import Session
from typing import List

from backend.utils.database import get_db
from backend.models.custom_tables import HealthCondition
from backend.schema.health import Health, HealthConditionList, HealthConditionResponse
from backend.utils.logger import CustomLogger
import pandas as pd

LOGGER = CustomLogger()

router = APIRouter(
    prefix='/health_condition',
    tags=['Health Conditions']
)


@router.get('/', response_model=List[HealthConditionResponse])
def get_all_health_conditions(db: Session = Depends(get_db)):
    """Get all available health conditions"""
    try:
        conditions = db.query(HealthCondition).all()

        LOGGER.info(f"Retrieved {len(conditions)} health conditions")
        return conditions

    except Exception as ex:
        LOGGER.error(f"Error fetching health conditions: {str(ex)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch health conditions"
        )


@router.get('/{condition_id}', response_model=HealthConditionResponse)
def get_health_condition(condition_id: int, db: Session = Depends(get_db)):
    """Get specific health condition by ID"""
    try:
        condition = db.query(HealthCondition).filter(
            HealthCondition.id == condition_id
        ).first()

        if not condition:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Health condition with ID {condition_id} not found"
            )

        return condition

    except HTTPException:
        raise
    except Exception as ex:
        LOGGER.error(f"Error fetching health condition: {str(ex)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch health condition"
        )


@router.post('/batch', status_code=status.HTTP_201_CREATED)
def insert_health_conditions(
        request: HealthConditionList,
        db: Session = Depends(get_db)
):
    """Batch insert health conditions (admin only)"""
    try:
        data_to_insert = [item.model_dump() for item in request.health_condition]

        df = pd.DataFrame(data_to_insert)

        df.to_sql(
            HealthCondition.__tablename__,
            con=db.bind,
            if_exists="append",
            index=False,
            method="multi",
            chunksize=100,
        )

        db.commit()

        LOGGER.info(f"Inserted {len(data_to_insert)} health conditions")
        return {
            "message": "Health conditions inserted successfully",
            "count": len(data_to_insert)
        }

    except Exception as ex:
        db.rollback()
        LOGGER.error(f"Adding health conditions failed: {str(ex)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to insert health conditions: {str(ex)}"
        )
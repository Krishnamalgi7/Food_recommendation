from typing import List, Optional
from fastapi import APIRouter, Depends, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import func

from backend.schema import food
from backend.utils.logger import CustomLogger
from backend.models import custom_tables
from backend.utils.database import get_db
import sqlalchemy
import pandas as pd

LOGGER = CustomLogger()

router = APIRouter(
    prefix='/food',
    tags=['Food']
)


@router.get('/all')
def get_all_foods_paginated(
        page: int = Query(1, ge=1, description="Page number"),
        limit: int = Query(100, ge=1, le=500, description="Items per page"),
        food_type: Optional[str] = Query(None, description="Filter by type: Veg, Non-Veg, etc."),
        category: Optional[str] = Query(None, description="Filter by category"),
        db: Session = Depends(get_db)
):
    """Get all foods with pagination and filters"""
    try:
        # Build query
        query = db.query(custom_tables.Food)

        # Apply filters
        if food_type:
            # Use exact match (case-insensitive) to avoid matching "Non-Veg" when searching "Veg"
            query = query.filter(func.lower(custom_tables.Food.type) == food_type.lower())

        if category:
            query = query.filter(custom_tables.Food.category.ilike(f"%{category}%"))

        # Get total count
        total_count = query.count()

        # Calculate pagination
        offset = (page - 1) * limit
        total_pages = (total_count + limit - 1) // limit

        # Get paginated results
        foods = query.offset(offset).limit(limit).all()

        # Convert to dict
        food_list = []
        for f in foods:
            food_list.append({
                "id": f.id,
                "name": f.name,
                "category": f.category,
                "type": f.type,
                "ingredients": f.ingredients,
                "nutrients": f.nutrients,
                "price": f.price
            })

        return {
            "foods": food_list,
            "page": page,
            "limit": limit,
            "total_count": total_count,
            "total_pages": total_pages,
            "has_next": page < total_pages,
            "has_prev": page > 1
        }

    except Exception as ex:
        LOGGER.error(f"Getting foods failed: {str(ex)}")
        return {
            "foods": [],
            "page": 1,
            "limit": limit,
            "total_count": 0,
            "total_pages": 0,
            "has_next": False,
            "has_prev": False,
            "error": str(ex)
        }


@router.get('/get_all', response_model=List[food.Food])
def get_all(db: Session = Depends(get_db)):
    """Get all foods (legacy endpoint)"""
    try:
        food_data = db.query(custom_tables.Food).limit(1000).all()
        return food_data
    except Exception as ex:
        LOGGER.error(f"Getting Food Item Failed due to -{str(ex)}")
        return []


@router.post('/create', status_code=status.HTTP_201_CREATED)
def insert_food(request: food.FoodItemsBatch, db: Session = Depends(get_db)):
    """Batch insert foods"""
    try:
        data_to_insert = [item.model_dump() for item in request.food_items]

        df = pd.DataFrame(data_to_insert)

        df.to_sql(
            custom_tables.Food.__tablename__,
            con=db.bind,
            if_exists="append",
            index=False,
            method="multi",
            chunksize=2000,
            dtype={'nutrients': sqlalchemy.types.JSON}
        )

        db.commit()
        return {"message": f"Successfully inserted {len(data_to_insert)} foods"}
    except Exception as ex:
        LOGGER.error(f"Adding Food Item Failed due to -{str(ex)}")
        return {"error": str(ex)}


@router.get('/{name}', response_model=List[food.Food], status_code=status.HTTP_200_OK)
def search_food_name(name, db: Session = Depends(get_db)):
    """Search food by name"""
    try:
        data = db.query(custom_tables.Food).filter(
            custom_tables.Food.name.ilike(f"%{name}%")
        ).limit(100).all()
        return data
    except Exception as ex:
        LOGGER.error(f"Searching Food Item Failed due to -{str(ex)}")
        return []


@router.get('/category/{category}', response_model=List[food.Food], status_code=status.HTTP_200_OK)
def search_food_category(category, db: Session = Depends(get_db)):
    """Search food by category"""
    try:
        data = db.query(custom_tables.Food).filter(
            custom_tables.Food.category.ilike(f"%{category}%")
        ).limit(100).all()
        return data
    except Exception as ex:
        LOGGER.error(f"Searching Food Item Failed due to -{str(ex)}")
        return []
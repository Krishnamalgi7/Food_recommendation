from typing import List, Optional
from pydantic import BaseModel, Field


class Health(BaseModel):
    """Health condition schema for input"""
    name: str
    description: str
    carbohydrates_grm: float
    fats_grm: float
    fiber_grm: float
    protein_grm: float
    sodium_grm: float
    sugar_grm: float


class HealthConditionList(BaseModel):
    """List of health conditions for batch insert"""
    health_condition: List[Health]


class HealthConditionResponse(BaseModel):
    """Health condition response schema"""
    id: int
    name: str
    description: Optional[str]
    carbohydrates_grm: Optional[float]
    fats_grm: Optional[float]
    fiber_grm: Optional[float]
    protein_grm: Optional[float]
    sodium_grm: Optional[float]
    sugar_grm: Optional[float]

    class Config:
        from_attributes = True
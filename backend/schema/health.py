from typing import List, Optional
from pydantic import BaseModel, Field


class Health(BaseModel):
    """Health condition schema for input"""
    name: str
    description: str
    calcium_grm: float
    carbohydrates_grm: float
    fats_grm: float
    fiber_grm: float
    iron_grm: float
    magnesium_grm: float
    potassium_grm: float
    protein_grm: float
    sodium_grm: float
    vitamin_a_grm: float
    vitamin_b12_grm: float
    vitamin_c_grm: float


class HealthConditionList(BaseModel):
    """List of health conditions for batch insert"""
    health_condition: List[Health]


class HealthConditionResponse(BaseModel):
    """Health condition response schema"""
    id: int
    name: str
    description: Optional[str]
    calcium_grm: Optional[float]
    carbohydrates_grm: Optional[float]
    fats_grm: Optional[float]
    fiber_grm: Optional[float]
    iron_grm: Optional[float]
    magnesium_grm: Optional[float]
    potassium_grm: Optional[float]
    protein_grm: Optional[float]
    sodium_grm: Optional[float]
    vitamin_a_grm: Optional[float]
    vitamin_b12_grm: Optional[float]
    vitamin_c_grm: Optional[float]

    class Config:
        from_attributes = True
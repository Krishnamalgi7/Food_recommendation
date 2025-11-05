from typing import List, Dict, Optional
from pydantic import BaseModel, Field


class NutrientInfo(BaseModel):
    """Nutrient information - based on new dataset nutrients"""
    Calories: float
    Carbohydrates: float
    Fats: float
    Fiber: float
    Protein: float
    Sodium: float
    Saturated_Fat: float
    Cholesterol: float
    Sugar: float


class FoodRecommendation(BaseModel):
    """Single food recommendation"""
    food_id: int
    name: str
    category: str
    type: str
    price: float
    match_score: float = Field(..., description="Match score (0-1, higher is better)")
    distance: float = Field(..., description="Distance from ideal nutrients")
    nutrients: NutrientInfo

    class Config:
        from_attributes = True


class RecommendationRequest(BaseModel):
    """Request for food recommendations"""
    n_recommendations: int = Field(default=100, ge=1, le=500)
    category_filter: Optional[str] = None
    food_type: Optional[str] = Field(None, description="Filter by food type: Veg, Non-Veg, etc.")


class RecommendationResponse(BaseModel):
    """Response containing food recommendations"""
    user_id: int
    recommendations: List[FoodRecommendation]
    total_count: int
    nutrient_requirements: Dict[str, float]


class UserConditionRequest(BaseModel):
    """Request to add health condition to user"""
    condition_ids: List[int] = Field(..., description="List of health condition IDs")


class UserConditionResponse(BaseModel):
    """Response for user health conditions"""
    user_id: int
    conditions: List[str]
    message: str
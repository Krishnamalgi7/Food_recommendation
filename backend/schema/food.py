from typing import Dict,Any,List
from pydantic import BaseModel

class Food(BaseModel):
    name: str
    category: str
    type: str
    ingredients: str
    nutrients: Dict[str, Any]
    price: float
    class Config:
        from_attributes = True

class FoodItemsBatch(BaseModel):
    food_items: List[Food]
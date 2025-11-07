from pydantic import BaseModel
from typing import List, Dict

class RecipeIn(BaseModel):
    type: str
    name: str
    cuisine: str
    ingredients: List[str]
    instructions: List[str]
    calories: float
    macros: Dict[str, float]
    micros: Dict[str, float]
    user_info: Dict

class RecipeOut(RecipeIn):
    id: int
    rating: int

class RatingIn(BaseModel):
    rating: int

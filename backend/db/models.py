from typing import Optional
from sqlmodel import SQLModel, Field

class Recipe(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    type: str  # breakfast, lunch, etc.
    cuisine: str
    ingredients: str  # JSON serialized list
    instructions: str  # JSON serialized list
    calories: float
    macros: str  # JSON serialized dict
    micros: str  # JSON serialized dict
    user_info: str  # JSON serialized dict
    rating: Optional[int] = 0

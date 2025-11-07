from typing import Optional
from sqlmodel import SQLModel, Field

class Recipe(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    type: str  # breakfast, lunch,dinner 
    cuisine: str
    ingredients: str  # json serialized list
    instructions: str  
    calories: float
    macros: str  
    micros: str  # json serialized dict
    user_info: str  
    rating: Optional[int] = 0

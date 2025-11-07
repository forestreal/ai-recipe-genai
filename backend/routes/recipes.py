from fastapi import APIRouter, HTTPException, Request
from sqlmodel import select
from backend.db.models import Recipe
from backend.db.database import get_session

from backend.services.generator import call_genai_llm

from backend.schemas.recipe import RecipeIn, RatingIn

import json

router = APIRouter()

from fastapi import Request

@router.post("/generate")
async def generate_recipe(request: Request):  
    body = await request.json()
    user_profile = body.get("user_profile")

    prompt = (
        "You are a polymath nutritionist. Generate 5 detailed recipes for the following profile:\n"
        + json.dumps(user_profile)
    )

    recipes = await call_genai_llm(prompt)  
    return recipes


@router.post("/{recipe_id}/save")
def save_recipe(recipe_id: int, recipe: RecipeIn):
    with get_session() as session:
        new_recipe = Recipe(
            name=recipe.name,
            type=recipe.type,
            cuisine=recipe.cuisine,
            ingredients=json.dumps(recipe.ingredients),
            instructions=json.dumps(recipe.instructions),
            calories=recipe.calories,
            macros=json.dumps(recipe.macros),
            micros=json.dumps(recipe.micros),
            user_info=json.dumps(recipe.user_info)
        )
        session.add(new_recipe)
        session.commit()
        return {"id": new_recipe.id, "message": "Recipe saved"}

@router.get("/")
def get_all_recipes(skip: int = 0, limit: int = 10):
    with get_session() as session:
        statement = select(Recipe).offset(skip).limit(limit)
        results = session.exec(statement).all()
        return results

@router.get("/{recipe_id}")
def get_recipe(recipe_id: int):
    with get_session() as session:
        recipe = session.get(Recipe, recipe_id)
        if not recipe:
            raise HTTPException(status_code=404, detail="Recipe not found")
        return recipe

@router.delete("/{recipe_id}")
def delete_recipe(recipe_id: int):
    with get_session() as session:
        recipe = session.get(Recipe, recipe_id)
        if not recipe:
            raise HTTPException(status_code=404, detail="Recipe not found")
        session.delete(recipe)
        session.commit()
        return {"message": "Recipe deleted"}

@router.post("/{recipe_id}/rate")
def rate_recipe(recipe_id: int, rating: RatingIn):
    with get_session() as session:
        recipe = session.get(Recipe, recipe_id)
        if not recipe:
            raise HTTPException(status_code=404, detail="Recipe not found")
        recipe.rating = rating.rating
        session.add(recipe)
        session.commit()
        return {"message": "Rating updated"}

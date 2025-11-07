from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.routes.recipes import router as recipes_router
from backend.db.database import create_db_and_tables 

app = FastAPI(title="AI Recipe Generator API")


@app.on_event("startup")
def on_startup():
    create_db_and_tables()


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(recipes_router, prefix="/api/recipes")


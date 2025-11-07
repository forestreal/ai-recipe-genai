from sqlmodel import SQLModel, create_engine, Session

# Define DB path (SQLite for now, change to PostgreSQL/MySQL later if needed)
DATABASE_URL = "sqlite:///recipes.db"
engine = create_engine(DATABASE_URL, echo=False)

# Called once to create all necessary tables defined in SQLModel-based classes
def create_db_and_tables():
    from backend.db import models  # Import models before table creation
    SQLModel.metadata.create_all(engine)

# Returns a session instance you can use in route functions
def get_session():
    return Session(engine)

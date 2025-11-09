from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import String, Integer, JSON, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from typing import List
from datetime import datetime

class Base(DeclarativeBase): pass

class User(Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    password_hash: Mapped[str] = mapped_column(String(255))

    # relationships
    evaluations: Mapped[List["Evaluation"]] = relationship("Evaluation", back_populates="user", cascade="all, delete-orphan")
    flavors: Mapped[List["Flavor"]] = relationship("Flavor", back_populates="user", cascade="all, delete-orphan")
    analyses: Mapped[List["Analysis"]] = relationship("Analysis", back_populates="user", cascade="all, delete-orphan")
    recipe_runs: Mapped[List["RecipeRun"]] = relationship("RecipeRun", back_populates="user", cascade="all, delete-orphan")

class Evaluation(Base):
    __tablename__ = "evaluations"
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    snapshot: Mapped[dict] = mapped_column(JSON)
    locked: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow, index=True)

    user: Mapped["User"] = relationship("User", back_populates="evaluations")

class Flavor(Base):
    __tablename__ = "flavors"
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    template: Mapped[dict] = mapped_column(JSON)
    locked: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow, index=True)

    user: Mapped["User"] = relationship("User", back_populates="flavors")

class Analysis(Base):
    __tablename__ = "analyses"
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    content: Mapped[dict] = mapped_column(JSON)
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow, index=True)

    user: Mapped["User"] = relationship("User", back_populates="analyses")

class RecipeRun(Base):
    __tablename__ = "recipe_runs"
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    request_payload: Mapped[dict] = mapped_column(JSON)
    result: Mapped[dict] = mapped_column(JSON)
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow, index=True)

    user: Mapped["User"] = relationship("User", back_populates="recipe_runs")
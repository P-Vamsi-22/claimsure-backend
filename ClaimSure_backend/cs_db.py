from sqlmodel import SQLModel, create_engine, Session, Field, Relationship, Column
from .schemas import BaseUser, UserCreate, BaseAsset,CreateProfile
from fastapi import Depends
from typing import Annotated, Optional
from datetime import datetime, timezone, timedelta
from sqlalchemy import LargeBinary
import os


# Use PostgreSQL in production (Render), SQLite in development
database_url = os.getenv("DATABASE_URL")

if database_url:
    # Production: PostgreSQL on Render
    engine = create_engine(
        database_url,
        echo=False,
        future=True,
        pool_pre_ping=True,
    )
else:
    # Development: Local SQLite
    sql_file = "sc_database.db"
    sqlite_url = f"sqlite:///{sql_file}"
    engine = create_engine(sqlite_url, connect_args={"check_same_thread": False})


def create_db_tables():
    SQLModel.metadata.create_all(engine)


def get_session():
    with Session(engine) as session:
        yield session


sessionDep = Annotated[Session, Depends(get_session)]


class User(BaseUser, table=True):
    id: int = Field(primary_key=True, index=True, nullable=False)
    pwd: str = Field(nullable=False)
   
    # Corrected relationships with explicit foreign keys
    owned_assets: list["Asset"] = Relationship(
        back_populates="user",
        sa_relationship_kwargs={"foreign_keys": "Asset.user_id"}
    )
    nominee_assets: list["Asset"] = Relationship(
        back_populates="nominee",
        sa_relationship_kwargs={"foreign_keys": "Asset.nominee_id"}
    )
    profile: Optional["Profile"] = Relationship(back_populates="user")

class Profile(CreateProfile, table=True):
    id: int = Field(primary_key=True, index=True)
    user_id: int = Field(foreign_key="user.id", unique=True, nullable=False)
    # Relationship back to user
    user: Optional[User] = Relationship(back_populates="profile")



class Asset(BaseAsset, table=True):
    asset_id: Optional[int] = Field(default=None, primary_key=True, index=True)
    user_id: int = Field(foreign_key="user.id")
    nominee_id: Optional[int] = Field(default=None, foreign_key="user.id")
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


    # Relationships with explicit foreign keys
    user: User = Relationship(
        back_populates="owned_assets",
        sa_relationship_kwargs={"foreign_keys": "[Asset.user_id]"}
    )
    nominee: Optional[User] = Relationship(
        back_populates="nominee_assets",
        sa_relationship_kwargs={"foreign_keys": "[Asset.nominee_id]"}
    )

from fastapi import FastAPI
from pydantic import BaseModel
from sqlmodel import SQLModel,Field
from datetime import datetime
from typing import Optional

class BaseUser(SQLModel):
    username : str = Field(nullable=False,index=True)
    phone_no : int = Field(description="   phone no. without country code")

class UserCreate(BaseUser):
    pwd : str

class ShowUser(BaseUser):
    id : int



class BaseAsset(SQLModel):
    type: str
    title: str
    value: Optional[float] = None
    # document: Optional[bytes] = None
    description : Optional[str]  = None
    nominee_name : Optional[str] = None
    institution : str
    accountNumber : str


class CreateAsset(BaseAsset):
    pass

    



class ShowAsset(CreateAsset):
    type: str
    title: str
    value: Optional[float] = None
    # document: Optional[bytes] = None
    description : Optional[str]  = None
    # nominee_name : Optional[str] = None
    institution : str
    accountNumber : str
    # nominee_id : Optional[int] = None 
    # nominee_name : Optional[str]  = None
    created_at : datetime
    

class UpdateAsset(BaseAsset):
    nominee_id : Optional[int] = None
    

    
# class Nominee(SQLModel):
#     nominee_id: Optional[int] = Field(default=None, foreign_key="user.id")  # optional link to internal user
#     phone_number: Optional[str] = None
#     email: Optional[str] = None
#     # user_id : int

# class CreateNominee(Nominee):
#     pass

class CreateProfile(SQLModel):
    fullname: str
    age: int
    sex: str
    location: str
from fastapi import FastAPI,APIRouter,HTTPException,Depends
from ..schemas import UserCreate,ShowUser,BaseAsset,ShowAsset,CreateAsset
from ..cs_db import sessionDep,User,Asset

sessionDep = sessionDep
from sqlmodel import select,Session
from ..security import hash_pwd,get_user
from typing import Annotated


router = APIRouter()



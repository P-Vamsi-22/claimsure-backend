from fastapi.security import OAuth2PasswordBearer,OAuth2PasswordRequestForm
from fastapi import APIRouter,HTTPException,status,Depends
from passlib.context import CryptContext
import jwt
from .cs_db import sessionDep,User
from fastapi import APIRouter
from sqlmodel import select,Field
from typing import Annotated
from datetime import timedelta,timezone,datetime
from pydantic import BaseModel
from .cs_db import User
# from jwt.exceptions import InvalidTokenError

sessionDepp = sessionDep
class Token(BaseModel):
     access_token : str
     token_type : str

SECURITY_KEY = "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7"
ALGORITHM = "HS256"
TOKEN_EXPIRE_TIME = 30

o_schema = OAuth2PasswordBearer(tokenUrl="/token")

pwd_context = CryptContext(schemes=['bcrypt'])

def hash_pwd(pwd):
    return pwd_context.hash(pwd)

def verify_pwd(pwd,hpwd):
    return pwd_context.verify(pwd,hpwd)


def check_authentication(u_name,pwd,session:sessionDepp):
    user = session.exec(select(User).where(User.username == u_name)).first()
    if not user : 
        return False
    if not verify_pwd(pwd,user.pwd):
        return False
    return user
        
def get_user():
    pass

def access_token(data: dict, expire: timedelta):
    expire_time = datetime.now(timezone.utc) + expire
    to_encode = data.copy()
    to_encode.update({"exp": int(expire_time.timestamp())})  # Unix timestamp
    return jwt.encode(to_encode, key=SECURITY_KEY, algorithm=ALGORITHM)


def get_user(session:sessionDep,token : str= Depends(o_schema)):
    try :
        payload = jwt.decode(token,key=SECURITY_KEY,algorithms=[ALGORITHM])
        
    except Exception:
        raise HTTPException(status_code=401,detail="invalid token")
    
    username = payload.get("sub")
    user = session.exec(select(User).where(User.username == username)).first()


    if not username :
        raise HTTPException(status_code=401,detail='fuck wrong username--getuser')
    return user

router = APIRouter()

@router.post("/token")
def get_token(login : Annotated[OAuth2PasswordRequestForm,Depends()],session:sessionDepp):
    user = check_authentication(login.username,login.password,session=session)
    if not user : 
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="no user found/wrong credentials")
    
    access_time = timedelta(minutes=TOKEN_EXPIRE_TIME)
    access_token_ = access_token(data = {'sub':user.username},expire=access_time)
    return Token(access_token=access_token_,token_type="bearer")


from fastapi import FastAPI
from contextlib import asynccontextmanager
from .cs_db import create_db_tables
from .security import router
from .people import users
from fastapi.middleware.cors import CORSMiddleware


@asynccontextmanager
async def lifespan(app:FastAPI):
    create_db_tables()
    yield 
    print("server terminated")

app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(router)
app.include_router(users.router)



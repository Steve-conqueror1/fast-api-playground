from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware

from app import models
from app.database import engine
from app.routers import post, user, login, vote
from .config import Settings

# models.Base.metadata.create_all(bind=engine)
app = FastAPI()

origins = ["https://www.google.com"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(post.router)
app.include_router(user.router)
app.include_router(login.router)
app.include_router(vote.router)


@app.get("/")
def root():
    return {"message": "Welcom to sdfsdfdsfastapi"}

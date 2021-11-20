from fastapi import Depends, APIRouter, HTTPException
from sqlalchemy.orm import Session
from starlette import status

from app import models, utils
from app.database import get_db
from app.models import User
from app.schemas import UserResponse, UserCreate

router = APIRouter(prefix="/users", tags=["Users"])


@router.get("/", status_code=status.HTTP_201_CREATED)
def get_users(db: Session = Depends(get_db)):
    user = db.query(models.User).all()
    return user


@router.get("/{id}", response_model=UserResponse)
def get_user(
    id: int,
    db: Session = Depends(get_db),
):
    user = db.query(User).filter(User.id == id).first()
    if User is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with id:  {id} does not exist",
        )
    return user


@router.post("/", status_code=status.HTTP_201_CREATED, response_model=UserResponse)
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    # Hash password
    hashed_password = utils.hash("aaaaaa" + user.password)
    user.password = hashed_password
    new_user = models.User(**user.dict())
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

from fastapi import APIRouter, HTTPException, status, Response, Depends
from fastapi.security.oauth2 import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app import utils, oauth2
from app.database import get_db
from app.models import User
from app.schemas import UserLogin, Token

router = APIRouter(tags=["Authentication"])


@router.post("/login", response_model=Token)
def login(
    user_login: OAuth2PasswordRequestForm = Depends(),
    session: Session = Depends(get_db),
):
    user = session.query(User).filter(User.email == user_login.username).first()
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Wrong Password or Email"
        )
    is_correct_password = utils.verify(user_login.password, user.password)
    if not is_correct_password:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Wrong Password or Email"
        )

    access_token = oauth2.create_access_token(data={"user_id": user.id})

    #     create a token
    return {"access_token": access_token, "token_type": "bearer"}

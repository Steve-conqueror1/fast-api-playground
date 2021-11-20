from fastapi import FastAPI, APIRouter, Response, status, HTTPException, Depends
from sqlalchemy.orm import Session

from app import oauth2, schemas
from app.database import get_db
from app.models import Vote, Post

router = APIRouter(prefix="/vote", tags=["Post"])


@router.post("/", status_code=status.HTTP_201_CREATED)
def create_vote(
    vote: schemas.Vote,
    session: Session = Depends(get_db),
    current_user: int = Depends(oauth2.get_current_user),
):

    found_post = session.query(Post).filter(Post.id == vote.post_id).first()
    if found_post is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Vote doesnt exist"
        )

    vote_query = session.query(Vote).filter(
        Vote.post_id == vote.post_id, Vote.user_id == current_user.id
    )
    found_vote = vote_query.first()

    if vote.dir == 1:
        if found_vote:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"user {current_user.id} has already voted",
            )
        new_vote = Vote(post_id=vote.post_id, user_id=current_user.id)
        session.add(new_vote)
        session.commit()
        return {"message": "voting successiful"}
    else:
        if not found_vote:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Vote doesnt exist"
            )
        vote_query.delete(synchronize_session=False)
        session.commit()
    return {"message": "successiful deleted vote"}

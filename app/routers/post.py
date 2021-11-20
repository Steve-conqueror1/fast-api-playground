from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import func
from sqlalchemy.orm import Session
from starlette import status

from app import models, oauth2
from app.database import get_db
from app.schemas import Post, PostCreate, PostOut

router = APIRouter(prefix="/posts", tags=["Posts"])


# @router.get("/", response_model=List[Post])
@router.get("/", response_model=List[PostOut])
def get_posts(
    session: Session = Depends(get_db),
    current_user: int = Depends(oauth2.get_current_user),
    limit: int = 10,
    skip=0,
    search="",
):
    # cursor.execute("""SELECT * FROM posts""")
    # posts = cursor.fetchall()
    posts = (
        session.query(models.Post)
        .filter(models.Post.title.contains(search))
        .limit(limit)
        .offset(skip)
        .all()
    )

    # with joins
    results = (
        session.query(models.Post, func.count(models.Vote.post_id).label("votes"))
        .join(models.Vote, models.Vote.post_id == models.Post.id, isouter=True)
        .group_by(models.Post.id)
        .filter(models.Post.title.contains(search))
        .limit(limit)
        .offset(skip)
        .all()
    )

    return results


@router.post("/", status_code=status.HTTP_201_CREATED, response_model=Post)
def create_post(
    post: PostCreate,
    db: Session = Depends(get_db),
    current_user: int = Depends(oauth2.get_current_user),
):
    # cursor.execute("""INSERT INTO posts(title, content, published) VALUES (%s, %s, %s) RETURNING *""",
    #                (post.title, post.content, post.published))
    # new_post = cursor.fetchone()
    # conn.commit()
    post = models.Post(**post.dict(), user_id=current_user.id)
    db.add(post)
    db.commit()
    db.refresh(post)
    return post


@router.get("/{id}", response_model=PostOut)
def get_post(
    id: int,
    db: Session = Depends(get_db),
    current_user: int = Depends(oauth2.get_current_user),
):
    # cursor.execute(""" SELECT * FROM posts WHERE id = %s """, (str(id),))
    # post = cursor.fetchone()
    post = (
        db.query(models.Post, func.count(models.Vote.post_id).label("votes"))
        .join(models.Vote, models.Vote.post_id == models.Post.id, isouter=True)
        .filter(models.Post.id == id)
        .group_by(models.Post.id)
        .first()
    )
    if post is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"post with id: {id} was not found",
        )
    print(post)
    return post


@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_post(
    id: int,
    db: Session = Depends(get_db),
    current_user: int = Depends(oauth2.get_current_user),
):
    # cursor.execute(""" DELETE FROM posts WHERE id = %s returning *""", (str(id),))
    # deleted_post = cursor.fetchone()
    # conn.commit()
    post = db.query(models.Post).filter(models.Post.id == id).first()
    if post is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Post with id: {id} was not found",
        )

    if post.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not Authorized to perform requested action",
        )

    db.delete(post)
    db.commit()
    return {"mesasge": "Post successifully deleted"}


@router.put("/{id}", response_model=Post)
def update_post(
    id: int,
    updated_post: PostCreate,
    db: Session = Depends(get_db),
    current_user: int = Depends(oauth2.get_current_user),
):
    # cursor.execute("""UPDATE posts set title=%s, content=%s, published=%s WHERE id = %s returning *""",
    #                (post.title, post.content, post.published, id))
    # post = cursor.fetchone()
    # conn.commit()
    query = db.query(models.Post).filter(models.Post.id == id)
    post = query.first()
    if post is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Post with id: {id} not found ",
        )

    if post.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not Authorized to perform requested action",
        )

    query.update(updated_post.dict(), synchronize_session=False)
    db.commit()

    return query.first()

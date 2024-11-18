from typing import Optional, List
from starlette.status import HTTP_401_UNAUTHORIZED, HTTP_200_OK
from .. import models, schemas, oauth2
from fastapi import Response, status, HTTPException, Depends, APIRouter
from ..database import get_db
from sqlalchemy.orm import Session
from ..models import Posts
from sqlalchemy import func


router = APIRouter(
    prefix="/posts",
    tags=['Posts']
)


# @router.get("/", response_model=List[schemas.Post])
@router.get("/")
def get_posts(db: Session = Depends(get_db), current_user: int = Depends(oauth2.get_current_user),
              limit: int = 10, skip: int = 0, search: Optional[str] = ""):
    # cursor.execute("""SELECT * FROM posts""")
    # posts = cursor.fetchall()

    # posts = db.query(models.Posts).filter(models.Posts.title.contains(search)).limit(limit).offset(skip).all()

    results = db.query(models.Posts, func.count(models.Vote.post_id).label("votes")).join(models.Vote,
            models.Vote.post_id == models.Posts.id, isouter=True).group_by(models.Posts.id)

    new_results = db.execute(results).mappings().all()

    return new_results


@router.post("/", status_code=status.HTTP_201_CREATED, response_model=schemas.PostResponse)
def create_post(post: schemas.PostCreate, db: Session = Depends(get_db),
                current_user: int = Depends(oauth2.get_current_user)):
    # cursor.execute("""INSERT INTO posts (title, content, published)
    # VALUES (%s, %s, %s) RETURNING *""", (post.title, post.content, post.published))
    # new_post = cursor.fetchone()
    # conn.commit()
    new_post = models.Posts(owner_id=current_user.id, **post.model_dump())
    db.add(new_post)
    db.commit()
    db.refresh(new_post)
    return new_post


@router.get("/{id}", response_model=schemas.Post)  # Ensure the response model is correct
def get_post(id: int, db: Session = Depends(get_db), current_user: int = Depends(oauth2.get_current_user)):
    # Query for the specific post by id
    post = db.query(models.Posts).filter(models.Posts.id == id).first()

    # Check if the post exists
    if post is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Post with id: {id} was not found.")

    # Check if the post belongs to the current user
    # if post.owner_id != current_user.id:
    #    raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
    #                        detail="Not authorized to perform this action")

    return post


@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_post(id: int, db: Session = Depends(get_db),
                current_user: int = Depends(oauth2.get_current_user)):
    # cursor.execute("""DELETE FROM posts WHERE id = %s RETURNING *""",
    #               (str(id),))
    # deleted_post = cursor.fetchone()
    # conn.commit()
    deleted_post = db.query(Posts).filter(Posts.id == id).first()

    if deleted_post is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"post with id: {id} does not exist")
    if deleted_post.owner_id != current_user.id:
        raise HTTPException(status_code=HTTP_401_UNAUTHORIZED,
                            detail="Not authorized to perform this action")

    db.delete(deleted_post)
    db.commit()

    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.put("/{id}", response_model=schemas.PostResponse)
def update_post(id: int, post_data: schemas.PostCreate, db: Session = Depends(get_db),
                current_user: int = Depends(oauth2.get_current_user)):
    # Query for the post to update
    post_query = db.query(Posts).filter(Posts.id == id).first()

    # Check if the post exists
    if post_query is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Post with id: {id} does not exist"
        )
    if post_query.owner_id != current_user.id:
        raise HTTPException(status_code=HTTP_401_UNAUTHORIZED,
                            detail="Not authorized to perform this action")

    # Update the fields
    post_query.title = post_data.title
    post_query.content = post_data.content
    post_query.published = post_data.published

    # Commit the changes
    db.commit()

    # Return the updated post as a dictionary
    return post_query

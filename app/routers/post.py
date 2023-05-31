from sqlalchemy import func
import models, oauth2
from database import get_db
from typing import List, Optional
import schemas as sc
from fastapi import Response, status, HTTPException, Depends, APIRouter
from  sqlalchemy.orm import Session

router = APIRouter(
    prefix="/posts",
    tags=["Posts"]
)

@router.get("/", response_model=List[sc.PostOut])
def get_posts(db: Session=Depends(get_db), current_user: int = Depends(oauth2.get_current_user), limit: int =10, skip:int =0, search: Optional[str]=""):
    posts = db.query(models.Post, func.count(models.Like.post_id).label("likes")).join(models.Like, models.Post.id==models.Like.post_id, isouter=True).group_by(models.Post.id).all()
    return posts

@router.post("/", response_model=sc.Post)
def create_post(post: sc.PostCreate, db: Session=Depends(get_db), current_user: int = Depends(oauth2.get_current_user)):
    new_post = models.Post(owner_id= current_user.id, **post.dict())
    db.add(new_post)
    db.commit()
    db.refresh(new_post)
    return new_post

@router.get("/{id}", response_model=sc.PostOut)
def get_post(id:int, response:Response, db: Session=Depends(get_db), current_user: int = Depends(oauth2.get_current_user)):

    post = db.query(models.Post, func.count(models.Like.post_id).label("likes")).join(models.Like, models.Post.id==models.Like.post_id, isouter=True).group_by(models.Post.id).filter(models.Post.id == id).first()
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"post with id: {id} not found")
    return post

@router.delete("/{id}",status_code=status.HTTP_204_NO_CONTENT)
def delete_post(id:int, response:Response, db: Session=Depends(get_db), current_user: int = Depends(oauth2.get_current_user)):
    post_query = db.query(models.Post).filter(models.Post.id == id)
    post =post_query.first()
    if post==None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"post with id: {id} not found")
    if post.owner_id!= current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to perform requested action")
    post_query.delete(synchronize_session=False)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)

@router.put("/{id}", response_model=sc.Post)
def update_post(id:int, post: sc.PostCreate, response:Response, db: Session=Depends(get_db), current_user: int = Depends(oauth2.get_current_user)):
    post_query= db.query(models.Post).filter(models.Post.id == id)
    post =post_query.first()
    if post==None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"post with id: {id} not found")
    if post.owner_id!= current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to perform requested action")
    post_query.update(post.dict(),synchronize_session=False)
    db.commit()
    return post
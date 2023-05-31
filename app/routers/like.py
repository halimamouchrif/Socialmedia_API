import models,utils, oauth2
from database import get_db
from typing import List, Optional
import schemas as sc
from fastapi import FastAPI, Response, status, HTTPException, Depends, APIRouter
from  sqlalchemy.orm import Session

router = APIRouter(
    prefix="/likes",
    tags = ["Likes system"]
)
@router.post("/", status_code=status.HTTP_201_CREATED)
def like_post(like: sc.Likes, db: Session=Depends(get_db), user: Session=Depends(oauth2.get_current_user)):
    
    found_post= db.query(models.Post).filter(models.Post.id==like.post_id).first()
    if not found_post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"post with id ={like.post_id} not found")
    
    like_found=db.query(models.Like).filter(models.Like.post_id==like.post_id, models.Like.user_id==user.id)
    if like_found.first():
        if(like.dir==1):
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=f"Post with id={like.post_id} already liked")
        
        like_found.delete(synchronize_session=False)
        db.commit()
        return {"message": "Successfully deleted your like"}
    else:
        if(like.dir==0):
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=f"Post with id={like.post_id} isn't liked")
            
        new_like = models.Like(user_id=user.id, post_id=like.post_id)
        db.add(new_like)
        db.commit()
        db.refresh(new_like)
        return {"message": "Successfully added your like"}
            

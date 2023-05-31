from fastapi import FastAPI, Response, status, HTTPException, Depends, APIRouter
import database as db
import schemas as sc
import models,utils, oauth2
from  sqlalchemy.orm import Session
from fastapi.security.oauth2 import OAuth2PasswordRequestForm



router =APIRouter(
    tags= ['Authentication']
)
@router.post('/login', response_model=sc.Token)
def login(user_cred: OAuth2PasswordRequestForm= Depends(), db :Session =Depends(db.get_db)):
    user= db.query(models.User).filter(models.User.email == user_cred.username).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=f"Invalid Credentials")
    
    if not utils.verify(user_cred.password,user.password):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=f"Invalid Credentials")
    #create token
    access_token = oauth2.create_access_token(data ={"user_id": user.id})
    #return token
    return {"access_token": access_token, "token_type": "bearer"}
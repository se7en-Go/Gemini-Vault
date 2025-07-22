from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app import models, schemas, crud
from app.database.session import get_db
from app.service.security import get_current_user

api_keys_router = APIRouter()

@api_keys_router.post("/", response_model=schemas.ApiKey, tags=["API Keys"])
def create_api_key_for_user(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """
    Generate a new API key for the current logged-in user.
    """
    # Optional: Add logic here to limit the number of keys per user
    api_key = crud.api_key.create_api_key(db=db, user=current_user)
    return api_key

@api_keys_router.get("/", response_model=List[schemas.ApiKey], tags=["API Keys"])
def get_api_keys_for_user(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """
    Get all API keys for the current logged-in user.
    """
    return crud.api_key.get_user_api_keys(db=db, user_id=current_user.id)

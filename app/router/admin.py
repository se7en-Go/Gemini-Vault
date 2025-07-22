from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app import models, schemas, crud
from app.database.session import get_db
from app.service.security import get_current_admin_user
from pydantic import BaseModel

admin_router = APIRouter()

class AddBalanceRequest(BaseModel):
    amount: int # Amount to add in cents

@admin_router.get("/users", response_model=List[schemas.User], tags=["Admin"])
def read_users(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    admin_user: models.User = Depends(get_current_admin_user)
):
    """
    Retrieve all users. Admin access required.
    """
    users = crud.user.get_users(db, skip=skip, limit=limit)
    return users

@admin_router.post("/users/{user_id}/add-balance", response_model=schemas.ApiKey, tags=["Admin"])
def add_balance_to_user_key(
    user_id: int,
    request: AddBalanceRequest,
    db: Session = Depends(get_db),
    admin_user: models.User = Depends(get_current_admin_user)
):
    """
    Add balance to a user's first API key. Admin access required.
    """
    user_keys = crud.api_key.get_user_api_keys(db, user_id=user_id)
    if not user_keys:
        raise HTTPException(status_code=404, detail="User has no API keys")
    
    # For simplicity, add to the first key
    key_to_update = user_keys[0]
    key_to_update.balance += request.amount
    db.add(key_to_update)
    db.commit()
    db.refresh(key_to_update)
    return key_to_update

@admin_router.put("/users/{user_id}/toggle-active", response_model=schemas.User, tags=["Admin"])
def toggle_user_active_status(
    user_id: int,
    db: Session = Depends(get_db),
    admin_user: models.User = Depends(get_current_admin_user)
):
    """
    Toggle the is_active status of a user. Admin access required.
    """
    db_user = crud.user.get_user(db, user_id=user_id)
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    
    db_user.is_active = not db_user.is_active
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

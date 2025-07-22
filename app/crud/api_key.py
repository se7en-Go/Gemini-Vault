from sqlalchemy.orm import Session
from typing import List, Optional
from app.models.api_key import UserApiKey
from app.models.user import User

def create_api_key(db: Session, user: User) -> UserApiKey:
    """
    Creates a new API key for a given user.
    """
    db_api_key = UserApiKey(user_id=user.id)
    db.add(db_api_key)
    db.commit()
    db.refresh(db_api_key)
    return db_api_key

def get_api_key(db: Session, key: str) -> Optional[UserApiKey]:
    """
    Retrieves an API key object by its key string.
    """
    return db.query(UserApiKey).filter(UserApiKey.key == key).first()

def get_user_api_keys(db: Session, user_id: int) -> List[UserApiKey]:
    """
    Retrieves all API keys for a given user.
    """
    return db.query(UserApiKey).filter(UserApiKey.user_id == user_id).all()

def revoke_api_key(db: Session, api_key: UserApiKey) -> UserApiKey:
    """
    Deactivates an API key.
    """
    api_key.is_active = False
    db.commit()
    db.refresh(api_key)
    return api_key

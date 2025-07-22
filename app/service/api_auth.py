from fastapi import Security, HTTPException, status
from fastapi.security import APIKeyHeader
from sqlalchemy.orm import Session
from app import crud, models
from app.database.session import get_db
from fastapi import Depends

API_KEY_HEADER = APIKeyHeader(name="Authorization", auto_error=False)

async def get_api_key(
    api_key_header: str = Security(API_KEY_HEADER),
    db: Session = Depends(get_db)
) -> models.UserApiKey:
    """
    Dependency to authenticate and retrieve a user API key.
    The key should be provided in the 'Authorization' header.
    e.g., "Authorization: sk-xxxxxxxxxxxxxxxx"
    """
    if not api_key_header:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authorization header is missing",
        )

    db_api_key = crud.api_key.get_api_key(db, key=api_key_header)

    if not db_api_key or not db_api_key.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid or inactive API Key",
        )
    
    return db_api_key

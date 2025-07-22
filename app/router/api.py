from fastapi import APIRouter, Request, HTTPException, Depends
from sqlalchemy.orm import Session
from app.service.proxy import process_request
from app.service.api_auth import get_api_key
from app.models.api_key import UserApiKey
from app.database.session import get_db
import logging

logger = logging.getLogger(__name__)
api_router = APIRouter()

@api_router.post("/chat/completions", tags=["API"])
async def chat_completions(
    request: Request,
    db: Session = Depends(get_db),
    api_key: UserApiKey = Depends(get_api_key)
):
    """
    Proxy endpoint for Gemini chat completions.
    This endpoint requires a valid User API Key in the 'Authorization' header.
    """
    # Check if user has enough balance
    # For now, we'll use a simple "cost" of 1 unit per request.
    # This can be made more complex later.
    if api_key.balance <= 0:
        raise HTTPException(
            status_code=status.HTTP_402_PAYMENT_REQUIRED,
            detail="Insufficient balance. Please top up your account.",
        )

    try:
        # Pass the database session and the validated api_key object to the processing function
        response_data = await process_request(request, db, api_key)
        return response_data
    except Exception as e:
        logger.error(f"An error occurred in chat_completions for key ID {api_key.id}: {e}")
        raise HTTPException(status_code=500, detail="An internal error occurred.")

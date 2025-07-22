import httpx
import asyncio
import logging
import time
from fastapi import Request, HTTPException
from sqlalchemy.orm import Session
from app.core.config import settings
from app.models.api_key import UserApiKey
from typing import Dict, Any, List

logger = logging.getLogger(__name__)

class ApiKey:
    """Represents an API key with its state."""
    def __init__(self, key: str):
        self.key = key
        self.is_active = True
        self.failure_count = 0
        self.disabled_at = 0

    def fail(self):
        """Marks the key as failed, disabling it if the threshold is met."""
        self.failure_count += 1
        if self.failure_count >= settings.MAX_FAILURES:
            self.is_active = False
            self.disabled_at = time.time()
            logger.warning(f"Key ...{self.key[-4:]} has been disabled due to excessive failures.")

    def revive(self):
        """Re-enables the key and resets its failure count."""
        self.is_active = True
        self.failure_count = 0
        self.disabled_at = 0
        logger.info(f"Key ...{self.key[-4:]} has been re-enabled.")

class KeyManager:
    """Manages the pool of API keys, including rotation and health."""
    def __init__(self, keys: List[str]):
        self.keys = [ApiKey(key) for key in keys if key]
        self.current_index = 0

    def get_next_key(self) -> ApiKey:
        """
        Gets the next available and active API key.
        Also checks if any disabled keys can be revived.
        """
        if not self.keys:
            return None

        for _ in range(len(self.keys)):
            key_obj = self.keys[self.current_index]
            self.current_index = (self.current_index + 1) % len(self.keys)

            if not key_obj.is_active:
                # Check if the key can be revived
                if time.time() - key_obj.disabled_at > settings.CHECK_INTERVAL_SECONDS:
                    key_obj.revive()
                else:
                    # Skip this disabled key
                    continue
            
            return key_obj
        
        # If we loop through all keys and none are active
        return None

# Initialize the key manager as a singleton
keys_list = [key.strip() for key in settings.GEMINI_API_KEYS.split(',') if key.strip()]
key_manager = KeyManager(keys_list)

def _update_usage_and_balance(db: Session, api_key: UserApiKey, cost: int = 1):
    """Increments usage count and decrements balance for a given API key."""
    api_key.usage_count += 1
    api_key.balance -= cost
    db.add(api_key)
    db.commit()
    db.refresh(api_key)

def _transform_openai_to_gemini(request_body: Dict[str, Any]) -> Dict[str, Any]:
    """Converts an OpenAI-like request body to a Gemini-compatible one."""
    contents = []
    for msg in request_body.get("messages", []):
        role = "user" if msg.get("role") == "user" else "model"
        contents.append({"role": role, "parts": [{"text": msg.get("content", "")}]})
    return {"contents": contents}

def _transform_gemini_to_openai(gemini_data: Dict[str, Any], model: str, request_id: str) -> Dict[str, Any]:
    """Converts a Gemini response to an OpenAI-like one."""
    text_content = ""
    if gemini_data.get("candidates"):
        first_candidate = gemini_data["candidates"][0]
        if first_candidate.get("content", {}).get("parts"):
            text_content = first_candidate["content"]["parts"][0].get("text", "")

    choice = {
        "index": 0,
        "message": {"role": "assistant", "content": text_content},
        "finish_reason": "stop",
    }
    
    return {
        "id": f"chatcmpl-{request_id}",
        "object": "chat.completion",
        "created": int(time.time()),
        "model": model,
        "choices": [choice],
        "usage": {"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0}, # Placeholder
    }

async def process_request(request: Request, db: Session, api_key: UserApiKey) -> Dict[str, Any]:
    """
    Processes the incoming request, forwards it to Gemini, and handles retries with a robust key management system.
    """
    request_body = await request.json()
    model = request_body.get("model", "gemini-1.5-flash-latest")
    gemini_url = f"{settings.GEMINI_BASE_URL}/models/{model}:generateContent"
    gemini_payload = _transform_openai_to_gemini(request_body)

    for attempt in range(settings.MAX_RETRIES):
        api_key_obj = key_manager.get_next_key()
        if not api_key_obj:
            logger.error("No active API keys available.")
            raise HTTPException(status_code=503, detail="All API keys are currently disabled or unavailable.")

        params = {"key": api_key_obj.key}
        headers = {"Content-Type": "application/json"}

        try:
            async with httpx.AsyncClient() as client:
                logger.info(f"Attempt {attempt + 1}: Forwarding request with key ...{api_key_obj.key[-4:]}")
                response = await client.post(gemini_url, headers=headers, params=params, json=gemini_payload, timeout=60.0)
                
                if response.status_code >= 400:
                    # Treat any 4xx or 5xx as a failure for this key
                    raise httpx.HTTPStatusError(f"Request failed with status {response.status_code}", request=response.request, response=response)

                response.raise_for_status()
                
                gemini_data = response.json()
                request_id = response.headers.get("request-id", "unknown")
                
                # Update usage and balance on successful request
                _update_usage_and_balance(db, api_key)
                
                return _transform_gemini_to_openai(gemini_data, model, request_id)

        except httpx.HTTPStatusError as e:
            logger.warning(f"Attempt {attempt + 1} failed for key ...{api_key_obj.key[-4:]}. Status: {e.response.status_code}. Response: {e.response.text}")
            api_key_obj.fail() # Mark the key as failed
            # Continue to the next retry attempt with a new key
        except Exception as e:
            logger.error(f"An unexpected error occurred on attempt {attempt + 1} with key ...{api_key_obj.key[-4:]}: {e}")
            api_key_obj.fail() # Also mark as failed on unexpected errors
            await asyncio.sleep(1)

    raise HTTPException(status_code=503, detail="Service unavailable after multiple retries with different keys.")

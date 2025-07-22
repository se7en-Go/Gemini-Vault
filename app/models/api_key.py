import uuid
from sqlalchemy import Column, Integer, String, Boolean, DateTime, func, ForeignKey
from sqlalchemy.orm import relationship
from .user import Base

def generate_api_key():
    """Generates a unique, secure API key."""
    return f"sk-{uuid.uuid4().hex}"

class UserApiKey(Base):
    __tablename__ = "user_api_keys"

    id = Column(Integer, primary_key=True, index=True)
    key = Column(String, unique=True, index=True, nullable=False, default=generate_api_key)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    usage_count = Column(Integer, default=0)
    balance = Column(Integer, default=0) # Store balance in cents to avoid floating point issues

    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=func.now())
    
    user = relationship("User")

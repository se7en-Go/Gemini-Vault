from pydantic import BaseModel, EmailStr
import datetime

# Schema for creating a new user (request)
class UserCreate(BaseModel):
    email: EmailStr
    username: str
    password: str

# Schema for reading user data (response)
class User(BaseModel):
    id: int
    email: EmailStr
    username: str
    is_active: bool
    is_admin: bool
    created_at: datetime.datetime

    class Config:
        from_attributes = True # orm_mode = True for pydantic v1

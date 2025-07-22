from pydantic import BaseModel
import datetime

class ApiKey(BaseModel):
    key: str
    usage_count: int
    balance: int
    is_active: bool
    created_at: datetime.datetime

    class Config:
        from_attributes = True

from pydantic_settings import BaseSettings
from typing import List, Union

class Settings(BaseSettings):
    # A comma-separated string of Gemini API Keys will be automatically converted to a list of strings
    GEMINI_API_KEYS: List[str] = []

    # Gemini API Base URL
    GEMINI_BASE_URL: str = "https://generativelanguage.googleapis.com/v1beta"

    # Maximum number of retries for a failed API request
    MAX_RETRIES: int = 3

    # Log level
    LOG_LEVEL: str = "INFO"

    # Maximum failures allowed per key before it's temporarily disabled
    MAX_FAILURES: int = 3
    
    # Time in seconds to wait before re-enabling a disabled key
    CHECK_INTERVAL_SECONDS: int = 3600 # 1 hour

    # Database URL
    DATABASE_URL: str = "sqlite:///./data/gemini-vault.db"

    # JWT settings
    SECRET_KEY: str = "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    ALGORITHM: str = "HS256"

    class Config:
        env_file = ".env"
        env_file_encoding = 'utf-8'

settings = Settings()

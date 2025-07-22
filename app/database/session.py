from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.core.config import settings
import os

# For SQLite, we need to ensure the data directory exists
if settings.DATABASE_URL.startswith("sqlite"):
    db_path = os.path.dirname(settings.DATABASE_URL.replace("sqlite:///", ""))
    os.makedirs(db_path, exist_ok=True)

engine = create_engine(
    settings.DATABASE_URL,
    # connect_args is needed only for SQLite
    connect_args={"check_same_thread": False} if settings.DATABASE_URL.startswith("sqlite") else {}
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    """
    Dependency to get a database session.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

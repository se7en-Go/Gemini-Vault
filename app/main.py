from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from app.router.api import api_router
from app.router.auth import auth_router
from app.router.api_keys import api_keys_router
from app.router.admin import admin_router
from app.router.frontend import frontend_router
import logging
from app.core.config import settings
from app.database.session import engine
from app.models import Base

# Create database tables on startup
Base.metadata.create_all(bind=engine)

# Configure logging
logging.basicConfig(level=settings.LOG_LEVEL)

app = FastAPI(
    title="Gemini-Vault",
    description="A commercial-ready proxy and load balancer for Google Gemini API.",
    version="0.1.0"
)

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Include API routers
app.include_router(api_router, prefix="/v1")
app.include_router(auth_router, prefix="/auth")
app.include_router(api_keys_router, prefix="/api-keys")
app.include_router(admin_router, prefix="/admin")

app.include_router(frontend_router)

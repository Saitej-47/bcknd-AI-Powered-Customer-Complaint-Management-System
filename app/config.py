"""
Configuration settings
backend/app/config.py
"""

import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # API Settings
    API_TITLE: str = "Complaint Management System API"
    API_VERSION: str = "1.0.0"
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")
    
    # Database
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL", 
        "sqlite:///./complaint.db"
    )
    
    # Groq LLM Settings
    GROQ_API_KEY: str = os.getenv("GROQ_API_KEY", "")
    GROQ_MODEL: str = os.getenv("GROQ_MODEL", "gemma2-9b-it")
    
    # CORS - Include Production Vercel URL
    ALLOWED_ORIGINS: list = [
        "https://frontend-ai-powered-customer-complaint-management-m98jnqmf1.vercel.app",
        "https://frontend-ai-powered-customer-compla.vercel.app",
        "http://localhost:3000",
        "http://localhost:8000",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:8000",
    ]
    
    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()
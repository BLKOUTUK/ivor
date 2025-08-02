"""
Application Configuration
Centralized settings and environment variables
"""

import os
from typing import Optional
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

load_dotenv()

class Settings(BaseSettings):
    """Application settings with environment variable support"""
    
    # Application
    app_name: str = "IVOR Community AI"
    app_version: str = "2.0.0"
    environment: str = os.getenv("ENVIRONMENT", "production")
    debug: bool = os.getenv("DEBUG", "false").lower() == "true"
    
    # Database
    database_url: str = os.getenv("DATABASE_URL", "sqlite:///blkout_community.db")
    
    # API Keys
    groq_api_key: Optional[str] = os.getenv("GROQ_API_KEY")
    huggingface_api_key: Optional[str] = os.getenv("HUGGINGFACE_API_KEY")
    openai_api_key: Optional[str] = os.getenv("OPENAI_API_KEY")
    
    # AI Service Configuration
    ai_api_base: str = "https://api.groq.com/openai/v1"
    default_model: str = "llama3-8b-8192"
    max_tokens: int = 2000
    temperature: float = 0.7
    
    # Server Configuration
    host: str = os.getenv("HOST", "localhost")
    port: int = int(os.getenv("PORT", "8000"))
    reload: bool = os.getenv("RELOAD", "false").lower() == "true"
    
    # CORS Settings
    cors_origins: list = [
        "http://localhost:3000",
        "http://localhost:8000", 
        "http://127.0.0.1:3000",
        "http://127.0.0.1:8000"
    ]
    
    # Security
    secret_key: str = os.getenv("SECRET_KEY", "dev-secret-key-change-in-production")
    access_token_expire_minutes: int = 30
    
    # Community Features
    max_story_length: int = 10000
    max_comment_length: int = 1000
    stories_per_page: int = 20
    comments_per_page: int = 50
    
    # Rate Limiting
    rate_limit_per_minute: int = 60
    chat_rate_limit_per_minute: int = 10
    
    # Logging
    log_level: str = os.getenv("LOG_LEVEL", "INFO")
    log_file: Optional[str] = os.getenv("LOG_FILE")
    
    class Config:
        env_file = ".env"
        case_sensitive = False

# Global settings instance
settings = Settings()

# Convenience functions
def get_database_url() -> str:
    """Get database URL with fallback"""
    return settings.database_url

def is_production() -> bool:
    """Check if running in production"""
    return settings.environment.lower() == "production"

def get_cors_origins() -> list:
    """Get CORS origins with environment-specific additions"""
    origins = settings.cors_origins.copy()
    
    if not is_production():
        # Add development origins
        origins.extend([
            "http://localhost:3001",
            "http://localhost:8001"
        ])
    
    return origins
"""
Configuration settings for IVOR Backend
"""

import os
from typing import List
from pydantic import BaseSettings

class Settings(BaseSettings):
    """Application settings"""
    
    # API Configuration
    DEBUG: bool = os.getenv("DEBUG", "False").lower() == "true"
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    CORS_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://localhost:3003",
        "https://blkoutuk.com"
    ]
    
    # AI API Configuration (No Cost Primary)
    HUGGINGFACE_API_TOKEN: str = os.getenv("HUGGINGFACE_API_TOKEN", "")
    GROQ_API_KEY: str = os.getenv("GROQ_API_KEY", "")
    
    # Fallback AI APIs (Optional)
    DEEPSEEK_API_KEY: str = os.getenv("DEEPSEEK_API_KEY", "")
    QWEN_API_KEY: str = os.getenv("QWEN_API_KEY", "")
    
    # Embeddings API
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    
    # Model Configuration
    MIXTRAL_MODEL: str = "mistralai/Mixtral-8x7B-Instruct-v0.1"
    GROQ_MODEL: str = "llama-3.3-70b-versatile"
    
    # Database Configuration
    DATABASE_URL: str = os.getenv("DATABASE_URL", "postgresql://user:password@localhost:5432/ivor_db")
    REDIS_URL: str = os.getenv("REDIS_URL", "redis://localhost:6379")
    
    # ChromaDB Configuration
    CHROMA_PERSIST_DIRECTORY: str = os.getenv("CHROMA_PERSIST_DIRECTORY", "./chroma_db")
    CHROMA_COLLECTION_NAME: str = os.getenv("CHROMA_COLLECTION_NAME", "blkout_community_knowledge")
    
    # Events Calendar Configuration
    EVENTS_CALENDAR_API_URL: str = os.getenv("EVENTS_CALENDAR_API_URL", "http://localhost:5173/api.html")
    EVENTS_CALENDAR_API_KEY: str = os.getenv("EVENTS_CALENDAR_API_KEY", "")
    
    # Community Configuration
    BLKOUT_VALUES: List[str] = [
        "Collaboration over competition",
        "Complexity over simplification",
        "Conversation over conversion",
        "Community over commodity",
        "Realness over perfectionism"
    ]
    
    class Config:
        env_file = ".env"
        case_sensitive = True

# Global settings instance
settings = Settings()
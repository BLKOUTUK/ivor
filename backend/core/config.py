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
    
    # AI API Configuration
    DEEPSEEK_API_KEY: str = os.getenv("DEEPSEEK_API_KEY", "")
    DEEPSEEK_BASE_URL: str = os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com/v1")
    
    QWEN_API_KEY: str = os.getenv("QWEN_API_KEY", "")
    QWEN_BASE_URL: str = os.getenv("QWEN_BASE_URL", "https://dashscope.aliyuncs.com/api/v1")
    
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    
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
"""
Database configuration for IVOR Backend
"""

import logging
from sqlalchemy import create_engine, MetaData
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
import redis

from core.config import settings

logger = logging.getLogger(__name__)

# SQLAlchemy setup
engine = create_engine(
    settings.DATABASE_URL,
    poolclass=StaticPool,
    connect_args={"check_same_thread": False} if "sqlite" in settings.DATABASE_URL else {},
    echo=settings.DEBUG
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Redis setup
try:
    redis_client = redis.from_url(settings.REDIS_URL, decode_responses=True)
except Exception as e:
    logger.warning(f"Redis connection failed: {str(e)}")
    redis_client = None

async def init_db():
    """Initialize database tables"""
    try:
        # Create all tables
        Base.metadata.create_all(bind=engine)
        logger.info("Database tables created successfully")
        
        # Test Redis connection
        if redis_client:
            redis_client.ping()
            logger.info("Redis connection established")
        else:
            logger.warning("Redis not available - caching disabled")
            
    except Exception as e:
        logger.error(f"Database initialization failed: {str(e)}")
        raise

def get_db():
    """Get database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_redis():
    """Get Redis client"""
    return redis_client
"""
IVOR Backend - FastAPI Application
Community AI Assistant for BLKOUT
"""

import os
from fastapi import FastAPI, WebSocket, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import logging
from dotenv import load_dotenv

from api.routes import chat, health, events
from api.routes.conversation_history import router as conversation_router
from api.routes.user_profile import router as profile_router
from api.community import router as community_router
from core.config import settings
from core.database import init_db
from core.ai_service import AIService
from core.knowledge_base import KnowledgeBase
from utils.logging_config import setup_logging
# Import models to ensure they're registered with SQLAlchemy
from models.community import *

# Load environment variables
load_dotenv()

# Setup logging
setup_logging()
logger = logging.getLogger(__name__)

# Initialize services
ai_service = AIService()
knowledge_base = KnowledgeBase()

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    logger.info("Starting IVOR Backend...")
    
    # Initialize database
    await init_db()
    
    # Initialize knowledge base
    await knowledge_base.initialize()
    
    # Load initial community knowledge
    await knowledge_base.load_initial_knowledge()
    
    logger.info("IVOR Backend started successfully!")
    yield
    
    logger.info("Shutting down IVOR Backend...")

# Create FastAPI app
app = FastAPI(
    title="IVOR - Community AI Assistant",
    description="Backend API for BLKOUT's Community AI Assistant",
    version="1.0.0",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routes
app.include_router(health.router, prefix="/health", tags=["health"])
app.include_router(chat.router, prefix="/chat", tags=["chat"])
app.include_router(events.router, prefix="/events", tags=["events"])
app.include_router(conversation_router, prefix="/conversations", tags=["conversations"])
app.include_router(profile_router, prefix="/profiles", tags=["profiles"])
app.include_router(community_router, prefix="/api", tags=["community"])

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "IVOR - Community AI Assistant",
        "status": "active",
        "version": "1.0.0",
        "community": "Building cooperative ownership together 🏳️‍🌈"
    }

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint for real-time chat"""
    await websocket.accept()
    
    try:
        while True:
            # Receive message from client
            data = await websocket.receive_json()
            
            # Process message through AI service
            response = await ai_service.process_message(
                message=data.get("message"),
                session_id=data.get("session_id"),
                context=data.get("context", {})
            )
            
            # Send response back to client
            await websocket.send_json({
                "type": "response",
                "message": response.message,
                "sources": response.sources,
                "suggestions": response.suggestions,
                "timestamp": response.timestamp.isoformat()
            })
            
    except Exception as e:
        logger.error(f"WebSocket error: {str(e)}")
        await websocket.close()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG,
        log_level=settings.LOG_LEVEL.lower()
    )
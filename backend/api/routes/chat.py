"""
Chat endpoints for IVOR Backend
"""

from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Dict, Any, Optional, List
from datetime import datetime
import uuid
from sqlalchemy.orm import Session

from core.ai_service import AIService
from core.database import get_db
import logging

logger = logging.getLogger(__name__)

router = APIRouter()
ai_service = AIService()

class ChatMessage(BaseModel):
    message: str
    session_id: Optional[str] = None
    context: Optional[Dict[str, Any]] = None
    user_email: Optional[str] = None
    consent_level: Optional[str] = "anonymous_only"

class ChatResponse(BaseModel):
    message: str
    sources: List[Dict[str, Any]]
    suggestions: List[str]
    timestamp: str
    model_used: str
    confidence: float
    session_id: str

@router.post("/message", response_model=ChatResponse)
async def send_message(chat_message: ChatMessage, db: Session = Depends(get_db)) -> ChatResponse:
    """Send a message to IVOR and get a response"""
    
    try:
        # Generate session ID if not provided
        session_id = chat_message.session_id or str(uuid.uuid4())
        
        # Record start time for response tracking
        start_time = datetime.utcnow()
        
        # Process message through AI service with user context
        response = await ai_service.process_message(
            message=chat_message.message,
            session_id=session_id,
            context=chat_message.context or {},
            user_email=chat_message.user_email,
            db=db
        )
        
        # Calculate response time
        response_time_ms = int((datetime.utcnow() - start_time).total_seconds() * 1000)
        
        # Store conversation in database (respects consent level)
        if chat_message.consent_level != "anonymous_only" or chat_message.user_email:
            try:
                from services.ivor_storage import ivor_storage_service
                await ivor_storage_service.store_interaction({
                    "email": chat_message.user_email,
                    "session_id": session_id,
                    "user_message": chat_message.message,
                    "ivor_response": response.message,
                    "sources": [source.get("title", "") for source in response.sources],
                    "response_time_ms": response_time_ms,
                    "interaction_context": chat_message.context,
                    "consent_level": chat_message.consent_level
                }, db)
            except Exception as e:
                # Log error but don't fail the request
                logger.error(f"Failed to store conversation: {str(e)}")
        
        return ChatResponse(
            message=response.message,
            sources=response.sources,
            suggestions=response.suggestions,
            timestamp=response.timestamp.isoformat(),
            model_used=response.model_used,
            confidence=response.confidence,
            session_id=session_id
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to process message: {str(e)}"
        )

@router.get("/suggestions")
async def get_conversation_starters() -> Dict[str, List[str]]:
    """Get suggested conversation starters"""
    
    return {
        "suggestions": [
            "What's happening in the community this week?",
            "How do I get started with cooperative ownership?",
            "Tell me about BLKOUT's values and approach",
            "I'm interested in connecting with other community members",
            "What events are coming up?",
            "How can I contribute to the community?",
            "What resources are available for starting a cooperative?",
            "Tell me about Black queer liberation and economic alternatives"
        ]
    }
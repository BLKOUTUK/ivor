"""
Chat endpoints for IVOR Backend
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Dict, Any, Optional, List
from datetime import datetime
import uuid

from core.ai_service import AIService

router = APIRouter()
ai_service = AIService()

class ChatMessage(BaseModel):
    message: str
    session_id: Optional[str] = None
    context: Optional[Dict[str, Any]] = None

class ChatResponse(BaseModel):
    message: str
    sources: List[Dict[str, Any]]
    suggestions: List[str]
    timestamp: str
    model_used: str
    confidence: float
    session_id: str

@router.post("/message", response_model=ChatResponse)
async def send_message(chat_message: ChatMessage) -> ChatResponse:
    """Send a message to IVOR and get a response"""
    
    try:
        # Generate session ID if not provided
        session_id = chat_message.session_id or str(uuid.uuid4())
        
        # Process message through AI service
        response = await ai_service.process_message(
            message=chat_message.message,
            session_id=session_id,
            context=chat_message.context or {}
        )
        
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
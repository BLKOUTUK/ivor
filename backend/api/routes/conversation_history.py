"""
Conversation History endpoints for IVOR Backend
Privacy-first conversation management
"""

from fastapi import APIRouter, HTTPException, Depends, Query
from pydantic import BaseModel
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import and_, desc, func

from core.database import get_db
from models.community import CommunityProfile, IvorInteraction
from services.consent_manager import consent_manager
from services.user_context_service import user_context_service

router = APIRouter()

class ConversationSummary(BaseModel):
    session_id: str
    last_message_time: datetime
    message_count: int
    topics: List[str]
    user_satisfaction: Optional[float] = None

class ConversationMessage(BaseModel):
    user_message: str
    ivor_response: str
    timestamp: datetime
    sources: List[str]
    user_satisfaction: Optional[int] = None

class ConversationDetail(BaseModel):
    session_id: str
    messages: List[ConversationMessage]
    summary: ConversationSummary

class ConversationStatsResponse(BaseModel):
    total_conversations: int
    total_messages: int
    avg_satisfaction: float
    common_topics: List[Dict[str, Any]]
    recent_activity: List[ConversationSummary]

@router.get("/history/{email}", response_model=List[ConversationSummary])
async def get_conversation_history(
    email: str,
    limit: int = Query(default=10, le=50),
    days: int = Query(default=30, le=90),
    db: Session = Depends(get_db)
):
    """Get conversation history for a user (respects consent)"""
    
    try:
        # Get user profile and check consent
        profile = db.query(CommunityProfile).filter(
            CommunityProfile.email == email
        ).first()
        
        if not profile:
            raise HTTPException(status_code=404, detail="Profile not found")
        
        # Check if user consents to personal service
        consent_level = consent_manager.get_effective_consent_level(profile.consent_preferences)
        
        if consent_level == "anonymous_only":
            raise HTTPException(
                status_code=403, 
                detail="User has not consented to conversation history storage"
            )
        
        # Get conversations from specified time period
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        
        # Get unique sessions with aggregated data
        sessions = db.query(
            IvorInteraction.session_id,
            func.max(IvorInteraction.created_at).label('last_message_time'),
            func.count(IvorInteraction.id).label('message_count'),
            func.avg(IvorInteraction.user_satisfaction).label('avg_satisfaction')
        ).filter(
            and_(
                IvorInteraction.profile_id == profile.id,
                IvorInteraction.created_at >= cutoff_date
            )
        ).group_by(
            IvorInteraction.session_id
        ).order_by(
            desc('last_message_time')
        ).limit(limit).all()
        
        conversation_summaries = []
        for session in sessions:
            # Get sample messages to extract topics
            sample_messages = db.query(IvorInteraction).filter(
                and_(
                    IvorInteraction.profile_id == profile.id,
                    IvorInteraction.session_id == session.session_id
                )
            ).limit(3).all()
            
            # Extract topics from messages
            topics = []
            for msg in sample_messages:
                msg_topics = user_context_service._extract_topics(msg.user_message)
                topics.extend(msg_topics)
            
            topics = list(set(topics))  # Remove duplicates
            
            conversation_summaries.append(ConversationSummary(
                session_id=session.session_id,
                last_message_time=session.last_message_time,
                message_count=session.message_count,
                topics=topics,
                user_satisfaction=session.avg_satisfaction
            ))
        
        return conversation_summaries
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error retrieving conversation history: {str(e)}"
        )

@router.get("/conversation/{email}/{session_id}", response_model=ConversationDetail)
async def get_conversation_detail(
    email: str,
    session_id: str,
    db: Session = Depends(get_db)
):
    """Get detailed conversation for a specific session"""
    
    try:
        # Get user profile and check consent
        profile = db.query(CommunityProfile).filter(
            CommunityProfile.email == email
        ).first()
        
        if not profile:
            raise HTTPException(status_code=404, detail="Profile not found")
        
        # Check consent
        consent_level = consent_manager.get_effective_consent_level(profile.consent_preferences)
        
        if consent_level == "anonymous_only":
            raise HTTPException(
                status_code=403, 
                detail="User has not consented to detailed conversation history"
            )
        
        # Get all messages for this session
        messages = db.query(IvorInteraction).filter(
            and_(
                IvorInteraction.profile_id == profile.id,
                IvorInteraction.session_id == session_id
            )
        ).order_by(IvorInteraction.created_at).all()
        
        if not messages:
            raise HTTPException(status_code=404, detail="Conversation not found")
        
        # Build conversation detail
        conversation_messages = []
        topics = []
        
        for msg in messages:
            conversation_messages.append(ConversationMessage(
                user_message=msg.user_message,
                ivor_response=msg.ivor_response,
                timestamp=msg.created_at,
                sources=msg.sources or [],
                user_satisfaction=msg.user_satisfaction
            ))
            
            # Extract topics
            msg_topics = user_context_service._extract_topics(msg.user_message)
            topics.extend(msg_topics)
        
        topics = list(set(topics))
        
        # Create summary
        summary = ConversationSummary(
            session_id=session_id,
            last_message_time=messages[-1].created_at,
            message_count=len(messages),
            topics=topics,
            user_satisfaction=sum(m.user_satisfaction for m in messages if m.user_satisfaction) / len([m for m in messages if m.user_satisfaction]) if any(m.user_satisfaction for m in messages) else None
        )
        
        return ConversationDetail(
            session_id=session_id,
            messages=conversation_messages,
            summary=summary
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error retrieving conversation detail: {str(e)}"
        )

@router.get("/stats/{email}", response_model=ConversationStatsResponse)
async def get_conversation_stats(
    email: str,
    days: int = Query(default=30, le=90),
    db: Session = Depends(get_db)
):
    """Get conversation statistics for a user"""
    
    try:
        # Get user profile and check consent
        profile = db.query(CommunityProfile).filter(
            CommunityProfile.email == email
        ).first()
        
        if not profile:
            raise HTTPException(status_code=404, detail="Profile not found")
        
        # Check consent
        consent_level = consent_manager.get_effective_consent_level(profile.consent_preferences)
        
        if consent_level == "anonymous_only":
            raise HTTPException(
                status_code=403, 
                detail="User has not consented to conversation statistics"
            )
        
        # Get interactions from specified time period
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        
        interactions = db.query(IvorInteraction).filter(
            and_(
                IvorInteraction.profile_id == profile.id,
                IvorInteraction.created_at >= cutoff_date
            )
        ).all()
        
        # Calculate stats
        total_conversations = len(set(interaction.session_id for interaction in interactions))
        total_messages = len(interactions)
        
        # Calculate average satisfaction
        satisfactions = [i.user_satisfaction for i in interactions if i.user_satisfaction]
        avg_satisfaction = sum(satisfactions) / len(satisfactions) if satisfactions else 0.0
        
        # Extract common topics
        all_topics = []
        for interaction in interactions:
            topics = user_context_service._extract_topics(interaction.user_message)
            all_topics.extend(topics)
        
        # Count topic frequency
        topic_counts = {}
        for topic in all_topics:
            topic_counts[topic] = topic_counts.get(topic, 0) + 1
        
        # Get top 10 topics
        common_topics = [
            {"topic": topic, "count": count}
            for topic, count in sorted(topic_counts.items(), key=lambda x: x[1], reverse=True)[:10]
        ]
        
        # Get recent activity (last 10 sessions)
        recent_sessions = db.query(
            IvorInteraction.session_id,
            func.max(IvorInteraction.created_at).label('last_message_time'),
            func.count(IvorInteraction.id).label('message_count')
        ).filter(
            and_(
                IvorInteraction.profile_id == profile.id,
                IvorInteraction.created_at >= cutoff_date
            )
        ).group_by(
            IvorInteraction.session_id
        ).order_by(
            desc('last_message_time')
        ).limit(10).all()
        
        recent_activity = []
        for session in recent_sessions:
            # Get topics for this session
            session_messages = db.query(IvorInteraction).filter(
                and_(
                    IvorInteraction.profile_id == profile.id,
                    IvorInteraction.session_id == session.session_id
                )
            ).limit(3).all()
            
            topics = []
            for msg in session_messages:
                topics.extend(user_context_service._extract_topics(msg.user_message))
            
            recent_activity.append(ConversationSummary(
                session_id=session.session_id,
                last_message_time=session.last_message_time,
                message_count=session.message_count,
                topics=list(set(topics))
            ))
        
        return ConversationStatsResponse(
            total_conversations=total_conversations,
            total_messages=total_messages,
            avg_satisfaction=avg_satisfaction,
            common_topics=common_topics,
            recent_activity=recent_activity
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error retrieving conversation stats: {str(e)}"
        )

@router.delete("/history/{email}/{session_id}")
async def delete_conversation(
    email: str,
    session_id: str,
    db: Session = Depends(get_db)
):
    """Delete a specific conversation (user control)"""
    
    try:
        # Get user profile
        profile = db.query(CommunityProfile).filter(
            CommunityProfile.email == email
        ).first()
        
        if not profile:
            raise HTTPException(status_code=404, detail="Profile not found")
        
        # Delete all messages for this session
        deleted_count = db.query(IvorInteraction).filter(
            and_(
                IvorInteraction.profile_id == profile.id,
                IvorInteraction.session_id == session_id
            )
        ).delete()
        
        db.commit()
        
        return {"message": f"Deleted {deleted_count} messages from conversation {session_id}"}
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"Error deleting conversation: {str(e)}"
        )

@router.delete("/history/{email}")
async def delete_all_conversations(
    email: str,
    confirm: bool = Query(default=False),
    db: Session = Depends(get_db)
):
    """Delete all conversations for a user (user control)"""
    
    if not confirm:
        raise HTTPException(
            status_code=400,
            detail="Must confirm deletion with confirm=true parameter"
        )
    
    try:
        # Get user profile
        profile = db.query(CommunityProfile).filter(
            CommunityProfile.email == email
        ).first()
        
        if not profile:
            raise HTTPException(status_code=404, detail="Profile not found")
        
        # Delete all conversations
        deleted_count = db.query(IvorInteraction).filter(
            IvorInteraction.profile_id == profile.id
        ).delete()
        
        db.commit()
        
        # Clear user context cache
        user_context_service.clear_cache(email)
        
        return {"message": f"Deleted {deleted_count} conversation messages"}
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"Error deleting all conversations: {str(e)}"
        )

@router.post("/feedback/{email}/{session_id}")
async def submit_conversation_feedback(
    email: str,
    session_id: str,
    satisfaction: int = Query(..., ge=1, le=5),
    db: Session = Depends(get_db)
):
    """Submit feedback for a conversation"""
    
    try:
        # Get user profile
        profile = db.query(CommunityProfile).filter(
            CommunityProfile.email == email
        ).first()
        
        if not profile:
            raise HTTPException(status_code=404, detail="Profile not found")
        
        # Update satisfaction rating for the last message in the session
        last_message = db.query(IvorInteraction).filter(
            and_(
                IvorInteraction.profile_id == profile.id,
                IvorInteraction.session_id == session_id
            )
        ).order_by(desc(IvorInteraction.created_at)).first()
        
        if not last_message:
            raise HTTPException(status_code=404, detail="Conversation not found")
        
        last_message.user_satisfaction = satisfaction
        db.commit()
        
        return {"message": "Feedback submitted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"Error submitting feedback: {str(e)}"
        )
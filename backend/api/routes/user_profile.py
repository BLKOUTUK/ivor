"""
Unified User Profile endpoints for BLKOUT Community
Privacy-first, comprehensive profile management
"""

from fastapi import APIRouter, HTTPException, Depends, Query
from pydantic import BaseModel, EmailStr
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import and_, desc, func

from core.database import get_db
from models.community import (
    CommunityProfile, 
    EmailSubscription, 
    BlkouthubRequest, 
    QuizResult, 
    IvorInteraction,
    EngagementEvent,
    ConsentAudit,
    KnowledgeContribution
)
from services.consent_manager import consent_manager
from services.user_context_service import user_context_service
from schemas.community import ConsentUpdate, CommunityProfileResponse

router = APIRouter()

class ProfileSummary(BaseModel):
    profile_id: str
    email: str
    name: Optional[str] = None
    location: Optional[str] = None
    journey_stage: str
    engagement_score: int
    member_since: datetime
    last_interaction: datetime
    consent_level: str
    
class ProfileActivity(BaseModel):
    email_subscriptions: int
    blkouthub_requests: int
    quiz_results: int
    ivor_conversations: int
    engagement_events: int
    knowledge_contributions: int
    total_interactions: int

class ProfileInsights(BaseModel):
    liberation_pathway: Optional[Dict[str, Any]] = None
    community_interests: List[str] = []
    interaction_patterns: Dict[str, Any] = {}
    peer_matches: List[Dict[str, Any]] = []
    recent_topics: List[str] = []

class ProfilePrivacy(BaseModel):
    consent_preferences: Dict[str, bool]
    consent_level: str
    data_retention_days: int
    data_anonymization: bool
    last_consent_change: datetime
    consent_history: List[Dict[str, Any]]

class UnifiedProfile(BaseModel):
    summary: ProfileSummary
    activity: ProfileActivity
    insights: Optional[ProfileInsights] = None
    privacy: ProfilePrivacy

@router.get("/profile/{email}", response_model=UnifiedProfile)
async def get_unified_profile(
    email: str,
    include_insights: bool = Query(default=True),
    db: Session = Depends(get_db)
):
    """Get comprehensive unified profile for a user"""
    
    try:
        # Get user profile
        profile = db.query(CommunityProfile).filter(
            CommunityProfile.email == email
        ).first()
        
        if not profile:
            raise HTTPException(status_code=404, detail="Profile not found")
        
        # Get consent level
        consent_level = consent_manager.get_effective_consent_level(profile.consent_preferences)
        
        # Build profile summary
        summary = ProfileSummary(
            profile_id=str(profile.id),
            email=profile.email,
            name=profile.name,
            location=profile.location,
            journey_stage=profile.journey_stage,
            engagement_score=profile.engagement_score,
            member_since=profile.created_at,
            last_interaction=profile.last_interaction,
            consent_level=consent_level
        )
        
        # Get activity counts
        activity = ProfileActivity(
            email_subscriptions=db.query(EmailSubscription).filter(
                EmailSubscription.profile_id == profile.id
            ).count(),
            blkouthub_requests=db.query(BlkouthubRequest).filter(
                BlkouthubRequest.profile_id == profile.id
            ).count(),
            quiz_results=db.query(QuizResult).filter(
                QuizResult.profile_id == profile.id
            ).count(),
            ivor_conversations=db.query(IvorInteraction).filter(
                IvorInteraction.profile_id == profile.id
            ).with_entities(func.count(func.distinct(IvorInteraction.session_id))).scalar(),
            engagement_events=db.query(EngagementEvent).filter(
                EngagementEvent.profile_id == profile.id
            ).count(),
            knowledge_contributions=db.query(KnowledgeContribution).filter(
                KnowledgeContribution.profile_id == profile.id
            ).count(),
            total_interactions=db.query(IvorInteraction).filter(
                IvorInteraction.profile_id == profile.id
            ).count()
        )
        
        # Get privacy information
        privacy = ProfilePrivacy(
            consent_preferences=profile.consent_preferences,
            consent_level=consent_level,
            data_retention_days=consent_manager.get_data_retention_period(profile.consent_preferences),
            data_anonymization=consent_manager.should_anonymize_data(profile.consent_preferences),
            last_consent_change=profile.updated_at,
            consent_history=consent_manager.get_consent_history(str(profile.id), db)
        )
        
        # Get insights if consented and requested
        insights = None
        if include_insights and consent_level != "anonymous_only":
            insights = await _get_profile_insights(profile, db)
        
        return UnifiedProfile(
            summary=summary,
            activity=activity,
            insights=insights,
            privacy=privacy
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error retrieving unified profile: {str(e)}"
        )

async def _get_profile_insights(profile: CommunityProfile, db: Session) -> ProfileInsights:
    """Get profile insights based on consent level"""
    
    # Get user context
    user_context = await user_context_service.get_user_context(
        email=profile.email,
        session_id="profile_insights",
        db=db
    )
    
    return ProfileInsights(
        liberation_pathway=user_context.get("liberation_pathway"),
        community_interests=user_context.get("community_interests", []),
        interaction_patterns=user_context.get("community_connections", {}),
        peer_matches=user_context.get("peer_matches", []),
        recent_topics=_get_recent_topics(profile.id, db)
    )

def _get_recent_topics(profile_id: str, db: Session) -> List[str]:
    """Get recent conversation topics"""
    
    # Get recent conversations
    recent_conversations = db.query(IvorInteraction).filter(
        and_(
            IvorInteraction.profile_id == profile_id,
            IvorInteraction.created_at >= datetime.utcnow() - timedelta(days=7)
        )
    ).order_by(desc(IvorInteraction.created_at)).limit(10).all()
    
    # Extract topics
    all_topics = []
    for conv in recent_conversations:
        topics = user_context_service._extract_topics(conv.user_message)
        all_topics.extend(topics)
    
    # Return unique topics
    return list(set(all_topics))

@router.get("/profile/{email}/journey", response_model=Dict[str, Any])
async def get_user_journey(
    email: str,
    days: int = Query(default=90, le=365),
    db: Session = Depends(get_db)
):
    """Get user's community journey timeline"""
    
    try:
        # Get user profile
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
                detail="User has not consented to journey tracking"
            )
        
        # Get journey events
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        
        # Collect different types of events
        events = []
        
        # Email subscriptions
        email_subs = db.query(EmailSubscription).filter(
            and_(
                EmailSubscription.profile_id == profile.id,
                EmailSubscription.created_at >= cutoff_date
            )
        ).all()
        
        for sub in email_subs:
            events.append({
                "type": "email_subscription",
                "timestamp": sub.created_at,
                "data": {
                    "interests": sub.interests,
                    "source": sub.source,
                    "blkouthub_interest": sub.blkouthub_interest
                }
            })
        
        # Quiz results
        quiz_results = db.query(QuizResult).filter(
            and_(
                QuizResult.profile_id == profile.id,
                QuizResult.created_at >= cutoff_date
            )
        ).all()
        
        for quiz in quiz_results:
            events.append({
                "type": "quiz_completion",
                "timestamp": quiz.created_at,
                "data": {
                    "pathway": quiz.pathway,
                    "pathway_title": quiz.pathway_title,
                    "community_match": quiz.community_match
                }
            })
        
        # BLKOUTHUB requests
        blkouthub_requests = db.query(BlkouthubRequest).filter(
            and_(
                BlkouthubRequest.profile_id == profile.id,
                BlkouthubRequest.created_at >= cutoff_date
            )
        ).all()
        
        for request in blkouthub_requests:
            events.append({
                "type": "blkouthub_request",
                "timestamp": request.created_at,
                "data": {
                    "status": request.status,
                    "reviewed_at": request.reviewed_at,
                    "invitation_sent": request.invitation_sent_at is not None
                }
            })
        
        # Engagement milestones
        engagement_events = db.query(EngagementEvent).filter(
            and_(
                EngagementEvent.profile_id == profile.id,
                EngagementEvent.created_at >= cutoff_date,
                EngagementEvent.engagement_score_delta > 0
            )
        ).all()
        
        # Group engagement events by type
        engagement_summary = {}
        for event in engagement_events:
            event_type = event.event_type
            if event_type not in engagement_summary:
                engagement_summary[event_type] = {
                    "count": 0,
                    "total_score": 0,
                    "first_occurrence": event.created_at,
                    "last_occurrence": event.created_at
                }
            
            engagement_summary[event_type]["count"] += 1
            engagement_summary[event_type]["total_score"] += event.engagement_score_delta
            engagement_summary[event_type]["last_occurrence"] = max(
                engagement_summary[event_type]["last_occurrence"],
                event.created_at
            )
        
        # Add engagement milestones to timeline
        for event_type, summary in engagement_summary.items():
            if summary["count"] >= 5:  # Milestone threshold
                events.append({
                    "type": "engagement_milestone",
                    "timestamp": summary["last_occurrence"],
                    "data": {
                        "event_type": event_type,
                        "count": summary["count"],
                        "total_score": summary["total_score"]
                    }
                })
        
        # Sort events by timestamp
        events.sort(key=lambda x: x["timestamp"])
        
        return {
            "profile_id": str(profile.id),
            "email": profile.email,
            "journey_start": profile.created_at,
            "current_stage": profile.journey_stage,
            "total_engagement_score": profile.engagement_score,
            "events": events,
            "journey_duration_days": (datetime.utcnow() - profile.created_at).days,
            "events_in_period": len(events)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error retrieving user journey: {str(e)}"
        )

@router.get("/profile/{email}/recommendations", response_model=Dict[str, Any])
async def get_profile_recommendations(
    email: str,
    db: Session = Depends(get_db)
):
    """Get personalized recommendations for user"""
    
    try:
        # Get user profile
        profile = db.query(CommunityProfile).filter(
            CommunityProfile.email == email
        ).first()
        
        if not profile:
            raise HTTPException(status_code=404, detail="Profile not found")
        
        # Check consent
        consent_level = consent_manager.get_effective_consent_level(profile.consent_preferences)
        
        if consent_level == "anonymous_only":
            return {
                "recommendations": [
                    {
                        "type": "consent_upgrade",
                        "title": "Unlock Personalized Recommendations",
                        "description": "Enable personal service consent to receive tailored community recommendations",
                        "action": "update_consent",
                        "priority": "high"
                    }
                ]
            }
        
        recommendations = []
        
        # Get user context for recommendations
        user_context = await user_context_service.get_user_context(
            email=profile.email,
            session_id="recommendations",
            db=db
        )
        
        # Journey stage recommendations
        journey_stage = profile.journey_stage
        
        if journey_stage == "new":
            recommendations.append({
                "type": "pathway_discovery",
                "title": "Discover Your Liberation Pathway",
                "description": "Take our 5-question quiz to find your community match and next steps",
                "action": "take_quiz",
                "priority": "high"
            })
        
        elif journey_stage == "engaged":
            recommendations.append({
                "type": "community_connection",
                "title": "Connect with Your Community",
                "description": "Join discussions and events that align with your interests",
                "action": "browse_events",
                "priority": "medium"
            })
        
        # Pathway-based recommendations
        pathway = user_context.get("liberation_pathway")
        if pathway:
            pathway_type = pathway.get("pathway")
            
            if pathway_type == "storyteller":
                recommendations.append({
                    "type": "content_contribution",
                    "title": "Share Your Story",
                    "description": "Contribute to our community storytelling initiative",
                    "action": "contribute_story",
                    "priority": "medium"
                })
            
            elif pathway_type == "organizer":
                recommendations.append({
                    "type": "organizing_opportunity",
                    "title": "Join Organizing Efforts",
                    "description": "Get involved in community organizing and advocacy work",
                    "action": "join_organizing",
                    "priority": "high"
                })
        
        # Interest-based recommendations
        interests = user_context.get("community_interests", [])
        
        if "blkouthub-access" in interests:
            blkouthub_status = user_context.get("blkouthub_status")
            if not blkouthub_status:
                recommendations.append({
                    "type": "blkouthub_access",
                    "title": "Apply for BLKOUTHUB Access",
                    "description": "Join our private community platform for Black queer men",
                    "action": "apply_blkouthub",
                    "priority": "high"
                })
        
        # Engagement recommendations
        if profile.engagement_score < 50:
            recommendations.append({
                "type": "engagement_boost",
                "title": "Increase Community Engagement",
                "description": "Explore more community resources and participate in discussions",
                "action": "explore_resources",
                "priority": "low"
            })
        
        # Peer connection recommendations
        if consent_level == "peer_connections":
            peer_matches = user_context.get("peer_matches", [])
            if peer_matches:
                recommendations.append({
                    "type": "peer_connection",
                    "title": "Connect with Similar Community Members",
                    "description": f"You have {len(peer_matches)} potential matches on similar liberation pathways",
                    "action": "view_peer_matches",
                    "priority": "medium"
                })
        
        # Privacy recommendations
        if consent_level == "anonymous_only":
            recommendations.append({
                "type": "privacy_upgrade",
                "title": "Enable Community Insights",
                "description": "Allow us to provide better community matching and recommendations",
                "action": "update_consent",
                "priority": "low"
            })
        
        return {
            "profile_id": str(profile.id),
            "recommendations": recommendations,
            "total_recommendations": len(recommendations),
            "based_on": {
                "journey_stage": journey_stage,
                "consent_level": consent_level,
                "engagement_score": profile.engagement_score,
                "pathway": pathway.get("pathway") if pathway else None
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error generating recommendations: {str(e)}"
        )

@router.put("/profile/{email}/journey-stage")
async def update_journey_stage(
    email: str,
    new_stage: str = Query(..., regex="^(new|engaged|active|committed)$"),
    db: Session = Depends(get_db)
):
    """Update user's journey stage"""
    
    try:
        # Get user profile
        profile = db.query(CommunityProfile).filter(
            CommunityProfile.email == email
        ).first()
        
        if not profile:
            raise HTTPException(status_code=404, detail="Profile not found")
        
        old_stage = profile.journey_stage
        profile.journey_stage = new_stage
        profile.updated_at = datetime.utcnow()
        
        # Log the change as an engagement event
        engagement_event = EngagementEvent(
            profile_id=profile.id,
            event_type="journey_stage_update",
            event_data={
                "old_stage": old_stage,
                "new_stage": new_stage
            },
            engagement_score_delta=0
        )
        db.add(engagement_event)
        
        db.commit()
        
        # Clear user context cache
        user_context_service.clear_cache(email)
        
        return {
            "message": f"Journey stage updated from {old_stage} to {new_stage}",
            "old_stage": old_stage,
            "new_stage": new_stage
        }
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"Error updating journey stage: {str(e)}"
        )

@router.get("/profile/{email}/export")
async def export_profile_data(
    email: str,
    format: str = Query(default="json", regex="^(json|csv)$"),
    db: Session = Depends(get_db)
):
    """Export user's complete profile data"""
    
    try:
        # Get user profile
        profile = db.query(CommunityProfile).filter(
            CommunityProfile.email == email
        ).first()
        
        if not profile:
            raise HTTPException(status_code=404, detail="Profile not found")
        
        # Get all related data
        export_data = {
            "profile": {
                "id": str(profile.id),
                "email": profile.email,
                "name": profile.name,
                "location": profile.location,
                "created_at": profile.created_at.isoformat(),
                "updated_at": profile.updated_at.isoformat(),
                "journey_stage": profile.journey_stage,
                "engagement_score": profile.engagement_score,
                "consent_preferences": profile.consent_preferences
            },
            "email_subscriptions": [
                {
                    "interests": sub.interests,
                    "source": sub.source,
                    "created_at": sub.created_at.isoformat(),
                    "engagement_level": sub.engagement_level
                }
                for sub in profile.email_subscriptions
            ],
            "quiz_results": [
                {
                    "pathway": quiz.pathway,
                    "pathway_title": quiz.pathway_title,
                    "scores": quiz.scores,
                    "community_match": quiz.community_match,
                    "created_at": quiz.created_at.isoformat()
                }
                for quiz in profile.quiz_results
            ],
            "blkouthub_requests": [
                {
                    "status": req.status,
                    "connection_reason": req.connection_reason,
                    "created_at": req.created_at.isoformat(),
                    "reviewed_at": req.reviewed_at.isoformat() if req.reviewed_at else None
                }
                for req in profile.blkouthub_requests
            ],
            "engagement_events": [
                {
                    "event_type": event.event_type,
                    "engagement_score_delta": event.engagement_score_delta,
                    "created_at": event.created_at.isoformat()
                }
                for event in profile.engagement_events
            ],
            "export_metadata": {
                "exported_at": datetime.utcnow().isoformat(),
                "format": format,
                "total_records": {
                    "email_subscriptions": len(profile.email_subscriptions),
                    "quiz_results": len(profile.quiz_results),
                    "blkouthub_requests": len(profile.blkouthub_requests),
                    "engagement_events": len(profile.engagement_events)
                }
            }
        }
        
        return export_data
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error exporting profile data: {str(e)}"
        )
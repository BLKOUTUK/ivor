"""
Community API endpoints for BLKOUT data integration
Privacy-first, liberation-centered data management
"""

from fastapi import APIRouter, HTTPException, Depends, status
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
import uuid
import json

from core.database import get_db
from models.community import (
    CommunityProfile,
    EmailSubscription,
    BlkouthubRequest,
    QuizResult,
    IvorInteraction,
    EngagementEvent,
    ConsentAudit
)
from schemas.community import (
    CommunityProfileCreate,
    CommunityProfileResponse,
    EmailSubscriptionCreate,
    BlkouthubRequestCreate,
    QuizResultCreate,
    IvorInteractionCreate,
    ConsentUpdate,
    EngagementEventCreate
)

router = APIRouter(prefix="/community", tags=["community"])

# Community Profile Management
@router.post("/profile", response_model=CommunityProfileResponse)
async def create_or_update_profile(
    profile_data: CommunityProfileCreate,
    db: Session = Depends(get_db)
):
    """
    Create or update a community profile with privacy-first consent management
    Supports upsert functionality for existing emails
    """
    try:
        # Check if profile exists
        existing_profile = db.query(CommunityProfile).filter(
            CommunityProfile.email == profile_data.email
        ).first()
        
        if existing_profile:
            # Update existing profile
            for key, value in profile_data.dict(exclude_unset=True).items():
                if key == "consent_preferences":
                    # Log consent changes
                    old_consent = existing_profile.consent_preferences
                    new_consent = value
                    
                    # Track changes in consent_audit
                    for consent_type in ["anonymous_only", "personal_service", "community_insights", "peer_connections"]:
                        if old_consent.get(consent_type) != new_consent.get(consent_type):
                            audit_entry = ConsentAudit(
                                profile_id=existing_profile.id,
                                consent_type=consent_type,
                                previous_value=old_consent.get(consent_type),
                                new_value=new_consent.get(consent_type),
                                change_reason="user_update"
                            )
                            db.add(audit_entry)
                
                setattr(existing_profile, key, value)
            
            existing_profile.updated_at = datetime.utcnow()
            existing_profile.last_interaction = datetime.utcnow()
            db.commit()
            db.refresh(existing_profile)
            return existing_profile
        else:
            # Create new profile
            new_profile = CommunityProfile(**profile_data.dict())
            db.add(new_profile)
            db.commit()
            db.refresh(new_profile)
            
            # Log initial consent choices
            for consent_type, value in profile_data.consent_preferences.items():
                if value:  # Only log affirmative consents
                    audit_entry = ConsentAudit(
                        profile_id=new_profile.id,
                        consent_type=consent_type,
                        previous_value=None,
                        new_value=value,
                        change_reason="initial_registration"
                    )
                    db.add(audit_entry)
            
            db.commit()
            return new_profile
            
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating/updating profile: {str(e)}"
        )

@router.get("/profile/{profile_id}", response_model=CommunityProfileResponse)
async def get_profile(profile_id: str, db: Session = Depends(get_db)):
    """Get community profile by ID"""
    profile = db.query(CommunityProfile).filter(CommunityProfile.id == profile_id).first()
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Profile not found"
        )
    return profile

@router.put("/profile/{profile_id}/consent", response_model=CommunityProfileResponse)
async def update_consent(
    profile_id: str,
    consent_data: ConsentUpdate,
    db: Session = Depends(get_db)
):
    """Update consent preferences with full audit trail"""
    profile = db.query(CommunityProfile).filter(CommunityProfile.id == profile_id).first()
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Profile not found"
        )
    
    try:
        old_consent = profile.consent_preferences
        new_consent = consent_data.consent_preferences
        
        # Log all consent changes
        for consent_type in ["anonymous_only", "personal_service", "community_insights", "peer_connections"]:
            if old_consent.get(consent_type) != new_consent.get(consent_type):
                audit_entry = ConsentAudit(
                    profile_id=profile.id,
                    consent_type=consent_type,
                    previous_value=old_consent.get(consent_type),
                    new_value=new_consent.get(consent_type),
                    change_reason=consent_data.change_reason or "user_update"
                )
                db.add(audit_entry)
        
        profile.consent_preferences = new_consent
        profile.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(profile)
        return profile
        
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error updating consent: {str(e)}"
        )

# Email Subscriptions
@router.post("/email-subscription")
async def create_email_subscription(
    subscription_data: EmailSubscriptionCreate,
    db: Session = Depends(get_db)
):
    """Create email subscription with profile linking"""
    try:
        # Get or create profile
        profile = db.query(CommunityProfile).filter(
            CommunityProfile.email == subscription_data.email
        ).first()
        
        if not profile:
            # Create minimal profile for email subscriber
            profile = CommunityProfile(
                email=subscription_data.email,
                source="email_capture",
                consent_preferences={
                    "anonymous_only": True,
                    "personal_service": False,
                    "community_insights": False,
                    "peer_connections": False
                }
            )
            db.add(profile)
            db.flush()  # Get the ID
        
        # Create subscription
        subscription = EmailSubscription(
            profile_id=profile.id,
            interests=subscription_data.interests,
            source=subscription_data.source,
            n8n_tracking_id=subscription_data.n8n_tracking_id,
            engagement_level=subscription_data.engagement_level,
            blkouthub_interest=subscription_data.blkouthub_interest,
            referrer=subscription_data.referrer,
            consent_level="anonymous_only"
        )
        db.add(subscription)
        
        # Log engagement event
        engagement_event = EngagementEvent(
            profile_id=profile.id,
            event_type="email_subscription",
            event_data={
                "interests": subscription_data.interests,
                "source": subscription_data.source,
                "blkouthub_interest": subscription_data.blkouthub_interest
            },
            engagement_score_delta=10  # Email signup = 10 points
        )
        db.add(engagement_event)
        
        db.commit()
        return {"message": "Email subscription created successfully", "profile_id": str(profile.id)}
        
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating email subscription: {str(e)}"
        )

# BLKOUTHUB Access Requests
@router.post("/blkouthub-request")
async def create_blkouthub_request(
    request_data: BlkouthubRequestCreate,
    db: Session = Depends(get_db)
):
    """Create BLKOUTHUB access request"""
    try:
        # Get or create profile
        profile = db.query(CommunityProfile).filter(
            CommunityProfile.email == request_data.email
        ).first()
        
        if not profile:
            profile = CommunityProfile(
                email=request_data.email,
                name=request_data.name,
                location=request_data.location,
                source="blkouthub",
                consent_preferences={
                    "anonymous_only": False,
                    "personal_service": True,
                    "community_insights": True,
                    "peer_connections": False
                }
            )
            db.add(profile)
            db.flush()
        
        # Create access request
        access_request = BlkouthubRequest(
            profile_id=profile.id,
            identity_affirmation=request_data.identity_affirmation,
            connection_reason=request_data.connection_reason,
            referral_source=request_data.referral_source,
            community_guidelines_agreed=request_data.community_guidelines_agreed,
            status="pending",
            consent_level="personal_service"
        )
        db.add(access_request)
        
        # Log engagement event
        engagement_event = EngagementEvent(
            profile_id=profile.id,
            event_type="blkouthub_request",
            event_data={
                "identity_affirmation": request_data.identity_affirmation,
                "connection_reason": request_data.connection_reason,
                "referral_source": request_data.referral_source
            },
            engagement_score_delta=25  # BLKOUTHUB request = 25 points
        )
        db.add(engagement_event)
        
        db.commit()
        return {"message": "BLKOUTHUB access request created successfully", "profile_id": str(profile.id)}
        
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating BLKOUTHUB request: {str(e)}"
        )

# Quiz Results
@router.post("/quiz-result")
async def create_quiz_result(
    quiz_data: QuizResultCreate,
    db: Session = Depends(get_db)
):
    """Store quiz result with optional profile linking"""
    try:
        profile_id = None
        
        # Link to profile if email provided
        if quiz_data.email:
            profile = db.query(CommunityProfile).filter(
                CommunityProfile.email == quiz_data.email
            ).first()
            
            if not profile:
                profile = CommunityProfile(
                    email=quiz_data.email,
                    name=quiz_data.name,
                    location=quiz_data.location,
                    source="quiz",
                    consent_preferences={
                        "anonymous_only": False,
                        "personal_service": False,
                        "community_insights": True,
                        "peer_connections": False
                    }
                )
                db.add(profile)
                db.flush()
            
            profile_id = profile.id
        
        # Create quiz result
        quiz_result = QuizResult(
            profile_id=profile_id,
            pathway=quiz_data.pathway,
            pathway_title=quiz_data.pathway_title,
            scores=quiz_data.scores,
            answers=quiz_data.answers,
            community_match=quiz_data.community_match,
            next_steps=quiz_data.next_steps,
            consent_level="community_insights" if profile_id else "anonymous_only"
        )
        db.add(quiz_result)
        
        # Log engagement event if profile exists
        if profile_id:
            engagement_event = EngagementEvent(
                profile_id=profile_id,
                event_type="quiz_completion",
                event_data={
                    "pathway": quiz_data.pathway,
                    "scores": quiz_data.scores,
                    "community_match": quiz_data.community_match
                },
                engagement_score_delta=20  # Quiz completion = 20 points
            )
            db.add(engagement_event)
        
        db.commit()
        return {"message": "Quiz result stored successfully", "profile_id": str(profile_id) if profile_id else None}
        
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error storing quiz result: {str(e)}"
        )

# IVOR Interactions
@router.post("/ivor-interaction")
async def create_ivor_interaction(
    interaction_data: IvorInteractionCreate,
    db: Session = Depends(get_db)
):
    """Store IVOR conversation with privacy controls"""
    try:
        profile_id = None
        
        # Link to profile if email provided and consent given
        if interaction_data.email and interaction_data.consent_level != "anonymous_only":
            profile = db.query(CommunityProfile).filter(
                CommunityProfile.email == interaction_data.email
            ).first()
            
            if profile:
                profile_id = profile.id
        
        # Create interaction record
        interaction = IvorInteraction(
            profile_id=profile_id,
            session_id=interaction_data.session_id,
            user_message=interaction_data.user_message,
            ivor_response=interaction_data.ivor_response,
            sources=interaction_data.sources,
            response_time_ms=interaction_data.response_time_ms,
            user_satisfaction=interaction_data.user_satisfaction,
            interaction_context=interaction_data.interaction_context,
            consent_level=interaction_data.consent_level
        )
        db.add(interaction)
        
        # Log engagement event if profile exists
        if profile_id:
            engagement_event = EngagementEvent(
                profile_id=profile_id,
                event_type="ivor_interaction",
                event_data={
                    "session_id": interaction_data.session_id,
                    "response_time_ms": interaction_data.response_time_ms,
                    "user_satisfaction": interaction_data.user_satisfaction
                },
                engagement_score_delta=5  # IVOR interaction = 5 points
            )
            db.add(engagement_event)
        
        db.commit()
        return {"message": "IVOR interaction stored successfully"}
        
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error storing IVOR interaction: {str(e)}"
        )

# Community Analytics (Privacy-compliant)
@router.get("/analytics/community-insights")
async def get_community_insights(
    weeks: int = 4,
    db: Session = Depends(get_db)
):
    """Get community insights respecting privacy preferences"""
    try:
        # Use the privacy-compliant view created in schema
        query = """
        SELECT * FROM community_insights 
        ORDER BY week DESC 
        LIMIT %s
        """
        
        result = db.execute(query, (weeks,)).fetchall()
        
        insights = []
        for row in result:
            insights.append({
                "week": row.week.isoformat(),
                "total_profiles": row.total_profiles,
                "engaged_members": row.engaged_members,
                "active_members": row.active_members,
                "committed_members": row.committed_members,
                "avg_engagement_score": float(row.avg_engagement_score) if row.avg_engagement_score else 0
            })
        
        return {"insights": insights}
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error getting community insights: {str(e)}"
        )

@router.get("/analytics/popular-pathways")
async def get_popular_pathways(db: Session = Depends(get_db)):
    """Get popular liberation pathways respecting privacy"""
    try:
        # Use the privacy-compliant view
        query = "SELECT * FROM popular_pathways ORDER BY pathway_count DESC LIMIT 10"
        result = db.execute(query).fetchall()
        
        pathways = []
        for row in result:
            pathways.append({
                "pathway": row.pathway,
                "pathway_count": row.pathway_count,
                "avg_scores": {
                    "identity": float(row.avg_identity_score) if row.avg_identity_score else 0,
                    "community": float(row.avg_community_score) if row.avg_community_score else 0,
                    "liberation": float(row.avg_liberation_score) if row.avg_liberation_score else 0,
                    "connection": float(row.avg_connection_score) if row.avg_connection_score else 0
                }
            })
        
        return {"pathways": pathways}
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error getting popular pathways: {str(e)}"
        )

# Engagement Events
@router.post("/engagement-event")
async def create_engagement_event(
    event_data: EngagementEventCreate,
    db: Session = Depends(get_db)
):
    """Log engagement event for analytics"""
    try:
        # Get profile
        profile = db.query(CommunityProfile).filter(
            CommunityProfile.email == event_data.email
        ).first()
        
        if not profile:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Profile not found"
            )
        
        # Create engagement event
        engagement_event = EngagementEvent(
            profile_id=profile.id,
            event_type=event_data.event_type,
            event_data=event_data.event_data,
            engagement_score_delta=event_data.engagement_score_delta
        )
        db.add(engagement_event)
        db.commit()
        
        return {"message": "Engagement event logged successfully"}
        
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error logging engagement event: {str(e)}"
        )
"""
SQLAlchemy models for BLKOUT community data integration
Privacy-first, liberation-centered data architecture
"""

from sqlalchemy import Column, String, Integer, DateTime, Boolean, Text, ARRAY, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid
from datetime import datetime

from core.database import Base

class CommunityProfile(Base):
    """Core community member profiles with unified identity"""
    __tablename__ = "community_profiles"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String(255), unique=True, nullable=False, index=True)
    name = Column(String(255), nullable=True)
    location = Column(String(255), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow)
    source = Column(String(50), nullable=False)  # 'email_capture', 'blkouthub', 'quiz', 'ivor'
    journey_stage = Column(String(50), default='new', index=True)  # 'new', 'engaged', 'active', 'committed'
    last_interaction = Column(DateTime, default=datetime.utcnow, index=True)
    engagement_score = Column(Integer, default=0)
    consent_preferences = Column(JSONB, default={
        "anonymous_only": True,
        "personal_service": False,
        "community_insights": False,
        "peer_connections": False
    })
    is_active = Column(Boolean, default=True)
    
    # Relationships
    email_subscriptions = relationship("EmailSubscription", back_populates="profile", cascade="all, delete-orphan")
    blkouthub_requests = relationship("BlkouthubRequest", back_populates="profile", cascade="all, delete-orphan")
    quiz_results = relationship("QuizResult", back_populates="profile", cascade="all, delete-orphan")
    ivor_interactions = relationship("IvorInteraction", back_populates="profile", cascade="all, delete-orphan")
    engagement_events = relationship("EngagementEvent", back_populates="profile", cascade="all, delete-orphan")
    consent_audits = relationship("ConsentAudit", back_populates="profile", cascade="all, delete-orphan")
    knowledge_contributions = relationship("KnowledgeContribution", back_populates="profile", cascade="all, delete-orphan")

class EmailSubscription(Base):
    """Email subscription preferences and tracking"""
    __tablename__ = "email_subscriptions"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    profile_id = Column(UUID(as_uuid=True), ForeignKey("community_profiles.id"), nullable=False, index=True)
    interests = Column(ARRAY(Text), nullable=False)
    source = Column(String(50), nullable=False)  # 'scrollytelling', 'homepage', 'quiz', 'direct'
    n8n_tracking_id = Column(String(100), nullable=True)
    engagement_level = Column(String(20), default='casual')  # 'casual', 'active', 'committed'
    blkouthub_interest = Column(Boolean, default=False)
    referrer = Column(String(500), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    consent_level = Column(String(50), default='anonymous_only')
    
    # Relationships
    profile = relationship("CommunityProfile", back_populates="email_subscriptions")

class BlkouthubRequest(Base):
    """BLKOUTHUB access requests and approval workflow"""
    __tablename__ = "blkouthub_requests"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    profile_id = Column(UUID(as_uuid=True), ForeignKey("community_profiles.id"), nullable=False, index=True)
    identity_affirmation = Column(ARRAY(Text), nullable=False)
    connection_reason = Column(Text, nullable=False)
    referral_source = Column(String(100), nullable=True)
    community_guidelines_agreed = Column(Boolean, default=False)
    status = Column(String(20), default='pending', index=True)  # 'pending', 'approved', 'rejected', 'invited'
    reviewed_by = Column(String(100), nullable=True)
    reviewed_at = Column(DateTime, nullable=True)
    invitation_sent_at = Column(DateTime, nullable=True)
    invitation_code = Column(String(50), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    consent_level = Column(String(50), default='personal_service')
    
    # Relationships
    profile = relationship("CommunityProfile", back_populates="blkouthub_requests")

class QuizResult(Base):
    """Liberation pathway quiz results and community matching"""
    __tablename__ = "quiz_results"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    profile_id = Column(UUID(as_uuid=True), ForeignKey("community_profiles.id"), nullable=True, index=True)
    pathway = Column(String(50), nullable=False, index=True)  # 'storyteller', 'organizer', 'community-builder', etc.
    pathway_title = Column(String(100), nullable=True)
    scores = Column(JSONB, nullable=False)  # Store all dimension scores
    answers = Column(JSONB, nullable=False)  # Store all quiz answers for analysis
    community_match = Column(String(100), nullable=True)
    next_steps = Column(ARRAY(Text), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    consent_level = Column(String(50), default='community_insights')
    
    # Relationships
    profile = relationship("CommunityProfile", back_populates="quiz_results")

class IvorInteraction(Base):
    """IVOR AI assistant conversation history and analytics"""
    __tablename__ = "ivor_interactions"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    profile_id = Column(UUID(as_uuid=True), ForeignKey("community_profiles.id"), nullable=True, index=True)  # NULL for anonymous
    session_id = Column(String(100), nullable=False, index=True)
    user_message = Column(Text, nullable=False)
    ivor_response = Column(Text, nullable=False)
    sources = Column(ARRAY(Text), nullable=True)  # Knowledge base sources used
    response_time_ms = Column(Integer, nullable=True)
    user_satisfaction = Column(Integer, nullable=True)  # 1-5 rating
    interaction_context = Column(JSONB, nullable=True)  # User context used for response
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    consent_level = Column(String(50), default='anonymous_only')
    
    # Relationships
    profile = relationship("CommunityProfile", back_populates="ivor_interactions")

class EngagementEvent(Base):
    """Community engagement event tracking and scoring"""
    __tablename__ = "engagement_events"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    profile_id = Column(UUID(as_uuid=True), ForeignKey("community_profiles.id"), nullable=False, index=True)
    event_type = Column(String(50), nullable=False, index=True)  # 'form_submission', 'ivor_chat', 'email_click', etc.
    event_data = Column(JSONB, nullable=True)
    engagement_score_delta = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    profile = relationship("CommunityProfile", back_populates="engagement_events")

class MonthlyReport(Base):
    """Monthly community reports and analytics"""
    __tablename__ = "monthly_reports"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    report_month = Column(DateTime, nullable=False, index=True)
    report_title = Column(String(255), nullable=False)
    report_content = Column(JSONB, nullable=False)
    visualizations = Column(JSONB, nullable=True)
    metadata = Column(JSONB, nullable=True)
    published_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

class ConsentAudit(Base):
    """User consent audit trail for transparency"""
    __tablename__ = "consent_audit"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    profile_id = Column(UUID(as_uuid=True), ForeignKey("community_profiles.id"), nullable=False, index=True)
    consent_type = Column(String(50), nullable=False)
    previous_value = Column(Boolean, nullable=True)
    new_value = Column(Boolean, nullable=True)
    changed_at = Column(DateTime, default=datetime.utcnow)
    change_reason = Column(String(255), nullable=True)
    
    # Relationships
    profile = relationship("CommunityProfile", back_populates="consent_audits")

class KnowledgeContribution(Base):
    """Community knowledge base contributions"""
    __tablename__ = "knowledge_contributions"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    profile_id = Column(UUID(as_uuid=True), ForeignKey("community_profiles.id"), nullable=True, index=True)
    contribution_type = Column(String(50), nullable=False)  # 'question', 'answer', 'resource', 'story'
    content = Column(Text, nullable=False)
    category = Column(String(100), nullable=True)
    is_public = Column(Boolean, default=False)
    attribution_name = Column(String(255), nullable=True)  # How contributor wants to be credited
    moderation_status = Column(String(20), default='pending')
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    profile = relationship("CommunityProfile", back_populates="knowledge_contributions")
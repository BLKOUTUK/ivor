"""
Pydantic schemas for BLKOUT community data integration
Privacy-first, liberation-centered data validation
"""

from pydantic import BaseModel, EmailStr, Field, validator
from typing import List, Optional, Dict, Any
from datetime import datetime
import uuid

# Base schemas
class CommunityProfileBase(BaseModel):
    email: EmailStr
    name: Optional[str] = None
    location: Optional[str] = None
    source: str = Field(..., regex="^(email_capture|blkouthub|quiz|ivor)$")
    journey_stage: str = Field(default="new", regex="^(new|engaged|active|committed)$")
    consent_preferences: Dict[str, bool] = Field(default={
        "anonymous_only": True,
        "personal_service": False,
        "community_insights": False,
        "peer_connections": False
    })

class CommunityProfileCreate(CommunityProfileBase):
    pass

class CommunityProfileResponse(CommunityProfileBase):
    id: uuid.UUID
    created_at: datetime
    updated_at: datetime
    last_interaction: datetime
    engagement_score: int
    is_active: bool
    
    class Config:
        orm_mode = True

# Email subscription schemas
class EmailSubscriptionBase(BaseModel):
    email: EmailStr
    interests: List[str]
    source: str = Field(..., regex="^(scrollytelling|homepage|quiz|direct)$")
    n8n_tracking_id: Optional[str] = None
    engagement_level: str = Field(default="casual", regex="^(casual|active|committed)$")
    blkouthub_interest: bool = False
    referrer: Optional[str] = None

class EmailSubscriptionCreate(EmailSubscriptionBase):
    pass

# BLKOUTHUB request schemas
class BlkouthubRequestBase(BaseModel):
    email: EmailStr
    name: Optional[str] = None
    location: Optional[str] = None
    identity_affirmation: List[str]
    connection_reason: str
    referral_source: Optional[str] = None
    community_guidelines_agreed: bool = False

class BlkouthubRequestCreate(BlkouthubRequestBase):
    @validator('identity_affirmation')
    def validate_identity_affirmation(cls, v):
        if not v or len(v) == 0:
            raise ValueError('Identity affirmation is required')
        return v
    
    @validator('connection_reason')
    def validate_connection_reason(cls, v):
        if not v or len(v.strip()) < 10:
            raise ValueError('Connection reason must be at least 10 characters')
        return v
    
    @validator('community_guidelines_agreed')
    def validate_guidelines_agreed(cls, v):
        if not v:
            raise ValueError('Community guidelines must be agreed to')
        return v

class BlkouthubRequestResponse(BlkouthubRequestBase):
    id: uuid.UUID
    status: str
    reviewed_by: Optional[str] = None
    reviewed_at: Optional[datetime] = None
    invitation_sent_at: Optional[datetime] = None
    invitation_code: Optional[str] = None
    created_at: datetime
    consent_level: str
    
    class Config:
        orm_mode = True

# Quiz result schemas
class QuizResultBase(BaseModel):
    email: Optional[EmailStr] = None
    name: Optional[str] = None
    location: Optional[str] = None
    pathway: str
    pathway_title: Optional[str] = None
    scores: Dict[str, int]
    answers: Dict[str, Any]
    community_match: Optional[str] = None
    next_steps: Optional[List[str]] = None

class QuizResultCreate(QuizResultBase):
    @validator('scores')
    def validate_scores(cls, v):
        required_dimensions = ['identity', 'community', 'liberation', 'connection']
        for dim in required_dimensions:
            if dim not in v:
                raise ValueError(f'Missing required score dimension: {dim}')
            if not isinstance(v[dim], int) or v[dim] < 1 or v[dim] > 5:
                raise ValueError(f'Score for {dim} must be an integer between 1 and 5')
        return v

class QuizResultResponse(QuizResultBase):
    id: uuid.UUID
    profile_id: Optional[uuid.UUID] = None
    created_at: datetime
    consent_level: str
    
    class Config:
        orm_mode = True

# IVOR interaction schemas
class IvorInteractionBase(BaseModel):
    email: Optional[EmailStr] = None
    session_id: str
    user_message: str
    ivor_response: str
    sources: Optional[List[str]] = None
    response_time_ms: Optional[int] = None
    user_satisfaction: Optional[int] = Field(None, ge=1, le=5)
    interaction_context: Optional[Dict[str, Any]] = None
    consent_level: str = Field(default="anonymous_only", regex="^(anonymous_only|personal_service|community_insights|peer_connections)$")

class IvorInteractionCreate(IvorInteractionBase):
    @validator('user_message')
    def validate_user_message(cls, v):
        if not v or len(v.strip()) < 1:
            raise ValueError('User message cannot be empty')
        return v
    
    @validator('ivor_response')
    def validate_ivor_response(cls, v):
        if not v or len(v.strip()) < 1:
            raise ValueError('IVOR response cannot be empty')
        return v

class IvorInteractionResponse(IvorInteractionBase):
    id: uuid.UUID
    profile_id: Optional[uuid.UUID] = None
    created_at: datetime
    
    class Config:
        orm_mode = True

# Engagement event schemas
class EngagementEventBase(BaseModel):
    email: EmailStr
    event_type: str
    event_data: Optional[Dict[str, Any]] = None
    engagement_score_delta: int = 0

class EngagementEventCreate(EngagementEventBase):
    @validator('event_type')
    def validate_event_type(cls, v):
        allowed_types = [
            'form_submission', 'ivor_chat', 'email_click', 'email_open',
            'quiz_completion', 'blkouthub_request', 'email_subscription',
            'page_view', 'resource_download', 'community_interaction'
        ]
        if v not in allowed_types:
            raise ValueError(f'Event type must be one of: {", ".join(allowed_types)}')
        return v

# Consent management schemas
class ConsentUpdate(BaseModel):
    consent_preferences: Dict[str, bool] = Field(..., description="Updated consent preferences")
    change_reason: Optional[str] = None
    
    @validator('consent_preferences')
    def validate_consent_preferences(cls, v):
        required_keys = ['anonymous_only', 'personal_service', 'community_insights', 'peer_connections']
        for key in required_keys:
            if key not in v:
                raise ValueError(f'Missing required consent key: {key}')
            if not isinstance(v[key], bool):
                raise ValueError(f'Consent value for {key} must be boolean')
        return v

class ConsentAuditResponse(BaseModel):
    id: uuid.UUID
    profile_id: uuid.UUID
    consent_type: str
    previous_value: Optional[bool]
    new_value: Optional[bool]
    changed_at: datetime
    change_reason: Optional[str]
    
    class Config:
        orm_mode = True

# Analytics schemas
class CommunityInsightsResponse(BaseModel):
    week: str
    total_profiles: int
    engaged_members: int
    active_members: int
    committed_members: int
    avg_engagement_score: float

class PopularPathwayResponse(BaseModel):
    pathway: str
    pathway_count: int
    avg_scores: Dict[str, float]

class AnalyticsResponse(BaseModel):
    insights: Optional[List[CommunityInsightsResponse]] = None
    pathways: Optional[List[PopularPathwayResponse]] = None

# Monthly report schemas
class MonthlyReportBase(BaseModel):
    report_month: datetime
    report_title: str
    report_content: Dict[str, Any]
    visualizations: Optional[Dict[str, Any]] = None
    metadata: Optional[Dict[str, Any]] = None

class MonthlyReportCreate(MonthlyReportBase):
    pass

class MonthlyReportResponse(MonthlyReportBase):
    id: uuid.UUID
    published_at: Optional[datetime] = None
    created_at: datetime
    
    class Config:
        orm_mode = True

# Knowledge contribution schemas
class KnowledgeContributionBase(BaseModel):
    contribution_type: str = Field(..., regex="^(question|answer|resource|story)$")
    content: str
    category: Optional[str] = None
    is_public: bool = False
    attribution_name: Optional[str] = None

class KnowledgeContributionCreate(KnowledgeContributionBase):
    email: Optional[EmailStr] = None
    
    @validator('content')
    def validate_content(cls, v):
        if not v or len(v.strip()) < 10:
            raise ValueError('Content must be at least 10 characters')
        return v

class KnowledgeContributionResponse(KnowledgeContributionBase):
    id: uuid.UUID
    profile_id: Optional[uuid.UUID] = None
    moderation_status: str
    created_at: datetime
    
    class Config:
        orm_mode = True

# Error response schemas
class ErrorResponse(BaseModel):
    detail: str
    error_code: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)

class SuccessResponse(BaseModel):
    message: str
    data: Optional[Dict[str, Any]] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)
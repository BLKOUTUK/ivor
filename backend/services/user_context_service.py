"""
User Context Service for IVOR
Privacy-first user context management with community-controlled personalization
"""

import logging
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import and_, desc, func

from models.community import (
    CommunityProfile, 
    EmailSubscription, 
    BlkouthubRequest, 
    QuizResult, 
    IvorInteraction,
    EngagementEvent
)
from services.consent_manager import consent_manager

logger = logging.getLogger(__name__)

class UserContextService:
    """Manages user context for personalized IVOR responses"""
    
    def __init__(self):
        self.context_cache = {}
        self.cache_ttl = 300  # 5 minutes
    
    async def get_user_context(
        self, 
        email: Optional[str], 
        session_id: str,
        db: Session
    ) -> Dict[str, Any]:
        """
        Get comprehensive user context for IVOR personalization
        Respects privacy consent levels
        """
        
        # Base context for anonymous users
        base_context = {
            "user_type": "anonymous",
            "personalization_level": "none",
            "consent_level": "anonymous_only",
            "session_id": session_id,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        if not email:
            return base_context
        
        # Check cache first
        cache_key = f"user_context:{email}"
        cached_context = self.context_cache.get(cache_key)
        if cached_context and cached_context.get("expires_at", 0) > datetime.utcnow().timestamp():
            return cached_context["data"]
        
        try:
            # Get user profile
            profile = db.query(CommunityProfile).filter(
                CommunityProfile.email == email
            ).first()
            
            if not profile:
                return base_context
            
            # Check consent level
            consent_level = consent_manager.get_effective_consent_level(profile.consent_preferences)
            
            # Build context based on consent level
            context = self._build_context_by_consent_level(
                profile, consent_level, session_id, db
            )
            
            # Cache the result
            self.context_cache[cache_key] = {
                "data": context,
                "expires_at": (datetime.utcnow() + timedelta(seconds=self.cache_ttl)).timestamp()
            }
            
            return context
            
        except Exception as e:
            logger.error(f"Error getting user context for {email}: {str(e)}")
            return base_context
    
    def _build_context_by_consent_level(
        self, 
        profile: CommunityProfile, 
        consent_level: str, 
        session_id: str,
        db: Session
    ) -> Dict[str, Any]:
        """Build user context based on consent level"""
        
        context = {
            "user_type": "community_member",
            "profile_id": str(profile.id),
            "email": profile.email,
            "consent_level": consent_level,
            "session_id": session_id,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        if consent_level == "anonymous_only":
            # Minimal anonymous context
            context.update({
                "personalization_level": "none",
                "journey_stage": "anonymous",
                "engagement_level": "minimal"
            })
            
        elif consent_level == "personal_service":
            # Personal service context
            context.update({
                "personalization_level": "personal",
                "journey_stage": profile.journey_stage,
                "engagement_score": profile.engagement_score,
                "member_since": profile.created_at.isoformat(),
                "last_interaction": profile.last_interaction.isoformat(),
                "conversation_history": self._get_recent_conversations(profile.id, db, limit=5)
            })
            
        elif consent_level == "community_insights":
            # Community insights context
            context.update({
                "personalization_level": "community_aware",
                "journey_stage": profile.journey_stage,
                "engagement_score": profile.engagement_score,
                "member_since": profile.created_at.isoformat(),
                "last_interaction": profile.last_interaction.isoformat(),
                "conversation_history": self._get_recent_conversations(profile.id, db, limit=10),
                "community_interests": self._get_community_interests(profile.id, db),
                "liberation_pathway": self._get_liberation_pathway(profile.id, db),
                "community_connections": self._get_community_patterns(profile.id, db)
            })
            
        elif consent_level == "peer_connections":
            # Full peer connection context
            context.update({
                "personalization_level": "peer_connected",
                "journey_stage": profile.journey_stage,
                "engagement_score": profile.engagement_score,
                "member_since": profile.created_at.isoformat(),
                "last_interaction": profile.last_interaction.isoformat(),
                "conversation_history": self._get_recent_conversations(profile.id, db, limit=20),
                "community_interests": self._get_community_interests(profile.id, db),
                "liberation_pathway": self._get_liberation_pathway(profile.id, db),
                "community_connections": self._get_community_patterns(profile.id, db),
                "peer_matches": self._get_peer_matches(profile.id, db),
                "blkouthub_status": self._get_blkouthub_status(profile.id, db)
            })
        
        return context
    
    def _get_recent_conversations(
        self, 
        profile_id: str, 
        db: Session, 
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """Get recent IVOR conversations for context"""
        
        conversations = db.query(IvorInteraction).filter(
            IvorInteraction.profile_id == profile_id
        ).order_by(desc(IvorInteraction.created_at)).limit(limit).all()
        
        return [{
            "user_message": conv.user_message[:100] + "..." if len(conv.user_message) > 100 else conv.user_message,
            "timestamp": conv.created_at.isoformat(),
            "satisfaction": conv.user_satisfaction,
            "topics": self._extract_topics(conv.user_message)
        } for conv in conversations]
    
    def _get_community_interests(self, profile_id: str, db: Session) -> List[str]:
        """Get user's community interests"""
        
        subscriptions = db.query(EmailSubscription).filter(
            EmailSubscription.profile_id == profile_id
        ).all()
        
        interests = []
        for sub in subscriptions:
            interests.extend(sub.interests)
        
        return list(set(interests))
    
    def _get_liberation_pathway(self, profile_id: str, db: Session) -> Optional[Dict[str, Any]]:
        """Get user's liberation pathway from quiz results"""
        
        quiz_result = db.query(QuizResult).filter(
            QuizResult.profile_id == profile_id
        ).order_by(desc(QuizResult.created_at)).first()
        
        if quiz_result:
            return {
                "pathway": quiz_result.pathway,
                "pathway_title": quiz_result.pathway_title,
                "scores": quiz_result.scores,
                "community_match": quiz_result.community_match,
                "next_steps": quiz_result.next_steps,
                "completed_at": quiz_result.created_at.isoformat()
            }
        
        return None
    
    def _get_community_patterns(self, profile_id: str, db: Session) -> Dict[str, Any]:
        """Get community interaction patterns"""
        
        # Get engagement events from last 30 days
        thirty_days_ago = datetime.utcnow() - timedelta(days=30)
        
        events = db.query(EngagementEvent).filter(
            and_(
                EngagementEvent.profile_id == profile_id,
                EngagementEvent.created_at >= thirty_days_ago
            )
        ).all()
        
        patterns = {
            "interaction_frequency": len(events),
            "preferred_interaction_types": {},
            "engagement_trend": "stable",
            "peak_activity_times": []
        }
        
        # Analyze interaction types
        for event in events:
            event_type = event.event_type
            patterns["preferred_interaction_types"][event_type] = patterns["preferred_interaction_types"].get(event_type, 0) + 1
        
        # Calculate engagement trend
        if len(events) > 1:
            recent_events = [e for e in events if e.created_at >= datetime.utcnow() - timedelta(days=7)]
            older_events = [e for e in events if e.created_at < datetime.utcnow() - timedelta(days=7)]
            
            if len(recent_events) > len(older_events):
                patterns["engagement_trend"] = "increasing"
            elif len(recent_events) < len(older_events):
                patterns["engagement_trend"] = "decreasing"
        
        return patterns
    
    def _get_peer_matches(self, profile_id: str, db: Session) -> List[Dict[str, Any]]:
        """Get potential peer matches based on similar pathways and interests"""
        
        # Get user's pathway
        user_pathway = db.query(QuizResult).filter(
            QuizResult.profile_id == profile_id
        ).order_by(desc(QuizResult.created_at)).first()
        
        if not user_pathway:
            return []
        
        # Find others with similar pathways
        similar_pathways = db.query(QuizResult).filter(
            and_(
                QuizResult.pathway == user_pathway.pathway,
                QuizResult.profile_id != profile_id,
                QuizResult.consent_level.in_(["community_insights", "peer_connections"])
            )
        ).limit(5).all()
        
        matches = []
        for pathway in similar_pathways:
            if pathway.profile:
                matches.append({
                    "pathway": pathway.pathway,
                    "community_match": pathway.community_match,
                    "similarity_score": self._calculate_similarity(user_pathway.scores, pathway.scores),
                    "member_since": pathway.profile.created_at.isoformat(),
                    "journey_stage": pathway.profile.journey_stage
                })
        
        return matches
    
    def _get_blkouthub_status(self, profile_id: str, db: Session) -> Optional[Dict[str, Any]]:
        """Get BLKOUTHUB access status"""
        
        request = db.query(BlkouthubRequest).filter(
            BlkouthubRequest.profile_id == profile_id
        ).order_by(desc(BlkouthubRequest.created_at)).first()
        
        if request:
            return {
                "status": request.status,
                "requested_at": request.created_at.isoformat(),
                "reviewed_at": request.reviewed_at.isoformat() if request.reviewed_at else None,
                "invitation_sent": request.invitation_sent_at is not None
            }
        
        return None
    
    def _extract_topics(self, message: str) -> List[str]:
        """Extract topics from user message"""
        
        # Simple keyword extraction
        community_keywords = {
            "housing": ["housing", "accommodation", "rent", "eviction", "homeless"],
            "mental_health": ["mental", "therapy", "depression", "anxiety", "counseling"],
            "employment": ["job", "work", "career", "employment", "unemployment"],
            "legal": ["legal", "lawyer", "court", "immigration", "visa"],
            "community": ["community", "event", "meetup", "group", "gathering"],
            "identity": ["identity", "coming out", "trans", "gender", "sexuality"],
            "liberation": ["liberation", "activism", "organizing", "justice", "rights"],
            "creative": ["creative", "art", "music", "writing", "expression"]
        }
        
        topics = []
        message_lower = message.lower()
        
        for topic, keywords in community_keywords.items():
            if any(keyword in message_lower for keyword in keywords):
                topics.append(topic)
        
        return topics
    
    def _calculate_similarity(self, scores1: Dict, scores2: Dict) -> float:
        """Calculate similarity between two pathway scores"""
        
        if not scores1 or not scores2:
            return 0.0
        
        # Simple cosine similarity
        dimensions = ["identity", "community", "liberation", "connection"]
        
        dot_product = 0
        norm1 = 0
        norm2 = 0
        
        for dim in dimensions:
            val1 = scores1.get(dim, 0)
            val2 = scores2.get(dim, 0)
            
            dot_product += val1 * val2
            norm1 += val1 ** 2
            norm2 += val2 ** 2
        
        if norm1 == 0 or norm2 == 0:
            return 0.0
        
        return dot_product / (norm1 ** 0.5 * norm2 ** 0.5)
    
    def get_personalization_prompts(self, context: Dict[str, Any]) -> List[str]:
        """Generate personalization prompts for IVOR based on user context"""
        
        prompts = []
        
        consent_level = context.get("consent_level", "anonymous_only")
        
        if consent_level == "anonymous_only":
            prompts.append("Provide general community information without personal references.")
        
        elif consent_level == "personal_service":
            journey_stage = context.get("journey_stage", "new")
            engagement_score = context.get("engagement_score", 0)
            
            prompts.append(f"User is in '{journey_stage}' stage of their community journey.")
            
            if engagement_score > 50:
                prompts.append("This is an actively engaged community member.")
            
            # Add conversation history context
            if context.get("conversation_history"):
                recent_topics = []
                for conv in context["conversation_history"][:3]:
                    recent_topics.extend(conv.get("topics", []))
                
                if recent_topics:
                    prompts.append(f"Recent conversation topics: {', '.join(set(recent_topics))}")
        
        elif consent_level == "community_insights":
            # Add pathway context
            pathway = context.get("liberation_pathway")
            if pathway:
                prompts.append(f"User's liberation pathway: {pathway['pathway']} - {pathway['pathway_title']}")
                prompts.append(f"Community match: {pathway['community_match']}")
            
            # Add interests
            interests = context.get("community_interests", [])
            if interests:
                prompts.append(f"User interests: {', '.join(interests)}")
        
        elif consent_level == "peer_connections":
            # Add peer connection context
            peer_matches = context.get("peer_matches", [])
            if peer_matches:
                prompts.append(f"User has {len(peer_matches)} potential peer matches in their pathway.")
            
            # Add BLKOUTHUB status
            blkouthub_status = context.get("blkouthub_status")
            if blkouthub_status:
                if blkouthub_status["status"] == "approved":
                    prompts.append("User has BLKOUTHUB access.")
                elif blkouthub_status["status"] == "pending":
                    prompts.append("User has pending BLKOUTHUB access request.")
        
        return prompts
    
    def clear_cache(self, email: Optional[str] = None):
        """Clear context cache for specific user or all users"""
        
        if email:
            cache_key = f"user_context:{email}"
            self.context_cache.pop(cache_key, None)
        else:
            self.context_cache.clear()
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        
        active_entries = 0
        expired_entries = 0
        current_time = datetime.utcnow().timestamp()
        
        for entry in self.context_cache.values():
            if entry.get("expires_at", 0) > current_time:
                active_entries += 1
            else:
                expired_entries += 1
        
        return {
            "total_entries": len(self.context_cache),
            "active_entries": active_entries,
            "expired_entries": expired_entries,
            "cache_hit_rate": "N/A"  # Would need separate tracking
        }

# Global instance
user_context_service = UserContextService()
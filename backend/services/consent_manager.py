"""
Consent Management Service for BLKOUT Community
Privacy-first, community-controlled consent handling
"""

import logging
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_

from models.community import CommunityProfile, ConsentAudit, EngagementEvent
from schemas.community import ConsentUpdate

logger = logging.getLogger(__name__)

class ConsentManager:
    """Manages community consent with privacy-first principles"""
    
    def __init__(self):
        self.consent_levels = {
            "anonymous_only": {
                "description": "Anonymous community analytics only",
                "data_usage": ["aggregated_stats", "community_trends", "usage_patterns"],
                "retention_days": 90,
                "anonymization": True
            },
            "personal_service": {
                "description": "Personalized service improvements",
                "data_usage": ["service_personalization", "user_preferences", "interaction_history"],
                "retention_days": 365,
                "anonymization": False
            },
            "community_insights": {
                "description": "Community intelligence and insights",
                "data_usage": ["community_analytics", "pathway_matching", "resource_recommendations"],
                "retention_days": 730,
                "anonymization": False
            },
            "peer_connections": {
                "description": "Peer-to-peer connections and mutual aid",
                "data_usage": ["peer_matching", "mutual_aid", "community_networking"],
                "retention_days": 1095,
                "anonymization": False
            }
        }
    
    def get_consent_level_info(self, level: str) -> Dict[str, Any]:
        """Get information about a consent level"""
        return self.consent_levels.get(level, {})
    
    def get_all_consent_levels(self) -> Dict[str, Dict[str, Any]]:
        """Get all available consent levels"""
        return self.consent_levels
    
    def validate_consent_preferences(self, preferences: Dict[str, bool]) -> bool:
        """Validate consent preferences structure"""
        required_keys = ["anonymous_only", "personal_service", "community_insights", "peer_connections"]
        
        # Check all required keys are present
        for key in required_keys:
            if key not in preferences:
                logger.warning(f"Missing consent key: {key}")
                return False
            if not isinstance(preferences[key], bool):
                logger.warning(f"Invalid consent value for {key}: must be boolean")
                return False
        
        # Validate logical consistency
        if not self.validate_consent_hierarchy(preferences):
            return False
        
        return True
    
    def validate_consent_hierarchy(self, preferences: Dict[str, bool]) -> bool:
        """Validate consent hierarchy logic"""
        # If anonymous_only is True, all others should be False
        if preferences.get("anonymous_only", False):
            for key in ["personal_service", "community_insights", "peer_connections"]:
                if preferences.get(key, False):
                    logger.warning(f"Invalid consent: anonymous_only=True but {key}=True")
                    return False
        
        # If peer_connections is True, community_insights should also be True
        if preferences.get("peer_connections", False):
            if not preferences.get("community_insights", False):
                logger.warning("Invalid consent: peer_connections=True but community_insights=False")
                return False
        
        return True
    
    def normalize_consent_preferences(self, preferences: Dict[str, bool]) -> Dict[str, bool]:
        """Normalize consent preferences to ensure consistency"""
        normalized = preferences.copy()
        
        # If anonymous_only is True, set all others to False
        if normalized.get("anonymous_only", False):
            normalized.update({
                "personal_service": False,
                "community_insights": False,
                "peer_connections": False
            })
        
        # If peer_connections is True, ensure community_insights is True
        if normalized.get("peer_connections", False):
            normalized["community_insights"] = True
            normalized["anonymous_only"] = False
        
        # If any higher level is True, set anonymous_only to False
        if any(normalized.get(key, False) for key in ["personal_service", "community_insights", "peer_connections"]):
            normalized["anonymous_only"] = False
        
        return normalized
    
    def get_effective_consent_level(self, preferences: Dict[str, bool]) -> str:
        """Get the highest effective consent level"""
        if preferences.get("peer_connections", False):
            return "peer_connections"
        elif preferences.get("community_insights", False):
            return "community_insights"
        elif preferences.get("personal_service", False):
            return "personal_service"
        else:
            return "anonymous_only"
    
    def can_use_data_for_purpose(self, preferences: Dict[str, bool], purpose: str) -> bool:
        """Check if data can be used for a specific purpose"""
        effective_level = self.get_effective_consent_level(preferences)
        level_info = self.consent_levels.get(effective_level, {})
        allowed_purposes = level_info.get("data_usage", [])
        
        return purpose in allowed_purposes
    
    def get_data_retention_period(self, preferences: Dict[str, bool]) -> int:
        """Get data retention period in days based on consent level"""
        effective_level = self.get_effective_consent_level(preferences)
        level_info = self.consent_levels.get(effective_level, {})
        return level_info.get("retention_days", 90)
    
    def should_anonymize_data(self, preferences: Dict[str, bool]) -> bool:
        """Check if data should be anonymized"""
        effective_level = self.get_effective_consent_level(preferences)
        level_info = self.consent_levels.get(effective_level, {})
        return level_info.get("anonymization", True)
    
    def update_consent_with_audit(
        self, 
        profile: CommunityProfile, 
        new_preferences: Dict[str, bool],
        change_reason: str,
        db: Session
    ) -> None:
        """Update consent preferences with full audit trail"""
        old_preferences = profile.consent_preferences
        
        # Normalize new preferences
        normalized_preferences = self.normalize_consent_preferences(new_preferences)
        
        # Create audit entries for all changes
        for consent_type in ["anonymous_only", "personal_service", "community_insights", "peer_connections"]:
            old_value = old_preferences.get(consent_type, False)
            new_value = normalized_preferences.get(consent_type, False)
            
            if old_value != new_value:
                audit_entry = ConsentAudit(
                    profile_id=profile.id,
                    consent_type=consent_type,
                    previous_value=old_value,
                    new_value=new_value,
                    change_reason=change_reason
                )
                db.add(audit_entry)
                
                logger.info(f"Consent change for {profile.email}: {consent_type} {old_value} -> {new_value}")
        
        # Update profile
        profile.consent_preferences = normalized_preferences
        profile.updated_at = datetime.utcnow()
        
        # Log engagement event
        engagement_event = EngagementEvent(
            profile_id=profile.id,
            event_type="consent_update",
            event_data={
                "old_preferences": old_preferences,
                "new_preferences": normalized_preferences,
                "change_reason": change_reason
            },
            engagement_score_delta=0  # No score change for consent updates
        )
        db.add(engagement_event)
    
    def get_consent_history(self, profile_id: str, db: Session) -> List[Dict[str, Any]]:
        """Get consent change history for a profile"""
        audits = db.query(ConsentAudit).filter(
            ConsentAudit.profile_id == profile_id
        ).order_by(ConsentAudit.changed_at.desc()).limit(50).all()
        
        history = []
        for audit in audits:
            history.append({
                "consent_type": audit.consent_type,
                "previous_value": audit.previous_value,
                "new_value": audit.new_value,
                "changed_at": audit.changed_at.isoformat(),
                "change_reason": audit.change_reason
            })
        
        return history
    
    def check_data_retention_compliance(self, db: Session) -> List[Dict[str, Any]]:
        """Check for profiles that need data retention compliance"""
        compliance_issues = []
        
        # Get all profiles
        profiles = db.query(CommunityProfile).filter(
            CommunityProfile.is_active == True
        ).all()
        
        for profile in profiles:
            retention_days = self.get_data_retention_period(profile.consent_preferences)
            cutoff_date = datetime.utcnow() - timedelta(days=retention_days)
            
            # Check if profile data is older than retention period
            if profile.created_at < cutoff_date and profile.last_interaction < cutoff_date:
                compliance_issues.append({
                    "profile_id": str(profile.id),
                    "email": profile.email,
                    "created_at": profile.created_at.isoformat(),
                    "last_interaction": profile.last_interaction.isoformat(),
                    "retention_days": retention_days,
                    "days_overdue": (datetime.utcnow() - cutoff_date).days,
                    "action_required": "anonymize_or_delete"
                })
        
        return compliance_issues
    
    def get_consent_statistics(self, db: Session) -> Dict[str, Any]:
        """Get community consent statistics"""
        total_profiles = db.query(CommunityProfile).filter(
            CommunityProfile.is_active == True
        ).count()
        
        stats = {
            "total_active_profiles": total_profiles,
            "consent_distribution": {},
            "consent_changes_last_30_days": {},
            "average_consent_level": 0
        }
        
        # Get consent distribution
        for level in ["anonymous_only", "personal_service", "community_insights", "peer_connections"]:
            count = db.query(CommunityProfile).filter(
                and_(
                    CommunityProfile.is_active == True,
                    CommunityProfile.consent_preferences[level].astext.cast(db.Boolean) == True
                )
            ).count()
            
            stats["consent_distribution"][level] = {
                "count": count,
                "percentage": (count / total_profiles * 100) if total_profiles > 0 else 0
            }
        
        # Get consent changes in last 30 days
        thirty_days_ago = datetime.utcnow() - timedelta(days=30)
        recent_changes = db.query(ConsentAudit).filter(
            ConsentAudit.changed_at >= thirty_days_ago
        ).all()
        
        for change in recent_changes:
            consent_type = change.consent_type
            if consent_type not in stats["consent_changes_last_30_days"]:
                stats["consent_changes_last_30_days"][consent_type] = {
                    "increases": 0,
                    "decreases": 0,
                    "total_changes": 0
                }
            
            stats["consent_changes_last_30_days"][consent_type]["total_changes"] += 1
            
            if change.previous_value == False and change.new_value == True:
                stats["consent_changes_last_30_days"][consent_type]["increases"] += 1
            elif change.previous_value == True and change.new_value == False:
                stats["consent_changes_last_30_days"][consent_type]["decreases"] += 1
        
        return stats
    
    def get_privacy_dashboard_data(self, profile_id: str, db: Session) -> Dict[str, Any]:
        """Get privacy dashboard data for a specific profile"""
        profile = db.query(CommunityProfile).filter(
            CommunityProfile.id == profile_id
        ).first()
        
        if not profile:
            return {}
        
        effective_level = self.get_effective_consent_level(profile.consent_preferences)
        level_info = self.consent_levels.get(effective_level, {})
        
        return {
            "profile_id": str(profile.id),
            "email": profile.email,
            "current_consent_level": effective_level,
            "consent_preferences": profile.consent_preferences,
            "level_info": level_info,
            "data_retention_days": self.get_data_retention_period(profile.consent_preferences),
            "data_anonymization": self.should_anonymize_data(profile.consent_preferences),
            "last_consent_change": profile.updated_at.isoformat(),
            "consent_history": self.get_consent_history(profile_id, db),
            "data_usage_permissions": level_info.get("data_usage", [])
        }

# Global consent manager instance
consent_manager = ConsentManager()
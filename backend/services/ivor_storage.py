"""
IVOR Storage Service - Handles conversation storage
Privacy-first conversation persistence
"""

import logging
from typing import Dict, Any, Optional
from datetime import datetime
from sqlalchemy.orm import Session

from models.community import CommunityProfile, IvorInteraction
from schemas.community import IvorInteractionCreate

logger = logging.getLogger(__name__)

class IvorStorageService:
    """Service for storing IVOR conversations"""
    
    @staticmethod
    async def store_interaction(
        interaction_data: Dict[str, Any],
        db: Session
    ) -> Dict[str, Any]:
        """Store IVOR interaction in database"""
        
        try:
            profile_id = None
            
            # Link to profile if email provided and consent given
            if interaction_data.get("email") and interaction_data.get("consent_level") != "anonymous_only":
                profile = db.query(CommunityProfile).filter(
                    CommunityProfile.email == interaction_data["email"]
                ).first()
                
                if profile:
                    profile_id = profile.id
            
            # Create interaction record
            interaction = IvorInteraction(
                profile_id=profile_id,
                session_id=interaction_data["session_id"],
                user_message=interaction_data["user_message"],
                ivor_response=interaction_data["ivor_response"],
                sources=interaction_data.get("sources", []),
                response_time_ms=interaction_data.get("response_time_ms"),
                user_satisfaction=interaction_data.get("user_satisfaction"),
                interaction_context=interaction_data.get("interaction_context"),
                consent_level=interaction_data.get("consent_level", "anonymous_only")
            )
            
            db.add(interaction)
            db.commit()
            
            return {
                "success": True,
                "interaction_id": str(interaction.id),
                "profile_id": str(profile_id) if profile_id else None
            }
            
        except Exception as e:
            logger.error(f"Error storing IVOR interaction: {str(e)}")
            db.rollback()
            return {
                "success": False,
                "error": str(e)
            }

# Global service instance
ivor_storage_service = IvorStorageService()
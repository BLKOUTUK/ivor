"""
Events endpoints for IVOR Backend - Calendar integration
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
import httpx
import logging

from core.config import settings

logger = logging.getLogger(__name__)
router = APIRouter()

class Event(BaseModel):
    id: str
    title: str
    description: str
    start_time: datetime
    end_time: datetime
    location: Optional[str] = None
    registration_url: Optional[str] = None
    category: Optional[str] = None

class EventsResponse(BaseModel):
    events: List[Event]
    total: int
    message: str

@router.get("/upcoming", response_model=EventsResponse)
async def get_upcoming_events(
    limit: int = 10,
    days_ahead: int = 30
) -> EventsResponse:
    """Get upcoming community events"""
    
    try:
        # For MVP, return mock events
        # In production, this would connect to the actual calendar API
        
        mock_events = [
            Event(
                id="coop-workshop-001",
                title="Cooperative Development Workshop",
                description="Learn the basics of starting a worker cooperative, including legal structures, governance, and financing options.",
                start_time=datetime.now() + timedelta(days=3, hours=18),
                end_time=datetime.now() + timedelta(days=3, hours=20),
                location="Community Hub, 123 Community St",
                registration_url="https://example.com/register/coop-workshop",
                category="education"
            ),
            Event(
                id="community-gathering-001",
                title="Monthly Community Gathering",
                description="Join us for our monthly community gathering where we share updates, connect with each other, and plan future initiatives.",
                start_time=datetime.now() + timedelta(days=7, hours=19),
                end_time=datetime.now() + timedelta(days=7, hours=21),
                location="Online and In-Person",
                registration_url="https://example.com/register/community-gathering",
                category="community"
            ),
            Event(
                id="skill-share-001",
                title="Financial Planning for Cooperatives",
                description="Community member Sarah shares her expertise in financial planning specifically for cooperative businesses.",
                start_time=datetime.now() + timedelta(days=14, hours=17),
                end_time=datetime.now() + timedelta(days=14, hours=18, minutes=30),
                location="Online",
                registration_url="https://example.com/register/financial-planning",
                category="skill-share"
            ),
            Event(
                id="social-event-001",
                title="Community Potluck & Social",
                description="Bring a dish to share and join us for an informal community social event. Great opportunity to meet new people!",
                start_time=datetime.now() + timedelta(days=21, hours=18),
                end_time=datetime.now() + timedelta(days=21, hours=21),
                location="Community Garden, 456 Garden Ave",
                registration_url="https://example.com/register/potluck",
                category="social"
            )
        ]
        
        # Filter events within the specified timeframe
        cutoff_date = datetime.now() + timedelta(days=days_ahead)
        filtered_events = [
            event for event in mock_events 
            if event.start_time <= cutoff_date
        ][:limit]
        
        return EventsResponse(
            events=filtered_events,
            total=len(filtered_events),
            message=f"Found {len(filtered_events)} upcoming events in the next {days_ahead} days"
        )
        
    except Exception as e:
        logger.error(f"Failed to fetch events: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Failed to fetch upcoming events"
        )

@router.get("/search")
async def search_events(
    query: str,
    limit: int = 5
) -> EventsResponse:
    """Search events by query"""
    
    try:
        # Get all upcoming events
        all_events_response = await get_upcoming_events(limit=50, days_ahead=90)
        all_events = all_events_response.events
        
        # Simple text search in title and description
        query_lower = query.lower()
        matching_events = [
            event for event in all_events
            if (query_lower in event.title.lower() or 
                query_lower in event.description.lower() or
                query_lower in (event.category or "").lower())
        ][:limit]
        
        return EventsResponse(
            events=matching_events,
            total=len(matching_events),
            message=f"Found {len(matching_events)} events matching '{query}'"
        )
        
    except Exception as e:
        logger.error(f"Failed to search events: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Failed to search events"
        )

@router.get("/categories")
async def get_event_categories() -> Dict[str, List[str]]:
    """Get available event categories"""
    
    return {
        "categories": [
            "education",
            "community", 
            "skill-share",
            "social",
            "workshop",
            "meeting",
            "fundraising",
            "advocacy"
        ]
    }

@router.get("/{event_id}")
async def get_event_details(event_id: str) -> Event:
    """Get details for a specific event"""
    
    try:
        # Get all events and find the specific one
        all_events_response = await get_upcoming_events(limit=100, days_ahead=365)
        
        for event in all_events_response.events:
            if event.id == event_id:
                return event
        
        raise HTTPException(
            status_code=404,
            detail=f"Event with ID {event_id} not found"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get event details: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Failed to get event details"
        )
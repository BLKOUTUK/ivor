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
    """Get upcoming community events from Events Calendar API"""
    
    try:
        # Connect to Events Calendar API
        events_calendar_url = settings.EVENTS_CALENDAR_API_URL
        
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(
                f"{events_calendar_url}/api/events/upcoming",
                params={"limit": limit}
            )
            
            if response.status_code == 200:
                calendar_data = response.json()
                calendar_events = calendar_data.get("events", [])
                
                # Transform calendar events to IVOR format
                ivor_events = []
                for event_data in calendar_events:
                    # Parse date and time
                    event_date = event_data.get("date", "")
                    event_time = event_data.get("time", "19:00")
                    
                    try:
                        start_time = datetime.fromisoformat(f"{event_date}T{event_time}:00")
                        end_time = start_time + timedelta(hours=2)  # Default 2-hour duration
                    except:
                        start_time = datetime.now() + timedelta(days=7)
                        end_time = start_time + timedelta(hours=2)
                    
                    # Only include events within the timeframe
                    cutoff_date = datetime.now() + timedelta(days=days_ahead)
                    if start_time <= cutoff_date:
                        ivor_events.append(Event(
                            id=event_data.get("id", ""),
                            title=event_data.get("title", ""),
                            description=event_data.get("description", ""),
                            start_time=start_time,
                            end_time=end_time,
                            location=event_data.get("location"),
                            registration_url=event_data.get("event_url"),
                            category=event_data.get("category"),
                            organizer_name=event_data.get("organizer_name"),
                            price=event_data.get("price"),
                            tags=event_data.get("tags", []),
                            source="events_calendar",
                            relevance_score=event_data.get("relevance_score")
                        ))
                
                return EventsResponse(
                    events=ivor_events,
                    total=len(ivor_events),
                    message=f"Found {len(ivor_events)} upcoming events from Events Calendar"
                )
            
            else:
                logger.warning(f"Events Calendar API returned status {response.status_code}")
                # Fallback to mock events
                return await get_fallback_events(limit, days_ahead)
                
    except httpx.TimeoutException:
        logger.error("Events Calendar API timeout")
        return await get_fallback_events(limit, days_ahead)
    except Exception as e:
        logger.error(f"Failed to fetch events from Calendar API: {str(e)}")
        return await get_fallback_events(limit, days_ahead)

async def get_fallback_events(limit: int = 10, days_ahead: int = 30) -> EventsResponse:
    """Fallback mock events when Events Calendar API is unavailable"""
    
    mock_events = [
        Event(
            id="coop-workshop-001",
            title="Cooperative Development Workshop",
            description="Learn the basics of starting a worker cooperative, including legal structures, governance, and financing options.",
            start_time=datetime.now() + timedelta(days=3, hours=18),
            end_time=datetime.now() + timedelta(days=3, hours=20),
            location="Community Hub, 123 Community St",
            registration_url="https://example.com/register/coop-workshop",
            category="education",
            organizer_name="BLKOUT Cooperative Network",
            source="fallback"
        ),
        Event(
            id="community-gathering-001",
            title="Monthly Community Gathering",
            description="Join us for our monthly community gathering where we share updates, connect with each other, and plan future initiatives.",
            start_time=datetime.now() + timedelta(days=7, hours=19),
            end_time=datetime.now() + timedelta(days=7, hours=21),
            location="Online and In-Person",
            registration_url="https://example.com/register/community-gathering",
            category="community",
            organizer_name="BLKOUT Community",
            source="fallback"
        ),
        Event(
            id="skill-share-001",
            title="Financial Planning for Cooperatives",
            description="Community member Sarah shares her expertise in financial planning specifically for cooperative businesses.",
            start_time=datetime.now() + timedelta(days=14, hours=17),
            end_time=datetime.now() + timedelta(days=14, hours=18, minutes=30),
            location="Online",
            registration_url="https://example.com/register/financial-planning",
            category="skill-share",
            organizer_name="Community Finance Network",
            source="fallback"
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
        message=f"Found {len(filtered_events)} events (fallback mode - Events Calendar API unavailable)"
    )

@router.get("/search")
async def search_events(
    query: str,
    limit: int = 5
) -> EventsResponse:
    """Search events by query via Events Calendar API"""
    
    try:
        # Try Events Calendar API first
        events_calendar_url = settings.EVENTS_CALENDAR_API_URL
        
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(
                f"{events_calendar_url}/api/events/search",
                params={"q": query, "limit": limit}
            )
            
            if response.status_code == 200:
                calendar_data = response.json()
                calendar_events = calendar_data.get("events", [])
                
                # Transform calendar events to IVOR format
                ivor_events = []
                for event_data in calendar_events:
                    # Parse date and time
                    event_date = event_data.get("date", "")
                    event_time = event_data.get("time", "19:00")
                    
                    try:
                        start_time = datetime.fromisoformat(f"{event_date}T{event_time}:00")
                        end_time = start_time + timedelta(hours=2)
                    except:
                        start_time = datetime.now() + timedelta(days=7)
                        end_time = start_time + timedelta(hours=2)
                    
                    ivor_events.append(Event(
                        id=event_data.get("id", ""),
                        title=event_data.get("title", ""),
                        description=event_data.get("description", ""),
                        start_time=start_time,
                        end_time=end_time,
                        location=event_data.get("location"),
                        registration_url=event_data.get("event_url"),
                        category=event_data.get("category"),
                        organizer_name=event_data.get("organizer_name"),
                        price=event_data.get("price"),
                        tags=event_data.get("tags", []),
                        source="events_calendar",
                        relevance_score=event_data.get("relevance_score")
                    ))
                
                return EventsResponse(
                    events=ivor_events,
                    total=len(ivor_events),
                    message=f"Found {len(ivor_events)} events matching '{query}' from Events Calendar"
                )
        
        # Fallback to local search
        all_events_response = await get_fallback_events(limit=50, days_ahead=90)
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
            message=f"Found {len(matching_events)} events matching '{query}' (fallback mode)"
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
#!/usr/bin/env python3
"""
Test script for IVOR Events Calendar integration
"""

import asyncio
import httpx
import json
from datetime import datetime

async def test_integration():
    """Test the full integration between Events Calendar API and IVOR backend"""
    
    print("🧪 Testing IVOR Events Calendar Integration\n")
    
    # Test 1: Events Calendar API Health
    print("1️⃣ Testing Events Calendar API Health...")
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get("http://localhost:3001/api/health")
            if response.status_code == 200:
                health_data = response.json()
                print(f"   ✅ Events Calendar API: {health_data['status']}")
                print(f"   📊 Events available: {health_data['events_count']}")
            else:
                print(f"   ❌ Events Calendar API unhealthy: {response.status_code}")
                return False
    except Exception as e:
        print(f"   ❌ Events Calendar API not accessible: {e}")
        return False
    
    # Test 2: Events Calendar API Endpoints
    print("\n2️⃣ Testing Events Calendar API Endpoints...")
    endpoints = [
        ("upcoming", "/api/events/upcoming?limit=2"),
        ("search", "/api/events/search?q=workshop&limit=2"),
        ("categories", "/api/events/categories")
    ]
    
    calendar_data = {}
    for name, endpoint in endpoints:
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(f"http://localhost:3001{endpoint}")
                if response.status_code == 200:
                    data = response.json()
                    calendar_data[name] = data
                    if name == "upcoming":
                        print(f"   ✅ Upcoming events: {data.get('total', 0)} found")
                    elif name == "search":
                        print(f"   ✅ Search events: {data.get('total', 0)} found")
                    elif name == "categories":
                        print(f"   ✅ Categories: {len(data.get('categories', []))} available")
                else:
                    print(f"   ❌ {name.title()} endpoint failed: {response.status_code}")
        except Exception as e:
            print(f"   ❌ {name.title()} endpoint error: {e}")
    
    # Test 3: IVOR Backend Integration
    print("\n3️⃣ Testing IVOR Backend Integration...")
    
    # Check if IVOR backend is running and can connect to Events Calendar
    ivor_endpoints = [
        ("health", "/health/"),
        ("events_upcoming", "/events/upcoming?limit=3"),
        ("events_search", "/events/search?query=community&limit=2")
    ]
    
    for name, endpoint in ivor_endpoints:
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(f"http://localhost:8000{endpoint}")
                if response.status_code == 200:
                    data = response.json()
                    if name == "health":
                        print(f"   ✅ IVOR Backend: {data.get('status', 'unknown')}")
                    elif name == "events_upcoming":
                        events = data.get('events', [])
                        message = data.get('message', '')
                        print(f"   ✅ IVOR Events: {len(events)} events")
                        print(f"      📝 Response: {message}")
                        
                        # Check if data comes from Events Calendar
                        if events and any(event.get('source') == 'events_calendar' for event in events):
                            print(f"      🔗 Integration: Successfully connected to Events Calendar")
                        else:
                            print(f"      ⚠️  Integration: Using fallback data (Calendar API might be unavailable)")
                            
                    elif name == "events_search":
                        events = data.get('events', [])
                        message = data.get('message', '')
                        print(f"   ✅ IVOR Search: {len(events)} results")
                        print(f"      📝 Response: {message}")
                else:
                    print(f"   ❌ IVOR {name} endpoint failed: {response.status_code}")
        except Exception as e:
            print(f"   ❌ IVOR {name} endpoint error: {e}")
    
    # Test 4: Data Flow Validation
    print("\n4️⃣ Testing Data Flow Validation...")
    
    try:
        # Get data from Events Calendar directly
        async with httpx.AsyncClient() as client:
            calendar_response = await client.get("http://localhost:3001/api/events/upcoming?limit=1")
            calendar_data = calendar_response.json() if calendar_response.status_code == 200 else {}
            
            # Get data from IVOR (which should consume Events Calendar)
            ivor_response = await client.get("http://localhost:8000/events/upcoming?limit=1")
            ivor_data = ivor_response.json() if ivor_response.status_code == 200 else {}
            
            calendar_events = calendar_data.get('events', [])
            ivor_events = ivor_data.get('events', [])
            
            if calendar_events and ivor_events:
                calendar_event = calendar_events[0]
                ivor_event = ivor_events[0]
                
                print(f"   📊 Calendar Event: {calendar_event.get('title', 'N/A')}")
                print(f"   📊 IVOR Event: {ivor_event.get('title', 'N/A')}")
                
                # Check if event titles match (indicating successful integration)
                if calendar_event.get('title') == ivor_event.get('title'):
                    print(f"   ✅ Data Flow: Events match! Integration successful")
                else:
                    print(f"   ⚠️  Data Flow: Events differ (IVOR might be using fallback)")
            else:
                print(f"   ❌ Data Flow: Missing events data")
                
    except Exception as e:
        print(f"   ❌ Data Flow validation error: {e}")
    
    # Test 5: Chat Integration
    print("\n5️⃣ Testing Chat Integration...")
    
    try:
        async with httpx.AsyncClient() as client:
            chat_response = await client.post(
                "http://localhost:8000/chat/message",
                json={
                    "message": "What events are happening this week?",
                    "session_id": "integration-test"
                }
            )
            
            if chat_response.status_code == 200:
                chat_data = chat_response.json()
                message = chat_data.get('message', '')
                print(f"   ✅ Chat Response: {len(message)} characters")
                
                # Check if response mentions events
                if any(keyword in message.lower() for keyword in ['event', 'workshop', 'community', 'celebration']):
                    print(f"   🔗 Chat Integration: Response includes event information")
                else:
                    print(f"   ⚠️  Chat Integration: Response might not include event data")
            else:
                print(f"   ❌ Chat endpoint failed: {chat_response.status_code}")
                
    except Exception as e:
        print(f"   ❌ Chat integration error: {e}")
    
    print(f"\n🎯 Integration Test Complete!")
    print(f"💡 Next Steps:")
    print(f"   1. Ensure both servers are running simultaneously")
    print(f"   2. Test frontend integration with IVOR chatbot")
    print(f"   3. Deploy both services to production")

if __name__ == "__main__":
    asyncio.run(test_integration())
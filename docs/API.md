# IVOR API Reference

Complete API documentation for IVOR backend services.

---

## Base URL

- **Development**: `http://localhost:8000`
- **Production**: `https://your-domain.com`

---

## Authentication

IVOR currently operates without authentication for community accessibility. All endpoints are public.

---

## Endpoints

### Health Checks

#### `GET /health/`
Basic health check endpoint.

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2025-07-03T12:00:00Z",
  "service": "IVOR Backend",
  "version": "1.0.0"
}
```

#### `GET /health/detailed`
Detailed health check with system information.

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2025-07-03T12:00:00Z",
  "service": "IVOR Backend",
  "version": "1.0.0",
  "system": {
    "cpu_percent": 25.5,
    "memory": {
      "total": 8589934592,
      "available": 6442450944,
      "percent": 25.0
    },
    "disk": {
      "total": 1000000000000,
      "free": 500000000000,
      "percent": 50.0
    }
  },
  "services": {
    "ai_service": "operational",
    "knowledge_base": "operational",
    "database": "operational"
  }
}
```

---

### Chat

#### `POST /chat/message`
Send a message to IVOR and receive an AI response.

**Request Body:**
```json
{
  "message": "What is BLKOUT about?",
  "session_id": "optional-session-id",
  "context": {
    "page": "homepage",
    "user_interests": ["cooperatives"]
  }
}
```

**Response:**
```json
{
  "message": "BLKOUT is a community focused on...",
  "sources": [
    {
      "title": "BLKOUT Core Values",
      "source": "community_handbook",
      "url": "https://example.com/values"
    }
  ],
  "suggestions": [
    "Tell me more about cooperative ownership",
    "What events are coming up?",
    "How can I get involved?"
  ],
  "timestamp": "2025-07-03T12:00:00Z",
  "model_used": "deepseek-chat",
  "confidence": 0.9,
  "session_id": "generated-or-provided-session-id"
}
```

#### `GET /chat/suggestions`
Get conversation starter suggestions.

**Response:**
```json
{
  "suggestions": [
    "What's happening in the community this week?",
    "How do I get started with cooperative ownership?",
    "Tell me about BLKOUT's values and approach",
    "I'm interested in connecting with other community members",
    "What events are coming up?",
    "How can I contribute to the community?",
    "What resources are available for starting a cooperative?",
    "Tell me about Black queer liberation and economic alternatives"
  ]
}
```

---

### Events

#### `GET /events/upcoming`
Get upcoming community events.

**Query Parameters:**
- `limit` (optional): Number of events to return (default: 10)
- `days_ahead` (optional): Number of days to look ahead (default: 30)

**Example:** `GET /events/upcoming?limit=5&days_ahead=14`

**Response:**
```json
{
  "events": [
    {
      "id": "coop-workshop-001",
      "title": "Cooperative Development Workshop",
      "description": "Learn the basics of starting a worker cooperative...",
      "start_time": "2025-07-06T18:00:00Z",
      "end_time": "2025-07-06T20:00:00Z",
      "location": "Community Hub, 123 Community St",
      "registration_url": "https://example.com/register/coop-workshop",
      "category": "education"
    }
  ],
  "total": 1,
  "message": "Found 1 upcoming events in the next 30 days"
}
```

#### `GET /events/search`
Search events by query string.

**Query Parameters:**
- `query` (required): Search term
- `limit` (optional): Number of results (default: 5)

**Example:** `GET /events/search?query=cooperative&limit=3`

**Response:**
```json
{
  "events": [
    {
      "id": "coop-workshop-001",
      "title": "Cooperative Development Workshop",
      "description": "Learn the basics of starting a worker cooperative...",
      "start_time": "2025-07-06T18:00:00Z",
      "end_time": "2025-07-06T20:00:00Z",
      "location": "Community Hub, 123 Community St",
      "registration_url": "https://example.com/register/coop-workshop",
      "category": "education"
    }
  ],
  "total": 1,
  "message": "Found 1 events matching 'cooperative'"
}
```

#### `GET /events/categories`
Get available event categories.

**Response:**
```json
{
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
```

#### `GET /events/{event_id}`
Get details for a specific event.

**Response:**
```json
{
  "id": "coop-workshop-001",
  "title": "Cooperative Development Workshop",
  "description": "Learn the basics of starting a worker cooperative, including legal structures, governance, and financing options.",
  "start_time": "2025-07-06T18:00:00Z",
  "end_time": "2025-07-06T20:00:00Z",
  "location": "Community Hub, 123 Community St",
  "registration_url": "https://example.com/register/coop-workshop",
  "category": "education"
}
```

---

## WebSocket

### Connection: `ws://localhost:8000/ws`

Real-time chat interface for immediate responses.

#### Send Message
```json
{
  "message": "Hello IVOR!",
  "session_id": "user-session-123",
  "context": {
    "page": "homepage"
  }
}
```

#### Receive Response
```json
{
  "type": "response",
  "message": "Hello! I'm IVOR, BLKOUT's community AI...",
  "sources": [...],
  "suggestions": [...],
  "timestamp": "2025-07-03T12:00:00Z"
}
```

---

## Error Handling

### Error Response Format
```json
{
  "detail": "Error message description",
  "error_code": "SPECIFIC_ERROR_CODE",
  "timestamp": "2025-07-03T12:00:00Z"
}
```

### Common HTTP Status Codes

- **200**: Success
- **400**: Bad Request - Invalid input
- **404**: Not Found - Resource doesn't exist
- **429**: Too Many Requests - Rate limited
- **500**: Internal Server Error - Server issue

### WebSocket Error Handling

Connection errors are handled gracefully with automatic reconnection attempts. If WebSocket fails, the frontend falls back to HTTP API.

---

## Rate Limiting

- **Chat Messages**: 60 requests per minute per session
- **Events API**: 100 requests per minute per IP
- **Health Checks**: Unlimited

---

## Response Times

- **Chat Messages**: < 3 seconds
- **Event Queries**: < 500ms
- **Health Checks**: < 100ms
- **WebSocket**: Real-time (< 100ms overhead)

---

## Data Models

### Message Object
```typescript
interface Message {
  id: string
  text: string
  sender: 'user' | 'ivor'
  timestamp: Date
  sources?: Source[]
  suggestions?: string[]
  modelUsed?: string
}
```

### Source Object
```typescript
interface Source {
  title: string
  source: string
  url?: string
  relevance?: number
}
```

### Event Object
```typescript
interface Event {
  id: string
  title: string
  description: string
  start_time: Date
  end_time: Date
  location?: string
  registration_url?: string
  category?: string
}
```

---

## SDK Examples

### JavaScript/TypeScript

```typescript
// Send chat message
const response = await fetch('http://localhost:8000/chat/message', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    message: 'What is cooperative ownership?',
    session_id: 'user-123'
  })
})
const data = await response.json()

// WebSocket connection
const ws = new WebSocket('ws://localhost:8000/ws')
ws.onmessage = (event) => {
  const response = JSON.parse(event.data)
  console.log('IVOR:', response.message)
}
```

### Python

```python
import httpx
import json

# Send chat message
async with httpx.AsyncClient() as client:
    response = await client.post(
        'http://localhost:8000/chat/message',
        json={
            'message': 'What is cooperative ownership?',
            'session_id': 'user-123'
        }
    )
    data = response.json()
    print(data['message'])
```

### cURL

```bash
# Send chat message
curl -X POST http://localhost:8000/chat/message \
  -H "Content-Type: application/json" \
  -d '{"message": "What is cooperative ownership?"}'

# Get upcoming events
curl http://localhost:8000/events/upcoming?limit=5
```

---

## Interactive Documentation

When the server is running, visit:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

These provide interactive API exploration and testing capabilities.
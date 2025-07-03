# IVOR Backend

Community AI Assistant for BLKOUT - FastAPI backend with DeepSeek integration and ChromaDB knowledge base.

## Quick Start

1. **Environment Setup**
   ```bash
   cp .env.example .env
   # Edit .env with your API keys
   ```

2. **Local Development**
   ```bash
   pip install -r requirements.txt
   uvicorn main:app --reload --port 8000
   ```

3. **Docker Development**
   ```bash
   docker-compose up --build
   ```

## Configuration

### Required Environment Variables

- `DEEPSEEK_API_KEY`: Your DeepSeek API key
- `OPENAI_API_KEY`: OpenAI API key for embeddings
- `DATABASE_URL`: PostgreSQL connection string
- `REDIS_URL`: Redis connection string

### Optional Environment Variables

- `QWEN_API_KEY`: Qwen API key (fallback LLM)
- `DEBUG`: Enable debug mode (default: False)
- `LOG_LEVEL`: Logging level (default: INFO)

## API Endpoints

### Health Checks
- `GET /health/` - Basic health check
- `GET /health/detailed` - Detailed system health

### Chat
- `POST /chat/message` - Send message to IVOR
- `GET /chat/suggestions` - Get conversation starters
- `WS /ws` - WebSocket chat connection

### Events
- `GET /events/upcoming` - Get upcoming events
- `GET /events/search?query=...` - Search events
- `GET /events/{event_id}` - Get event details

## Architecture

### AI Integration
- **Primary LLM**: DeepSeek (cost-optimized)
- **Fallback LLM**: Qwen (ultra-low cost)
- **Embeddings**: OpenAI ada-002
- **Knowledge Base**: ChromaDB with semantic search

### Tech Stack
- **API Framework**: FastAPI
- **Database**: PostgreSQL + Redis
- **Vector DB**: ChromaDB (self-hosted)
- **AI Models**: DeepSeek, Qwen, OpenAI

## Development

### Testing the API
```bash
# Health check
curl http://localhost:8000/health/

# Send chat message
curl -X POST http://localhost:8000/chat/message \
  -H "Content-Type: application/json" \
  -d '{"message": "What is BLKOUT about?"}'

# Get upcoming events
curl http://localhost:8000/events/upcoming
```

### WebSocket Testing
Use a WebSocket client to connect to `ws://localhost:8000/ws` and send:
```json
{
  "message": "Hello IVOR!",
  "session_id": "test-session",
  "context": {}
}
```

## Cost Optimization

This backend is designed for cost-effectiveness:
- **DeepSeek**: 96% cheaper than OpenAI GPT-4
- **ChromaDB**: Self-hosted vector database ($0 cost)
- **Docker**: Easy deployment on low-cost VPS

Expected monthly costs: $5-15 for moderate usage.

## Community Values

IVOR embodies BLKOUT's core values:
- Collaboration over competition
- Complexity over simplification  
- Conversation over conversion
- Community over commodity
- Realness over perfectionism
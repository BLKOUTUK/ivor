# IVOR - Community AI Assistant
## BLKOUT's AI-Powered Community Platform

IVOR (Interactive Virtual Organizing Representative) is BLKOUT's community AI assistant designed to facilitate authentic connections, support cooperative ownership initiatives, and embody community values through intelligent dialogue.

---

## 🎯 Features

### AI-Powered Community Support
- **DeepSeek Integration**: 96% cheaper than OpenAI with excellent performance
- **Community Knowledge Base**: ChromaDB with BLKOUT values and cooperative resources
- **Event Integration**: Connect community members with upcoming events
- **Values-Driven Responses**: Embodies BLKOUT's core principles

### Cost-Optimized Architecture
- **Monthly Costs**: $15-35 (vs $135-400 with traditional stack)
- **Open Source Vector DB**: Self-hosted ChromaDB
- **Efficient LLMs**: DeepSeek primary, Qwen fallback
- **Docker Deployment**: Easy scaling on low-cost infrastructure

### Community-First Design
- **Registration-Free**: Anonymous sessions with browser storage
- **Privacy-Focused**: Minimal data collection
- **Accessibility**: Full keyboard navigation and screen reader support
- **Mobile-Optimized**: Responsive design for all devices

---

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- Node.js 18+ (for frontend integration)
- DeepSeek API key ([Get one here](https://platform.deepseek.com))
- Optional: OpenAI API key for embeddings

### 1. Backend Setup

```bash
cd backend
cp .env.example .env
# Edit .env with your API keys
./start.sh
```

### 2. Test the API

```bash
# Health check
curl http://localhost:8000/health/

# Send message
curl -X POST http://localhost:8000/chat/message \
  -H "Content-Type: application/json" \
  -d '{"message": "What is BLKOUT about?"}'
```

### 3. Docker Deployment

```bash
cd deployment
docker-compose up --build
```

---

## 📁 Repository Structure

```
ivor/
├── backend/                 # FastAPI backend service
│   ├── core/               # Core AI and knowledge base logic
│   ├── api/                # REST API endpoints
│   ├── utils/              # Utilities and helpers
│   ├── main.py             # FastAPI application entry point
│   ├── requirements.txt    # Python dependencies
│   └── Dockerfile         # Container configuration
├── docs/                   # Documentation
│   ├── API.md             # API reference
│   ├── DEPLOYMENT.md      # Deployment guide
│   └── DEVELOPMENT.md     # Development setup
├── deployment/             # Deployment configurations
│   ├── docker-compose.yml # Local development
│   ├── production.yml     # Production deployment
│   └── kubernetes/        # K8s manifests
├── scripts/               # Utility scripts
│   ├── setup.sh          # Environment setup
│   └── backup.sh         # Database backup
└── README.md             # This file
```

---

## 🏗️ Architecture

### Backend Stack
- **API Framework**: FastAPI with async support
- **AI Integration**: DeepSeek (primary) + Qwen (fallback)
- **Knowledge Base**: ChromaDB with semantic search
- **Database**: PostgreSQL + Redis for caching
- **Real-time**: WebSocket connections

### AI Pipeline
```
User Query → Agent Controller → Knowledge Retrieval → Context Synthesis → LLM Generation → Response
```

### Data Flow
1. **Message Processing**: Parse and analyze user input
2. **Knowledge Search**: Semantic search across community documents
3. **Context Building**: Combine retrieved knowledge with conversation history
4. **AI Generation**: Generate response using DeepSeek/Qwen
5. **Response Enhancement**: Add sources, suggestions, and metadata

---

## 🔧 Configuration

### Environment Variables

**Required:**
```env
DEEPSEEK_API_KEY=your_deepseek_api_key
DATABASE_URL=postgresql://user:pass@localhost:5432/ivor_db
REDIS_URL=redis://localhost:6379
```

**Optional:**
```env
QWEN_API_KEY=your_qwen_api_key
OPENAI_API_KEY=your_openai_api_key
DEBUG=True
LOG_LEVEL=INFO
```

### Knowledge Base

IVOR comes pre-loaded with:
- BLKOUT core values and principles
- Cooperative ownership basics
- Community engagement guides
- Getting involved resources

Add custom knowledge by updating `core/knowledge_base.py`

---

## 🔌 Frontend Integration

### React Component Integration

```tsx
import IvorChatbot from '@/components/IvorChatbot'
import { IVOR_CONFIG } from '@/lib/ivor-config'

function App() {
  return (
    <div>
      {/* Your app content */}
      <IvorChatbot apiUrl={IVOR_CONFIG.API_BASE_URL} />
    </div>
  )
}
```

### WebSocket Connection

```typescript
const ws = new WebSocket('ws://localhost:8000/ws')
ws.send(JSON.stringify({
  message: "Hello IVOR!",
  session_id: "user-session-id",
  context: {}
}))
```

---

## 🎨 Community Values Integration

IVOR embodies BLKOUT's core values:

- **Collaboration over competition**: Facilitates connections between community members
- **Complexity over simplification**: Handles nuanced conversations about community issues
- **Conversation over conversion**: Focuses on dialogue rather than persuasion
- **Community over commodity**: Prioritizes community needs over profit
- **Realness over perfectionism**: Authentic responses that acknowledge limitations

---

## 📊 Cost Analysis

### Monthly Operating Costs

**DeepSeek API Usage:**
- Light usage (100 queries/day): ~$3
- Moderate usage (500 queries/day): ~$12
- Heavy usage (2000 queries/day): ~$40

**Infrastructure:**
- VPS hosting: $5-20
- Database: $10-30
- Total: **$15-90/month**

**Cost Comparison:**
- Traditional stack (GPT-4 + Pinecone): $135-400/month
- IVOR stack: $15-90/month
- **Savings: 75-85%**

---

## 🚀 Deployment

### Production Deployment

1. **Prepare Environment**
   ```bash
   cd deployment
   cp production.env.example production.env
   # Edit with production values
   ```

2. **Deploy with Docker**
   ```bash
   docker-compose -f production.yml up -d
   ```

3. **Configure Reverse Proxy**
   ```nginx
   location /api/ {
       proxy_pass http://localhost:8000/;
   }
   ```

### Scaling Considerations

- **Horizontal Scaling**: Multiple FastAPI instances behind load balancer
- **Database**: Managed PostgreSQL for production
- **Vector DB**: Consider Pinecone/Weaviate for large-scale deployments
- **Monitoring**: Implement health checks and alerting

---

## 🧪 Development

### Running Tests

```bash
cd backend
pytest tests/
```

### Adding Knowledge

```python
# In core/knowledge_base.py
await knowledge_base.add_document(
    doc_id="new_doc",
    content="Community resource content...",
    metadata={"category": "resources", "source": "community"}
)
```

### Custom AI Prompts

```python
# In core/ai_service.py
def _create_system_prompt(self) -> str:
    return """Your custom system prompt here..."""
```

---

## 🤝 Contributing

1. Fork the repository
2. Create feature branch: `git checkout -b feature/amazing-feature`
3. Commit changes: `git commit -m 'Add amazing feature'`
4. Push to branch: `git push origin feature/amazing-feature`
5. Open Pull Request

### Development Guidelines

- Follow BLKOUT community values
- Maintain cost-effectiveness
- Prioritize accessibility
- Write tests for new features
- Update documentation

---

## 📝 License

Community-Owned - BLKOUT Community

---

## 🆘 Support

- **Documentation**: Check `/docs` directory
- **Issues**: GitHub Issues
- **Community**: BLKOUT Discord/Slack
- **API Docs**: http://localhost:8000/docs (when running)

---

## 🎉 Acknowledgments

Built with ❤️ by the BLKOUT community, embodying our values of cooperation, authenticity, and community-driven development.

**Technologies:**
- FastAPI, DeepSeek, ChromaDB, PostgreSQL, Redis
- React, TypeScript, Framer Motion, Tailwind CSS

**Community Values:**
- Building cooperative ownership together 🏳️‍🌈
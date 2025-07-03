# Getting No-Cost API Keys for IVOR

Quick guide to get free API keys for Mixtral 8x7B integration.

---

## 🚀 Groq (Recommended - Fastest)

### 1. Sign up at Groq
- Go to: https://console.groq.com
- Click "Sign Up" (free account)
- Verify email

### 2. Get API Key
- Go to "API Keys" in dashboard
- Click "Create API Key"
- Copy the key (starts with `gsk_...`)

### 3. Add to .env
```env
GROQ_API_KEY=gsk_your_key_here
```

**Free Limits**: Very generous rate limits, excellent for development and production

---

## 🤗 Hugging Face (Backup)

### 1. Sign up at Hugging Face
- Go to: https://huggingface.co
- Click "Sign Up" (free account)
- Verify email

### 2. Get API Token
- Go to: https://huggingface.co/settings/tokens
- Click "New token"
- Name: "IVOR Backend"
- Role: "Read"
- Click "Generate"
- Copy the token (starts with `hf_...`)

### 3. Add to .env
```env
HUGGINGFACE_API_TOKEN=hf_your_token_here
```

**Free Limits**: 1,000 requests/month, good for development

---

## ⚡ Complete Setup

### 1. Create .env file
```bash
cd /home/robbe/projects/ivor-repository/backend
cp .env.example .env
```

### 2. Edit .env with your keys
```env
# Primary AI APIs (No Cost)
HUGGINGFACE_API_TOKEN=hf_your_token_here
GROQ_API_KEY=gsk_your_key_here

# Database Configuration  
DATABASE_URL=postgresql://ivor:ivor123@localhost:5432/ivor_db
REDIS_URL=redis://localhost:6379

# Application Configuration
DEBUG=True
LOG_LEVEL=INFO
CORS_ORIGINS=["http://localhost:3000", "http://localhost:3003"]

# ChromaDB Configuration
CHROMA_PERSIST_DIRECTORY=./chroma_db
CHROMA_COLLECTION_NAME=blkout_community_knowledge
```

### 3. Start IVOR
```bash
./start.sh
```

### 4. Test
```bash
curl -X POST http://localhost:8000/chat/message \
  -H "Content-Type: application/json" \
  -d '{"message": "Hello IVOR!"}'
```

---

## 🔄 Priority Order

IVOR will try APIs in this order:
1. **Groq** (fastest, most reliable)
2. **Hugging Face** (fallback)
3. **Fallback response** (if all fail)

---

## 🎯 Expected Performance

- **Groq**: ~1-2 seconds response time
- **Hugging Face**: ~3-5 seconds response time
- **Both**: High-quality Mixtral 8x7B responses
- **Cost**: $0/month for reasonable usage

---

## 🚨 Troubleshooting

**Groq not working?**
- Check API key starts with `gsk_`
- Verify account is active
- Check rate limits in dashboard

**Hugging Face not working?**
- Check token starts with `hf_`
- Ensure "Read" permissions
- Model might be loading (try again in 30 seconds)

**Both failing?**
- Check internet connection
- Verify .env file format
- Look at backend logs: `tail -f logs/ivor.log`

That's it! You now have no-cost Mixtral 8x7B integration. 🎉
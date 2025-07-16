# BLKOUT Community Data System - Testing Guide

This guide explains how to test the integrated BLKOUT community data system.

## 🚀 Quick Start

### 1. Setup Environment

```bash
# Copy environment configuration
cp env_example.txt .env

# Edit .env with your database and API keys
nano .env
```

### 2. Install Dependencies

```bash
pip install fastapi uvicorn sqlalchemy psycopg2-binary redis httpx python-dotenv pydantic
```

### 3. Run Integration Tests

```bash
# Run comprehensive integration tests
python test_integration.py
```

### 4. Start the System

```bash
# Start the backend server
python run_system.py
```

### 5. Test API Endpoints

```bash
# In another terminal, test all API endpoints
python test_api.py
```

## 🧪 Test Components

### Database Integration Tests

The integration test verifies:
- ✅ Database connection and table creation
- ✅ PostgreSQL schema with all 9 tables
- ✅ Model relationships and constraints
- ✅ Privacy-compliant views and functions

### Consent Management Tests

Tests the 4-level consent system:
- ✅ **Anonymous Only**: Basic community analytics
- ✅ **Personal Service**: IVOR personalization
- ✅ **Community Insights**: Pathway matching
- ✅ **Peer Connections**: Community networking

### User Context Service Tests

Verifies personalization features:
- ✅ Topic extraction from messages
- ✅ Conversation history analysis
- ✅ Liberation pathway integration
- ✅ Community interest tracking
- ✅ Peer similarity matching

### IVOR AI Service Tests

Tests the enhanced AI system:
- ✅ Context-aware responses
- ✅ User personalization prompts
- ✅ Knowledge base integration
- ✅ Privacy-respecting AI behavior

### API Endpoint Tests

Tests all REST endpoints:
- ✅ `/health` - System health check
- ✅ `/api/community/profile` - User profiles
- ✅ `/api/community/email-subscription` - Email signups
- ✅ `/api/community/quiz-result` - Quiz submissions
- ✅ `/chat/message` - IVOR conversations
- ✅ `/conversations/history/{email}` - Chat history
- ✅ `/profiles/profile/{email}` - Unified profiles
- ✅ `/api/community/analytics/community-insights` - Analytics

## 📊 Expected Test Results

### Integration Tests
```
🧪 TEST RESULTS SUMMARY
==================================================
Total Tests: 6
Passed: 6 ✅
Failed: 0 ❌
Success Rate: 100.0%

🎉 ALL TESTS PASSED! System is ready for use.
```

### API Tests
```
🧪 API TEST RESULTS
============================================================
Total Tests: 8
Passed: 8 ✅
Failed: 0 ❌
Success Rate: 100.0%
```

## 🔧 Manual Testing

### 1. Test Community Profile Creation

```bash
curl -X POST http://localhost:8000/api/community/profile \\
  -H "Content-Type: application/json" \\
  -d '{
    "email": "test@blkoutuk.com",
    "name": "Test User",
    "location": "London",
    "source": "email_capture",
    "consent_preferences": {
      "anonymous_only": false,
      "personal_service": true,
      "community_insights": true,
      "peer_connections": false
    }
  }'
```

### 2. Test IVOR Chat with Context

```bash
curl -X POST http://localhost:8000/chat/message \\
  -H "Content-Type: application/json" \\
  -d '{
    "message": "Hello IVOR, I need help with housing",
    "user_email": "test@blkoutuk.com",
    "consent_level": "personal_service",
    "context": {
      "location": "London",
      "urgent": true
    }
  }'
```

### 3. Test Conversation History

```bash
curl http://localhost:8000/conversations/history/test@blkoutuk.com?limit=5
```

### 4. Test Unified Profile

```bash
curl http://localhost:8000/profiles/profile/test@blkoutuk.com
```

## 🚨 Common Issues & Solutions

### Database Connection Issues

**Problem**: `connection to server at "localhost", port 5432 failed`

**Solution**:
1. Ensure PostgreSQL is running
2. Check DATABASE_URL in .env
3. Create the database: `createdb blkout_community`

### Redis Connection Issues

**Problem**: `Redis connection failed`

**Solution**:
1. Install Redis: `sudo apt install redis-server`
2. Start Redis: `sudo systemctl start redis`
3. Check REDIS_URL in .env

### API Key Issues

**Problem**: `Groq API key not configured`

**Solution**:
1. Get API key from https://console.groq.com/
2. Set GROQ_API_KEY in .env
3. Restart the server

### Import Errors

**Problem**: `ModuleNotFoundError: No module named 'X'`

**Solution**:
```bash
pip install fastapi uvicorn sqlalchemy psycopg2-binary redis httpx python-dotenv pydantic
```

## 📝 Test Data

### Sample Community Profile

```json
{
  "email": "storyteller@blkoutuk.com",
  "name": "Creative Storyteller",
  "location": "Birmingham",
  "source": "quiz",
  "journey_stage": "engaged",
  "consent_preferences": {
    "anonymous_only": false,
    "personal_service": true,
    "community_insights": true,
    "peer_connections": false
  }
}
```

### Sample Quiz Result

```json
{
  "email": "storyteller@blkoutuk.com",
  "pathway": "storyteller",
  "pathway_title": "THE STORYTELLER",
  "scores": {
    "identity": 4,
    "community": 3,
    "liberation": 2,
    "connection": 3
  },
  "answers": {
    "energy_source": "Creating something beautiful",
    "safe_space": "Creative studio or workshop"
  },
  "community_match": "Creative Community & StoryLab",
  "next_steps": [
    "Join our StoryLab workshops",
    "Contribute to the BLKOUT Channel"
  ]
}
```

## 🎯 Test Scenarios

### Scenario 1: New User Journey

1. User signs up via email capture
2. Takes liberation pathway quiz
3. Chats with IVOR (gets personalized responses)
4. Requests BLKOUTHUB access
5. Views their unified profile

### Scenario 2: Privacy-Conscious User

1. User creates profile with anonymous_only consent
2. Uses IVOR chat (no personalization)
3. Upgrades to personal_service consent
4. Gets personalized IVOR responses
5. Views conversation history

### Scenario 3: Community Builder

1. User completes quiz → "community-builder" pathway
2. Enables peer_connections consent
3. Gets matched with similar users
4. Receives community organizing recommendations
5. Contributes to knowledge base

## 📈 Performance Testing

### Load Testing with curl

```bash
# Test concurrent requests
for i in {1..10}; do
  curl -X POST http://localhost:8000/chat/message \\
    -H "Content-Type: application/json" \\
    -d '{"message": "Hello IVOR '$i'", "consent_level": "anonymous_only"}' &
done
wait
```

### Database Performance

```sql
-- Check query performance
EXPLAIN ANALYZE SELECT * FROM community_insights;
EXPLAIN ANALYZE SELECT * FROM popular_pathways;
```

## 🛠️ Debugging

### Enable Debug Logging

```bash
# Set in .env
DEBUG=true
LOG_LEVEL=debug
```

### Check Database Tables

```sql
-- Connect to database
psql -d blkout_community

-- List tables
\\dt

-- Check table structure
\\d community_profiles
\\d ivor_interactions
```

### Monitor Redis

```bash
# Connect to Redis
redis-cli

# Check keys
KEYS *

# Monitor commands
MONITOR
```

## ✅ Success Criteria

The system is working correctly when:

1. **All integration tests pass** (6/6)
2. **All API tests pass** (8/8)
3. **Database has all 9 tables** created
4. **IVOR provides personalized responses** based on user context
5. **Conversation history is stored** and retrievable
6. **Consent management works** across all privacy levels
7. **Forms integrate with database** successfully
8. **Community analytics** generate insights

## 🎉 Next Steps

Once testing is complete:

1. **Deploy to staging** environment
2. **Run load tests** with realistic traffic
3. **Test N8N integrations** with real workflows
4. **Implement monthly reports** system
5. **Add community dashboard** interface
6. **Launch user acceptance testing**

---

*This testing guide ensures the BLKOUT Community Data System works correctly and provides the privacy-first, liberation-centered experience our community deserves.*
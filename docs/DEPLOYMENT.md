# IVOR Deployment Guide

Complete guide for deploying IVOR in various environments.

---

## Deployment Options

### 1. Local Development
**Best for**: Testing and development
**Cost**: Free
**Complexity**: Low

### 2. VPS Deployment  
**Best for**: Production with cost control
**Cost**: $5-20/month
**Complexity**: Medium

### 3. Cloud Platform
**Best for**: Auto-scaling production
**Cost**: $20-100/month
**Complexity**: Medium-High

### 4. Kubernetes
**Best for**: Enterprise/high-scale
**Cost**: $50+/month
**Complexity**: High

---

## 1. Local Development

### Quick Start

```bash
# Clone repository
git clone https://github.com/blkoutuk/ivor.git
cd ivor/backend

# Setup environment
cp .env.example .env
# Edit .env with your API keys

# Start with Docker
cd ../deployment
docker-compose up --build

# Or start manually
cd ../backend
./start.sh
```

### Environment Configuration

```env
# .env file
DEEPSEEK_API_KEY=your_deepseek_api_key
OPENAI_API_KEY=your_openai_api_key
DATABASE_URL=postgresql://ivor:ivor123@localhost:5432/ivor_db
REDIS_URL=redis://localhost:6379
DEBUG=True
LOG_LEVEL=INFO
```

---

## 2. VPS Deployment (Recommended)

### Providers
- **Hetzner Cloud**: €4.15/month (2 CPU, 4GB RAM)
- **DigitalOcean**: $24/month (2 CPU, 4GB RAM)  
- **Linode**: $24/month (2 CPU, 4GB RAM)
- **Vultr**: $12/month (2 CPU, 4GB RAM)

### Server Setup

```bash
# 1. Update system
sudo apt update && sudo apt upgrade -y

# 2. Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER

# 3. Install Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# 4. Clone repository
git clone https://github.com/blkoutuk/ivor.git
cd ivor
```

### Production Configuration

```bash
# Create production environment file
cp deployment/production.env.example deployment/production.env

# Edit with production values
nano deployment/production.env
```

```env
# production.env
DEEPSEEK_API_KEY=your_production_key
OPENAI_API_KEY=your_production_key
DATABASE_URL=postgresql://ivor:secure_password@postgres:5432/ivor_db
REDIS_URL=redis://redis:6379
DEBUG=False
LOG_LEVEL=WARNING
CORS_ORIGINS=["https://yourdomain.com", "https://www.yourdomain.com"]
```

### Deploy with Docker

```bash
# Deploy production stack
docker-compose -f deployment/production.yml up -d

# Check status
docker-compose -f deployment/production.yml ps

# View logs
docker-compose -f deployment/production.yml logs -f ivor-backend
```

### Reverse Proxy (Nginx)

```nginx
# /etc/nginx/sites-available/ivor
server {
    listen 80;
    server_name api.yourdomain.com;

    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /ws {
        proxy_pass http://localhost:8000/ws;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "Upgrade";
        proxy_set_header Host $host;
    }
}
```

```bash
# Enable site
sudo ln -s /etc/nginx/sites-available/ivor /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx

# SSL with Let's Encrypt
sudo certbot --nginx -d api.yourdomain.com
```

---

## 3. Cloud Platform Deployment

### Railway (Recommended for simplicity)

1. **Connect Repository**
   - Link GitHub repository to Railway
   - Select `backend` folder as root

2. **Environment Variables**
   ```
   DEEPSEEK_API_KEY=your_key
   OPENAI_API_KEY=your_key
   DATABASE_URL=${{Postgres.DATABASE_URL}}
   REDIS_URL=${{Redis.REDIS_URL}}
   ```

3. **Add Services**
   - PostgreSQL database
   - Redis cache
   - Deploy

### Render

```yaml
# render.yaml
services:
  - type: web
    name: ivor-backend
    env: python
    buildCommand: "pip install -r requirements.txt"
    startCommand: "uvicorn main:app --host 0.0.0.0 --port $PORT"
    envVars:
      - key: DEEPSEEK_API_KEY
        sync: false
      - key: DATABASE_URL
        fromDatabase:
          name: ivor-db
          property: connectionString
```

### Heroku

```bash
# Install Heroku CLI and login
heroku create ivor-backend

# Add buildpack
heroku buildpacks:set heroku/python

# Set environment variables
heroku config:set DEEPSEEK_API_KEY=your_key
heroku config:set OPENAI_API_KEY=your_key

# Add PostgreSQL
heroku addons:create heroku-postgresql:hobby-dev

# Add Redis
heroku addons:create heroku-redis:hobby-dev

# Deploy
git subtree push --prefix=backend heroku main
```

---

## 4. Kubernetes Deployment

### Prerequisites

```bash
# Install kubectl and helm
kubectl version
helm version
```

### Namespace Setup

```yaml
# namespace.yaml
apiVersion: v1
kind: Namespace
metadata:
  name: ivor
```

### ConfigMap

```yaml
# configmap.yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: ivor-config
  namespace: ivor
data:
  DEBUG: "False"
  LOG_LEVEL: "INFO"
  CORS_ORIGINS: '["https://yourdomain.com"]'
```

### Secrets

```yaml
# secrets.yaml
apiVersion: v1
kind: Secret
metadata:
  name: ivor-secrets
  namespace: ivor
type: Opaque
data:
  deepseek-api-key: <base64-encoded-key>
  openai-api-key: <base64-encoded-key>
  database-url: <base64-encoded-url>
  redis-url: <base64-encoded-url>
```

### Deployment

```yaml
# deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: ivor-backend
  namespace: ivor
spec:
  replicas: 2
  selector:
    matchLabels:
      app: ivor-backend
  template:
    metadata:
      labels:
        app: ivor-backend
    spec:
      containers:
      - name: ivor-backend
        image: your-registry/ivor-backend:latest
        ports:
        - containerPort: 8000
        env:
        - name: DEEPSEEK_API_KEY
          valueFrom:
            secretKeyRef:
              name: ivor-secrets
              key: deepseek-api-key
        envFrom:
        - configMapRef:
            name: ivor-config
        resources:
          requests:
            memory: "256Mi"
            cpu: "250m"
          limits:
            memory: "512Mi"
            cpu: "500m"
```

### Service & Ingress

```yaml
# service.yaml
apiVersion: v1
kind: Service
metadata:
  name: ivor-backend-service
  namespace: ivor
spec:
  selector:
    app: ivor-backend
  ports:
  - port: 80
    targetPort: 8000
  type: ClusterIP

---
# ingress.yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: ivor-ingress
  namespace: ivor
  annotations:
    cert-manager.io/cluster-issuer: "letsencrypt-prod"
    nginx.ingress.kubernetes.io/websocket-services: "ivor-backend-service"
spec:
  tls:
  - hosts:
    - api.yourdomain.com
    secretName: ivor-tls
  rules:
  - host: api.yourdomain.com
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: ivor-backend-service
            port:
              number: 80
```

---

## Environment-Specific Configurations

### Development
```env
DEBUG=True
LOG_LEVEL=DEBUG
DATABASE_URL=sqlite:///./test.db
CORS_ORIGINS=["http://localhost:3000", "http://localhost:3003"]
```

### Staging
```env
DEBUG=True
LOG_LEVEL=INFO
DATABASE_URL=postgresql://staging_user:pass@staging-db:5432/ivor_staging
CORS_ORIGINS=["https://staging.yourdomain.com"]
```

### Production
```env
DEBUG=False
LOG_LEVEL=WARNING
DATABASE_URL=postgresql://prod_user:secure_pass@prod-db:5432/ivor_prod
CORS_ORIGINS=["https://yourdomain.com", "https://www.yourdomain.com"]
```

---

## Monitoring & Observability

### Health Checks

```bash
# Basic health
curl https://api.yourdomain.com/health/

# Detailed health
curl https://api.yourdomain.com/health/detailed
```

### Logging

```bash
# Docker logs
docker-compose logs -f ivor-backend

# Kubernetes logs
kubectl logs -f deployment/ivor-backend -n ivor

# Log aggregation with ELK stack
# See deployment/monitoring/elk-stack.yml
```

### Metrics

```python
# Add to main.py for Prometheus metrics
from prometheus_client import Counter, Histogram, generate_latest

REQUEST_COUNT = Counter('ivor_requests_total', 'Total requests')
REQUEST_DURATION = Histogram('ivor_request_duration_seconds', 'Request duration')

@app.get("/metrics")
async def metrics():
    return Response(generate_latest(), media_type="text/plain")
```

---

## Backup & Recovery

### Database Backup

```bash
# PostgreSQL backup
docker exec postgres pg_dump -U ivor ivor_db > backup_$(date +%Y%m%d).sql

# Restore
docker exec -i postgres psql -U ivor ivor_db < backup_20250703.sql
```

### Knowledge Base Backup

```bash
# ChromaDB backup
docker exec ivor-backend tar -czf /tmp/chroma_backup.tar.gz /app/chroma_db
docker cp ivor-backend:/tmp/chroma_backup.tar.gz ./chroma_backup_$(date +%Y%m%d).tar.gz
```

### Automated Backups

```bash
# Add to crontab
0 2 * * * /path/to/backup-script.sh
```

---

## Security Considerations

### API Security
- Use HTTPS in production
- Implement rate limiting
- Validate all inputs
- Monitor for suspicious activity

### Infrastructure Security
- Keep systems updated
- Use strong passwords
- Limit SSH access
- Enable firewall

### Container Security
- Use non-root user in containers
- Scan images for vulnerabilities
- Keep base images updated
- Limit container privileges

---

## Performance Optimization

### Database Optimization
```sql
-- Add indexes for better query performance
CREATE INDEX idx_conversations_session_id ON conversations(session_id);
CREATE INDEX idx_conversations_timestamp ON conversations(timestamp);
```

### Caching Strategy
```python
# Redis caching for frequent queries
@lru_cache(maxsize=100)
def get_community_values():
    return cached_values
```

### Load Balancing
```nginx
upstream ivor_backend {
    server 127.0.0.1:8000;
    server 127.0.0.1:8001;
    server 127.0.0.1:8002;
}
```

---

## Cost Optimization

### VPS Deployment Costs
- **Hetzner**: €4.15/month + API costs
- **Total monthly**: €15-35 for moderate usage

### Cloud Platform Costs
- **Railway**: $5-20/month + usage
- **Render**: $7-25/month + usage
- **Total monthly**: $25-75 for moderate usage

### Optimization Tips
1. Use DeepSeek over OpenAI (96% savings)
2. Self-host ChromaDB vs Pinecone
3. Choose appropriate server size
4. Monitor and optimize API usage
5. Use connection pooling
6. Implement proper caching

---

## Troubleshooting

### Common Issues

**Cannot connect to backend:**
```bash
# Check if service is running
docker-compose ps
curl localhost:8000/health/
```

**Database connection fails:**
```bash
# Check database logs
docker-compose logs postgres
# Verify connection string
echo $DATABASE_URL
```

**High response times:**
```bash
# Check system resources
docker stats
# Monitor API usage
curl localhost:8000/health/detailed
```

**WebSocket connection issues:**
```bash
# Test WebSocket connection
wscat -c ws://localhost:8000/ws
# Check nginx WebSocket config
nginx -t
```

### Log Analysis

```bash
# Search for errors
docker-compose logs | grep ERROR

# Monitor real-time logs
docker-compose logs -f --tail=100

# Filter by service
docker-compose logs -f ivor-backend
```

---

## Migration Guide

### From Single Container to Multi-Service

1. **Extract Database**
   ```bash
   # Export existing data
   docker exec container pg_dump > migration.sql
   
   # Import to new database
   docker exec new-postgres psql < migration.sql
   ```

2. **Update Configuration**
   ```env
   # Change from SQLite to PostgreSQL
   DATABASE_URL=postgresql://user:pass@postgres:5432/db
   ```

3. **Deploy New Stack**
   ```bash
   docker-compose -f production.yml up -d
   ```

### Version Updates

```bash
# Update to new version
git pull origin main
docker-compose pull
docker-compose up -d

# Rollback if needed
git checkout previous-tag
docker-compose up -d
```

This deployment guide ensures IVOR can be deployed reliably across different environments while maintaining cost-effectiveness and community accessibility.
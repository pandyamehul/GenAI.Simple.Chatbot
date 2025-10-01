# Enhanced GenAI Platform - Production Deployment Guide

## 🎯 Overview

This guide provides comprehensive instructions for deploying the Enhanced GenAI Platform v3.0 in production environments, including setup, configuration, security, and scaling considerations.

## 📋 Prerequisites

### System Requirements
- **Python**: 3.8 or higher
- **Memory**: Minimum 4GB RAM (8GB+ recommended)
- **Storage**: 10GB+ available disk space
- **OS**: Windows 10+, macOS 10.15+, or Linux (Ubuntu 18.04+)

### Required Services
- **Database**: PostgreSQL 12+ or MongoDB 4.4+
- **Cache**: Redis 6.0+ (optional but recommended)
- **WebSocket**: FastAPI with uvicorn or similar ASGI server
- **Reverse Proxy**: Nginx or Apache (for production)

## 🚀 Deployment Options

### 1. Local Development Deployment

#### Quick Start
```bash
# Clone repository
git clone https://github.com/pandyamehul/GenAI.Simple.Chatbot.git
cd GenAI.Simple.Chatbot

# Install dependencies
pip install -r requirements.txt

# Set environment variables
export OPENAI_API_KEY="your_openai_key_here"
export SECRET_KEY="your_secret_key_here"

# Run validation
python ./Modular_App/validate_modules.py

# Start application
streamlit run ./Modular_App/app.py
```

#### Environment Configuration
Create `.env` file in the project root:
```env
# API Keys
OPENAI_API_KEY=sk-your-openai-key-here
ANTHROPIC_API_KEY=your-anthropic-key-here
GOOGLE_API_KEY=your-google-ai-key-here

# Security
SECRET_KEY=your-256-bit-secret-key-here
JWT_ALGORITHM=HS256
JWT_EXPIRATION_HOURS=24

# Database (Optional)
DATABASE_URL=postgresql://user:password@localhost:5432/genai_platform
MONGODB_URL=mongodb://localhost:27017/genai_platform

# Redis (Optional)
REDIS_URL=redis://localhost:6379/0

# Application Settings
DEBUG=False
LOG_LEVEL=INFO
MAX_UPLOAD_SIZE=100MB
ALLOWED_FILE_TYPES=pdf,docx,xlsx,pptx,txt
```

### 2. Docker Deployment

#### Dockerfile
```dockerfile
FROM python:3.9-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create non-root user
RUN useradd -m -u 1000 genai && chown -R genai:genai /app
USER genai

# Expose ports
EXPOSE 8501 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD curl -f http://localhost:8501/ || exit 1

# Default command
CMD ["streamlit", "run", "./Modular_App/app.py", "--server.port=8501", "--server.address=0.0.0.0"]
```

#### Docker Compose
```yaml
version: '3.8'

services:
  genai-platform:
    build: .
    ports:
      - "8501:8501"
      - "8000:8000"
    environment:
      - OPENAI_API_KEY=${OPENAI_API_KEY}
      - SECRET_KEY=${SECRET_KEY}
      - DATABASE_URL=postgresql://postgres:password@postgres:5432/genai_platform
      - REDIS_URL=redis://redis:6379/0
    depends_on:
      - postgres
      - redis
    volumes:
      - ./uploads:/app/uploads
      - ./logs:/app/logs
    restart: unless-stopped

  postgres:
    image: postgres:13
    environment:
      POSTGRES_DB: genai_platform
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: password
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"
    restart: unless-stopped

  redis:
    image: redis:6-alpine
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data
    restart: unless-stopped

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
      - ./ssl:/etc/nginx/ssl
    depends_on:
      - genai-platform
    restart: unless-stopped

volumes:
  postgres_data:
  redis_data:
```

#### Deployment Commands
```bash
# Build and start services
docker-compose up -d

# View logs
docker-compose logs -f genai-platform

# Scale application
docker-compose up -d --scale genai-platform=3

# Update deployment
docker-compose pull
docker-compose up -d
```

### 3. Kubernetes Deployment

#### Namespace
```yaml
apiVersion: v1
kind: Namespace
metadata:
  name: genai-platform
```

#### ConfigMap
```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: genai-config
  namespace: genai-platform
data:
  DEBUG: "False"
  LOG_LEVEL: "INFO"
  MAX_UPLOAD_SIZE: "100MB"
  ALLOWED_FILE_TYPES: "pdf,docx,xlsx,pptx,txt"
```

#### Secret
```yaml
apiVersion: v1
kind: Secret
metadata:
  name: genai-secrets
  namespace: genai-platform
type: Opaque
stringData:
  OPENAI_API_KEY: "your-openai-key-here"
  SECRET_KEY: "your-secret-key-here"
  DATABASE_URL: "postgresql://user:password@postgres:5432/genai_platform"
```

#### Deployment
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: genai-platform
  namespace: genai-platform
spec:
  replicas: 3
  selector:
    matchLabels:
      app: genai-platform
  template:
    metadata:
      labels:
        app: genai-platform
    spec:
      containers:
      - name: genai-platform
        image: genai-platform:latest
        ports:
        - containerPort: 8501
        - containerPort: 8000
        envFrom:
        - configMapRef:
            name: genai-config
        - secretRef:
            name: genai-secrets
        resources:
          requests:
            memory: "2Gi"
            cpu: "500m"
          limits:
            memory: "4Gi"
            cpu: "1000m"
        livenessProbe:
          httpGet:
            path: /
            port: 8501
          initialDelaySeconds: 60
          periodSeconds: 30
        readinessProbe:
          httpGet:
            path: /
            port: 8501
          initialDelaySeconds: 30
          periodSeconds: 10
```

#### Service
```yaml
apiVersion: v1
kind: Service
metadata:
  name: genai-platform-service
  namespace: genai-platform
spec:
  selector:
    app: genai-platform
  ports:
  - name: streamlit
    port: 8501
    targetPort: 8501
  - name: api
    port: 8000
    targetPort: 8000
  type: ClusterIP
```

#### Ingress
```yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: genai-platform-ingress
  namespace: genai-platform
  annotations:
    kubernetes.io/ingress.class: nginx
    cert-manager.io/cluster-issuer: letsencrypt-prod
spec:
  tls:
  - hosts:
    - genai.yourcompany.com
    secretName: genai-platform-tls
  rules:
  - host: genai.yourcompany.com
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: genai-platform-service
            port:
              number: 8501
```

## 🔒 Security Configuration

### 1. Environment Security
```python
# security_config.py
import os
from cryptography.fernet import Fernet

class SecurityConfig:
    # Generate strong secret key
    SECRET_KEY = os.getenv('SECRET_KEY', Fernet.generate_key().decode())
    
    # JWT Configuration
    JWT_ALGORITHM = 'HS256'
    JWT_EXPIRATION_HOURS = 24
    
    # API Rate Limiting
    RATE_LIMIT_PER_MINUTE = 100
    RATE_LIMIT_PER_HOUR = 1000
    
    # File Upload Security
    MAX_FILE_SIZE = 100 * 1024 * 1024  # 100MB
    ALLOWED_EXTENSIONS = {'.pdf', '.docx', '.xlsx', '.pptx', '.txt'}
    UPLOAD_FOLDER = '/secure/uploads'
    
    # CORS Configuration
    ALLOWED_ORIGINS = [
        "https://yourcompany.com",
        "https://genai.yourcompany.com"
    ]
    
    # Database Security
    DATABASE_SSL_MODE = 'require'
    DATABASE_ENCRYPTION = True
```

### 2. Nginx Configuration
```nginx
# nginx.conf
upstream genai_platform {
    server genai-platform:8501 max_fails=3 fail_timeout=30s;
}

server {
    listen 80;
    server_name genai.yourcompany.com;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name genai.yourcompany.com;

    # SSL Configuration
    ssl_certificate /etc/nginx/ssl/certificate.crt;
    ssl_certificate_key /etc/nginx/ssl/private.key;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers ECDHE-RSA-AES256-GCM-SHA512:DHE-RSA-AES256-GCM-SHA512;
    ssl_prefer_server_ciphers off;
    ssl_session_cache shared:SSL:10m;

    # Security Headers
    add_header X-Frame-Options DENY;
    add_header X-Content-Type-Options nosniff;
    add_header X-XSS-Protection "1; mode=block";
    add_header Strict-Transport-Security "max-age=63072000; includeSubDomains; preload";

    # Rate Limiting
    limit_req_zone $binary_remote_addr zone=api:10m rate=10r/s;
    limit_req zone=api burst=20 nodelay;

    # File Upload Limits
    client_max_body_size 100M;
    client_body_timeout 60s;

    location / {
        proxy_pass http://genai_platform;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;

        # WebSocket Support
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_read_timeout 86400;
    }
}
```

## 📊 Monitoring & Logging

### 1. Application Monitoring
```python
# monitoring.py
import logging
import time
from functools import wraps
from prometheus_client import Counter, Histogram, generate_latest

# Metrics
REQUEST_COUNT = Counter('genai_requests_total', 'Total requests', ['method', 'endpoint'])
REQUEST_DURATION = Histogram('genai_request_duration_seconds', 'Request duration')
ERROR_COUNT = Counter('genai_errors_total', 'Total errors', ['error_type'])

def monitor_performance(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        try:
            result = func(*args, **kwargs)
            REQUEST_COUNT.labels(method='POST', endpoint=func.__name__).inc()
            return result
        except Exception as e:
            ERROR_COUNT.labels(error_type=type(e).__name__).inc()
            raise
        finally:
            REQUEST_DURATION.observe(time.time() - start_time)
    return wrapper

# Logging Configuration
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('/app/logs/genai_platform.log'),
        logging.StreamHandler()
    ]
)
```

### 2. Health Check Endpoint
```python
# health.py
from fastapi import FastAPI, HTTPException
from datetime import datetime
import psutil

app = FastAPI()

@app.get("/health")
async def health_check():
    """Comprehensive health check endpoint."""
    try:
        # System metrics
        cpu_percent = psutil.cpu_percent()
        memory_percent = psutil.virtual_memory().percent
        disk_percent = psutil.disk_usage('/').percent
        
        # Application status
        status = {
            "status": "healthy",
            "timestamp": datetime.utcnow().isoformat(),
            "version": "3.0.0",
            "system": {
                "cpu_usage": cpu_percent,
                "memory_usage": memory_percent,
                "disk_usage": disk_percent
            },
            "services": {
                "source_attribution": "operational",
                "collaboration": "operational",
                "websocket": "operational"
            }
        }
        
        # Check critical thresholds
        if cpu_percent > 90 or memory_percent > 90 or disk_percent > 90:
            status["status"] = "degraded"
            
        return status
        
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Health check failed: {str(e)}")

@app.get("/metrics")
async def metrics():
    """Prometheus metrics endpoint."""
    return generate_latest()
```

## 🔧 Database Migration

### PostgreSQL Setup
```sql
-- Create database and user
CREATE DATABASE genai_platform;
CREATE USER genai_user WITH ENCRYPTED PASSWORD 'secure_password';
GRANT ALL PRIVILEGES ON DATABASE genai_platform TO genai_user;

-- Switch to genai_platform database
\c genai_platform;

-- Create tables
CREATE TABLE workspaces (
    workspace_id VARCHAR(36) PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    created_by VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE workspace_users (
    id SERIAL PRIMARY KEY,
    workspace_id VARCHAR(36) REFERENCES workspaces(workspace_id),
    user_id VARCHAR(255) NOT NULL,
    username VARCHAR(255) NOT NULL,
    role VARCHAR(50) NOT NULL,
    permissions JSONB,
    joined_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_active TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE messages (
    message_id VARCHAR(36) PRIMARY KEY,
    workspace_id VARCHAR(36) REFERENCES workspaces(workspace_id),
    user_id VARCHAR(255) NOT NULL,
    username VARCHAR(255) NOT NULL,
    content TEXT NOT NULL,
    message_type VARCHAR(50) NOT NULL,
    metadata JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE document_chunks (
    chunk_id VARCHAR(36) PRIMARY KEY,
    source_file VARCHAR(255) NOT NULL,
    page_number INTEGER,
    section VARCHAR(255),
    chunk_content TEXT,
    metadata JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE citations (
    citation_id VARCHAR(36) PRIMARY KEY,
    chunk_id VARCHAR(36) REFERENCES document_chunks(chunk_id),
    citation_text TEXT NOT NULL,
    style VARCHAR(50) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes
CREATE INDEX idx_workspaces_created_by ON workspaces(created_by);
CREATE INDEX idx_workspace_users_workspace_id ON workspace_users(workspace_id);
CREATE INDEX idx_messages_workspace_id ON messages(workspace_id);
CREATE INDEX idx_document_chunks_source_file ON document_chunks(source_file);
CREATE INDEX idx_citations_chunk_id ON citations(chunk_id);
```

### Migration Script
```python
# migrate.py
import asyncio
import asyncpg
from source_attribution import SourceAttributionManager
from collaboration import create_collaboration_system

async def migrate_to_database():
    """Migrate in-memory data to PostgreSQL."""
    
    # Connect to database
    conn = await asyncpg.connect(
        host='localhost',
        port=5432,
        user='genai_user',
        password='secure_password',
        database='genai_platform'
    )
    
    try:
        # Initialize systems
        attribution_manager = SourceAttributionManager()
        workspace_manager, _, chat_manager = create_collaboration_system()
        
        # Migrate workspaces
        for workspace_id, workspace in workspace_manager.workspaces.items():
            await conn.execute("""
                INSERT INTO workspaces (workspace_id, name, description, created_by, created_at)
                VALUES ($1, $2, $3, $4, $5)
                ON CONFLICT (workspace_id) DO NOTHING
            """, workspace.workspace_id, workspace.name, workspace.description, 
                workspace.created_by, workspace.created_at)
            
            # Migrate users
            for user_id, user in workspace.users.items():
                await conn.execute("""
                    INSERT INTO workspace_users (workspace_id, user_id, username, role, permissions, joined_at)
                    VALUES ($1, $2, $3, $4, $5, $6)
                    ON CONFLICT DO NOTHING
                """, workspace_id, user.user_id, user.username, user.role.value,
                    list(perm.value for perm in user.permissions), user.joined_at)
        
        print("✅ Migration completed successfully")
        
    finally:
        await conn.close()

if __name__ == "__main__":
    asyncio.run(migrate_to_database())
```

## 📈 Performance Optimization

### 1. Caching Strategy
```python
# cache.py
import redis
import json
import pickle
from typing import Any, Optional
from functools import wraps

class CacheManager:
    def __init__(self, redis_url: str = "redis://localhost:6379"):
        self.redis_client = redis.from_url(redis_url)
    
    def cache_result(self, expiry: int = 3600):
        """Decorator to cache function results."""
        def decorator(func):
            @wraps(func)
            def wrapper(*args, **kwargs):
                # Generate cache key
                cache_key = f"{func.__name__}:{hash(str(args) + str(kwargs))}"
                
                # Try to get from cache
                cached_result = self.redis_client.get(cache_key)
                if cached_result:
                    return pickle.loads(cached_result)
                
                # Execute function and cache result
                result = func(*args, **kwargs)
                self.redis_client.setex(
                    cache_key, 
                    expiry, 
                    pickle.dumps(result)
                )
                return result
            return wrapper
        return decorator
    
    def cache_workspace(self, workspace_id: str, workspace_data: Any, expiry: int = 1800):
        """Cache workspace data."""
        cache_key = f"workspace:{workspace_id}"
        self.redis_client.setex(cache_key, expiry, pickle.dumps(workspace_data))
    
    def get_cached_workspace(self, workspace_id: str) -> Optional[Any]:
        """Retrieve cached workspace data."""
        cache_key = f"workspace:{workspace_id}"
        cached_data = self.redis_client.get(cache_key)
        return pickle.loads(cached_data) if cached_data else None

# Usage
cache_manager = CacheManager()

@cache_manager.cache_result(expiry=3600)
def generate_citations_cached(chunk_ids):
    """Cached citation generation."""
    return attribution_manager.generate_citations_for_chunks(chunk_ids)
```

### 2. Load Balancing Configuration
```python
# load_balancer.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
import uvicorn

app = FastAPI(
    title="GenAI Platform Load Balancer",
    version="3.0.0",
    docs_url="/api/docs"
)

# Add middleware
app.add_middleware(GZipMiddleware, minimum_size=1000)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://genai.yourcompany.com"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Health check for load balancer
@app.get("/lb/health")
async def load_balancer_health():
    return {"status": "healthy", "service": "load_balancer"}

if __name__ == "__main__":
    uvicorn.run(
        "load_balancer:app",
        host="0.0.0.0",
        port=8080,
        workers=4,
        loop="uvloop",
        http="httptools"
    )
```

## 🚀 Scaling Strategies

### Horizontal Scaling
```bash
# Scale with Docker Compose
docker-compose up -d --scale genai-platform=5

# Scale with Kubernetes
kubectl scale deployment genai-platform --replicas=10

# Auto-scaling with Kubernetes
kubectl autoscale deployment genai-platform --cpu-percent=50 --min=3 --max=20
```

### Vertical Scaling
```yaml
# Kubernetes resource adjustments
resources:
  requests:
    memory: "4Gi"
    cpu: "1000m"
  limits:
    memory: "8Gi"
    cpu: "2000m"
```

## 🔧 Troubleshooting

### Common Issues

1. **High Memory Usage**
   ```bash
   # Check memory usage
   docker stats genai-platform
   
   # Optimize Python memory
   export PYTHONMALLOC=malloc
   export MALLOC_TRIM_THRESHOLD=100000
   ```

2. **WebSocket Connection Issues**
   ```bash
   # Check WebSocket connectivity
   wscat -c ws://localhost:8501/ws
   
   # Verify Nginx WebSocket config
   nginx -t && nginx -s reload
   ```

3. **Database Connection Errors**
   ```bash
   # Test database connection
   psql -h localhost -U genai_user -d genai_platform -c "SELECT 1;"
   
   # Check connection pool
   SELECT * FROM pg_stat_activity WHERE datname = 'genai_platform';
   ```

### Logging Analysis
```bash
# Real-time log monitoring
tail -f /app/logs/genai_platform.log

# Error analysis
grep "ERROR" /app/logs/genai_platform.log | tail -20

# Performance metrics
grep "performance" /app/logs/genai_platform.log | awk '{print $NF}' | sort -n
```

## 📞 Support & Maintenance

### Backup Strategy
```bash
#!/bin/bash
# backup.sh

# Database backup
pg_dump -h localhost -U genai_user genai_platform > backup_$(date +%Y%m%d_%H%M%S).sql

# File backup
tar -czf uploads_backup_$(date +%Y%m%d_%H%M%S).tar.gz /app/uploads

# Upload to cloud storage (AWS S3 example)
aws s3 cp backup_*.sql s3://genai-backups/database/
aws s3 cp uploads_backup_*.tar.gz s3://genai-backups/files/
```

### Update Procedure
```bash
#!/bin/bash
# update.sh

# Pull latest code
git pull origin main

# Run tests
python ./Modular_App/validate_modules.py

# Update dependencies
pip install -r requirements.txt --upgrade

# Run database migrations
python migrate.py

# Restart services
docker-compose down && docker-compose up -d

# Verify deployment
curl -f http://localhost:8501/health
```

---

**🎉 Production Deployment Complete!**

Your Enhanced GenAI Platform v3.0 is now ready for enterprise production use with comprehensive source attribution and real-time collaboration features.

For additional support, refer to the [troubleshooting guide](TROUBLESHOOTING.md) or contact the development team.
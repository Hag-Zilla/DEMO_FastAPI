# DDoS Protection & Deployment Guide

## Architecture Overview

This deployment uses a 4-layer defense strategy against DDoS attacks:

1. **Firewall (Host OS)** - Blocks direct port access, enforces connection limits
2. **Reverse Proxy (Nginx)** - Rate limiting, request buffering, SSL termination
3. **Application (FastAPI)** - slowapi middleware with Redis backend for distributed rate limiting
4. **Session Storage (Redis)** - Centralized quota tracking across all services

## Quick Start

### 1. Prerequisites

- Docker & Docker Compose (v2.0+)
- Linux host with ufw (or iptables)
- 2GB RAM minimum
- Ports 80/443 available

### 2. Configuration

```bash
# Option 1: Use Makefile (recommended)
make init-env

# Option 2: Manual copy from template
cp .env.docker.prod.example .env.docker.prod

# Edit production values (do NOT skip this!)
nano .env.docker.prod

# Critical settings to customize:
# - SECRET_KEY (min 32 chars, use: openssl rand -hex 32)
# - REDIS_PASSWORD (strong password)
# - DATABASE_URL (production database)
# - DEBUG=false (IMPORTANT for production)
```

### 3. Deploy

```bash
# Load environment
export $(cat .env.docker.prod | xargs)

# Start services
docker-compose -f docker-compose.yml up -d

# Verify all services are running
docker-compose ps

# Check logs
docker-compose logs -f app

# Test endpoint
curl -i http://localhost/health
```

### 4. Firewall Configuration

⚠️ **IMPORTANT:** See [`SETUP.md`](./SETUP.md) for when and how to run `firewall-rules.sh`

```bash
# Apply firewall rules (BEFORE docker-compose up)
sudo bash firewall-rules.sh

# Verify rules
sudo ufw status numbered

# Expected output:
#   ✓ SSH (22) - ALLOWED
#   ✓ HTTP (80) - ALLOWED
#   ✓ HTTPS (443) - ALLOWED
#   ✗ FastAPI (8000) - BLOCKED
#   ✗ Redis (6379) - BLOCKED
```

## Rate Limiting Configuration

### Nginx Layer

Configured in `nginx/nginx.conf`:

- **General API**: 100 req/min per IP (burst: 20)
- **Auth endpoints** (`/login`, `/register`): 20 req/min per IP (burst: 5)
- **File uploads**: 10 req/min per IP (burst: 3)
- **Connection limit**: 50 concurrent connections per IP
- **Body size limit**: 5MB max

### Application Layer

Configured in `app/core/middleware.py` with slowapi + Redis. See [`RATE_LIMITING.md`](./RATE_LIMITING.md) for detailed examples.

```python
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(
    key_func=get_remote_address,
    storage_uri="redis://:redis_password@redis:6379"
)

@app.get("/api/v1/expenses")
@limiter.limit("10/minute")  # 10 requests per minute
async def get_expenses(current_user: User = Depends(get_current_user)):
    ...
```

## Monitoring

### Health Checks

All services have health checks:

```bash
# Check FastAPI
curl -i http://localhost:8000/health

# Check Nginx passes through
curl -i http://localhost/health

# Check Redis
docker-compose exec redis redis-cli -a $(grep REDIS_PASSWORD .env.docker.prod | cut -d= -f2) ping
```

### Logs

```bash
# FastAPI logs (JSON format, with credential redaction)
docker-compose logs -f app | grep -i "ERROR\|WARNING"

# Nginx access/error logs
docker-compose logs -f nginx

# Redis logs
docker-compose logs -f redis
```

### Metrics (Optional: Prometheus)

Install Prometheus exporter:

```bash
# Add to pyproject.toml
uv add prometheus-client

# In app/main.py
from prometheus_client import Counter, Histogram
import time

request_count = Counter('http_requests_total', 'Total HTTP Requests', ['method', 'endpoint'])
request_latency = Histogram('http_request_duration_seconds', 'HTTP Request Latency')

@app.middleware("http")
async def metrics_middleware(request, call_next):
    start = time.time()
    response = await call_next(request)
    duration = time.time() - start
    
    request_count.labels(method=request.method, endpoint=request.url.path).inc()
    request_latency.observe(duration)
    
    return response
```

Monitor with: `curl http://localhost:8000/metrics`

## Scaling

### Horizontal Scaling (Multiple App Instances)

If traffic increases, deploy multiple FastAPI instances:

```yaml
# docker-compose.yml
services:
  app-1:
    build: .
    container_name: demo_app_1
    ports:
      - "8001:8000"
    environment:
      INSTANCE_ID: "1"

  app-2:
    build: .
    container_name: demo_app_2
    ports:
      - "8002:8000"
    environment:
      INSTANCE_ID: "2"

  nginx:
    # Updated upstream section with all app instances
    upstream fastapi_backend {
      least_conn;
      server app-1:8000 max_fails=3 fail_timeout=30s;
      server app-2:8000 max_fails=3 fail_timeout=30s;
      keepalive 32;
    }
```

Redis remains **singleton** (one instance) for unified quota tracking.

## Performance Tuning

### Nginx Tuning

```nginx
# nginx/nginx.conf adjustments for high traffic
worker_processes 8;           # Increase from auto
worker_connections 4096;      # Increase from 1024
keepalive_timeout 120;        # Longer keep-alive
client_max_body_size 10M;     # If needed
```

### Redis Tuning

```bash
# Increase Redis memory limit in docker-compose.yml
command: redis-server 
  --appendonly yes 
  --maxmemory 1gb 
  --maxmemory-policy allkeys-lru
```

### FastAPI Tuning

```bash
# docker-compose.yml - app service
command: >
  ./.venv/bin/python -m uvicorn 
  app.main:app 
  --host 0.0.0.0 
  --port 8000 
  --workers 4 
  --worker-class uvicorn.workers.UvicornWorker
```

## Security Checklist

- [ ] Change `SECRET_KEY` (min 32 random chars)
- [ ] Change `REDIS_PASSWORD` (strong password)
- [ ] Configure SSL/TLS in nginx (uncomment cert/key lines)
- [ ] Enable HTTPS redirect (already in nginx.conf)
- [ ] Run firewall script to lock down ports
- [ ] Set `DEBUG=false` in production
- [ ] Review rate limits for your use case
- [ ] Enable log rotation (journald/logrotate)
- [ ] Use strong database passwords
- [ ] Regular backups of Redis and database

## Troubleshooting

### Port Already in Use

```bash
# Check what's using port 80/443/8000
sudo netstat -tlnp | grep -E ':(80|443|8000)'

# Kill process if needed
sudo kill -9 <PID>
```

### Nginx Can't Reach FastAPI

```bash
# Check DNS/network
docker-compose exec nginx nslookup app

# Test connectivity
docker-compose exec nginx curl -v http://app:8000/health
```

### Redis Connection Refused

```bash
# Check Redis is running
docker-compose logs redis

# Test connection
docker-compose exec redis redis-cli -a <REDIS_PASSWORD> ping
# Should return: PONG
```

### Rate Limit Not Working

```bash
# Check Redis connection from app
docker-compose exec app python -c "
from redis import Redis
r = Redis(host='redis', port=6379, db=0, password='<PASSWORD>')
print('Redis ping:', r.ping())
"

# Check slowapi is initialized
docker-compose logs app | grep -i "slowapi\|limiter"
```

### Firewall Blocking Everything

```bash
# Check firewall rules
sudo ufw status verbose

# Temporarily disable (not recommended)
sudo ufw disable

# Re-enable and reload
sudo ufw enable
sudo systemctl restart ufw
```

## Production Deployment

### Using Kubernetes (Optional)

If scaling to multiple servers, consider Kubernetes:

```yaml
# k8s-deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: fastapi-app
spec:
  replicas: 3
  selector:
    matchLabels:
      app: fastapi
  template:
    metadata:
      labels:
        app: fastapi
    spec:
      containers:
      - name: app
        image: your-registry/fastapi-app:latest
        ports:
        - containerPort: 8000
        env:
        - name: REDIS_URL
          value: "redis://redis-service:6379"
```

### Environment Isolation

For multiple environments, use separate `.env` files:

```bash
.env.local        # Local development
.env.staging      # Staging/testing
.env.prod         # Production
.env.prod-backup  # Disaster recovery
```

## References

- [Nginx Rate Limiting](https://nginx.org/en/docs/http/ngx_http_limit_req_module.html)
- [slowapi Documentation](https://github.com/laurenceisla/slowapi)
- [Redis Security](https://redis.io/topics/security)
- [FastAPI Security](https://fastapi.tiangolo.com/advanced/security/)
- [DDoS Mitigation Best Practices](https://www.cloudflare.com/learning/ddos/ddos-mitigation-techniques/)

# Rate Limiting Implementation Guide

This guide explains how to add rate limiting to FastAPI endpoints using the slowapi library with Redis storage.

## 📑 Table of Contents

- [Overview](#overview)
- [How slowapi Works](#how-slowapi-works)
- [Adding Rate Limits to Endpoints](#adding-rate-limits-to-endpoints)
- [Recommended Limits by Endpoint Type](#recommended-limits-by-endpoint-type)
- [Handling Rate Limit Exceeded (429 Errors)](#handling-rate-limit-exceeded-429-errors)
- [Monitoring Rate Limits](#monitoring-rate-limits)
- [Disabling Rate Limits](#disabling-rate-limits)
- [Advanced: Custom Rate Limiting](#advanced-custom-rate-limiting)
- [Testing Rate Limits](#testing-rate-limits)
- [Common Issues & Solutions](#common-issues--solutions)
- [Production Considerations](#production-considerations)
- [References](#references)

## 🌍 Overview

The application uses a **4-layer rate limiting strategy**:

1. **Host Firewall (ufw)** - Connection limits at OS level
2. **Reverse Proxy (Nginx)** - Request rate limiting (100 req/min general, 20 req/min auth)
3. **Application Layer (slowapi)** - Endpoint-specific limits with Redis tracking
4. **Database** - Query optimization to prevent resource exhaustion

## ⚙️ How slowapi Works

The `limiter` object from `app.core.middleware` tracks requests per IP address and enforces configured limits. It stores quota information in Redis for distributed tracking across multiple app instances.

### Available Limits

```
Format: "requests/timeframe"

Examples:
- "10/minute"      → 10 requests per minute
- "100/hour"       → 100 requests per hour
- "1000/day"       → 1000 requests per day
- "5/second"       → 5 requests per second

Combining:
- "10/minute;100/hour"  → max 10 per minute AND 100 per hour
```

## ➕ Adding Rate Limits to Endpoints

### Example 1: Authentication Endpoint (Strict)

```python
from fastapi import APIRouter
from app.core.middleware import limiter

router = APIRouter(tags=["Authentication"])

@router.post("/token")
@limiter.limit("5/minute")  # Max 5 login attempts per minute
async def login_for_access_token(form_data: OAuth2PasswordRequestFormStrict, db: Session):
    """Authenticate user and return access token.
    
    Rate limit: 5 requests per minute per IP
    (Helps prevent brute-force attacks)
    """
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    token = create_access_token({"sub": user.username})
    return {"access_token": token, "token_type": "bearer"}
```

### Example 2: Read-Only Endpoint (Relaxed)

```python
@router.get("/api/v1/expenses")
@limiter.limit("100/minute")  # Max 100 requests per minute
async def list_expenses(current_user: User = Depends(get_current_user)):
    """List user expenses.
    
    Rate limit: 100 requests per minute per IP
    (Relaxed because it's read-only and not resource-intensive)
    """
    return crud.get_expenses(current_user.id)
```

### Example 3: Heavy Operation (Very Strict)

```python
@router.post("/api/v1/expenses/batch-import")
@limiter.limit("2/minute")  # Max 2 batch imports per minute
async def batch_import_expenses(
    file: UploadFile,
    current_user: User = Depends(get_current_user)
):
    """Batch import expenses from CSV.
    
    Rate limit: 2 requests per minute per IP
    (Strict: prevents resource exhaustion from large file imports)
    """
    # Process file
    return {"imported": count}
```

### Example 4: Multiple Limits (Time-Based Tiers)

```python
@router.get("/api/v1/reports/annual")
@limiter.limit("5/minute;50/hour;500/day")
async def get_annual_report(
    year: int,
    current_user: User = Depends(get_current_user)
):
    """Generate annual report.
    
    Rate limits:
    - 5 requests per minute (burst traffic protection)
    - 50 requests per hour (sustained usage limit)
    - 500 requests per day (daily quota)
    """
    return report_generator.generate_annual(current_user.id, year)
```

## 🎯 Recommended Limits by Endpoint Type

### Authentication Endpoints
```python
- /auth/login       → 5/minute    (prevent brute-force)
- /auth/register    → 3/minute    (prevent spam registration)
- /auth/refresh     → 10/minute   (token refresh is frequent)
```

### Read-Only Endpoints (Safe)
```python
- GET /expenses      → 100/minute
- GET /reports       → 50/minute
- GET /budgets       → 100/minute
```

### Write Operations (Moderate)
```python
- POST /expenses     → 20/minute  (prevent spam)
- PATCH /expenses    → 20/minute
- DELETE /expenses   → 10/minute  (destructive, stricter)
```

### Heavy Operations (Strict)
```python
- /reports/export    → 5/minute   (CPU/memory intensive)
- /batch-import      → 2/minute   (large file processing)
- /generate-pdf      → 3/minute   (PDF generation)
```

## ⚠️ Handling Rate Limit Exceeded (429 Errors)

When a request exceeds the limit, the application returns:

```json
HTTP/1.1 429 Too Many Requests
Content-Type: application/json

{
  "detail": "Rate limit exceeded. Please try again later.",
  "retry_after": "60"  // Seconds to wait before retrying
}
```

### Client-Side Handling (JavaScript Example)

```javascript
async function fetchWithRetry(url, maxRetries = 3) {
  for (let i = 0; i < maxRetries; i++) {
    try {
      const response = await fetch(url);
      
      if (response.status === 429) {
        const retryAfter = response.headers.get('Retry-After') || 60;
        console.warn(`Rate limited. Waiting ${retryAfter} seconds...`);
        await new Promise(resolve => setTimeout(resolve, retryAfter * 1000));
        continue; // Retry
      }
      
      if (!response.ok) throw new Error(`HTTP ${response.status}`);
      return await response.json();
    } catch (error) {
      if (i === maxRetries - 1) throw error;
      await new Promise(resolve => setTimeout(resolve, 2000)); // 2s backoff
    }
  }
}

// Usage
const data = await fetchWithRetry('/api/v1/expenses');
```

### Python Client Example

```python
import time
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

def create_session_with_retry():
    session = requests.Session()
    
    # Retry strategy
    retry_strategy = Retry(
        total=3,
        backoff_factor=2,
        status_forcelist=[429, 500, 502, 503, 504],
    )
    adapter = HTTPAdapter(max_retries=retry_strategy)
    session.mount("http://", adapter)
    session.mount("https://", adapter)
    
    return session

# Usage
session = create_session_with_retry()
response = session.get('http://localhost:8000/api/v1/expenses')
```

## 📊 Monitoring Rate Limits

### Check if Redis is Operating Correctly

```bash
# Connect to Redis
docker-compose exec redis redis-cli -a <REDIS_PASSWORD>

# Monitor rate limit keys
MONITOR

# View all rate limit entries
KEYS slowapi:*

# Check specific IP's quota
GET slowapi:127.0.0.1:/api/v1/expenses

# Expected output format:
# slowapi:127.0.0.1:/api/v1/expenses  →  "5,1234567890"
# (5 requests remaining, expiry timestamp)
```

### Application Logs

```bash
# Watch for rate limit errors
docker-compose logs -f app | grep "Rate limit"

# Expected log entries:
# WARNING Rate limit exceeded for /api/v1/login from 192.168.1.100
# WARNING Rate limit exceeded for /api/v1/expenses/upload from 10.0.0.5
```

### Prometheus Metrics (Optional)

If Prometheus is enabled, monitor:

```
# Requests that hit rate limits
rate_limit_exceeded_total{endpoint="/api/v1/login"}

# Average response time (should stay low)
http_request_duration_seconds{endpoint="/api/v1/health"}
```

## 🔓 Disabling Rate Limits

**For specific endpoints only** (e.g., health checks):

```python
@router.get("/health")
# Note: NO @limiter.limit() decorator
async def health_check():
    """Health check endpoint (no rate limit)."""
    return {"status": "ok"}
```

**Globally** (development only, not recommended for production):

```python
# Set empty limit
limiter = Limiter(key_func=get_remote_address, default_limits=[])
```

## 🎓 Advanced: Custom Rate Limiting

### Rate Limit by User Instead of IP

```python
from slowapi.util import get_remote_address

def get_user_id(request: Request) -> str:
    """Extract user ID from token for user-based limiting."""
    try:
        token = request.headers.get("Authorization", "").split(" ")[1]
        payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        return str(payload.get("sub"))  # User ID
    except:
        return get_remote_address(request)  # Fallback to IP

# Usage
custom_limiter = Limiter(key_func=get_user_id)

@router.get("/api/v1/expensive-operation")
@custom_limiter.limit("10/minute")
async def expensive_operation():
    """Rate limit per user, not per IP."""
    pass
```

### Different Limits for Different Tiers

```python
def get_user_rate_limit(request: Request) -> str:
    """Determine rate limit based on user subscription tier."""
    user = request.state.user  # Set by authentication middleware
    
    tier_limits = {
        "free": "10/minute",
        "premium": "100/minute",
        "enterprise": "1000/minute"
    }
    
    return tier_limits.get(user.subscription_tier, "10/minute")

tier_limiter = Limiter(key_func=get_user_rate_limit)

@router.get("/api/v1/reports")
@tier_limiter.limit(lambda: "depends")
async def generate_report():
    """Rate limit depends on user's subscription tier."""
    pass
```

## ✅ Testing Rate Limits

### Manual Testing

```bash
# Test authentication rate limit (5/min)
for i in {1..10}; do
  echo "Request $i:"
  curl -X POST http://localhost/api/v1/auth/token \
    -H "Content-Type: application/x-www-form-urlencoded" \
    -d "username=test&password=wrong"
  echo ""
  sleep 1
done

# You should see 429 responses after 5 requests
```

### Automated Testing (pytest)

```python
import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_login_rate_limit():
    """Test that login endpoint enforces rate limit."""
    # Make 6 requests (limit is 5/minute)
    for i in range(5):
        response = client.post(
            "/api/v1/auth/token",
            data={"username": "user", "password": "pass"}
        )
        assert response.status_code != 429, f"Unexpected 429 on request {i+1}"
    
    # 6th request should hit the limit
    response = client.post(
        "/api/v1/auth/token",
        data={"username": "user", "password": "pass"}
    )
    assert response.status_code == 429, "Rate limit not enforced"
    assert "Rate limit exceeded" in response.json()["detail"]

def test_report_generation_limit():
    """Test report generation is strictly limited."""
    response = client.get(
        "/api/v1/reports/annual",
        params={"year": 2024},
        headers={"Authorization": "Bearer valid_token"}
    )
    # First request should succeed
    assert response.status_code == 200
    # Subsequent requests quickly should fail
    response = client.get(
        "/api/v1/reports/annual",
        params={"year": 2024},
        headers={"Authorization": "Bearer valid_token"}
    )
    # (depends on configured limit)
```

## 🐛 Common Issues & Solutions

### Issue: Rate Limit Not Taking Effect

**Cause:** Redis connection failed, fell back to in-memory storage.

```bash
# Check Redis is running
docker-compose ps redis

# Verify connectivity
docker-compose logs app | grep "limiter initialized"
# Should see: "Rate limiter initialized with Redis storage"
```

## 🚀 Production Considerations

**Fix:**
```bash
docker-compose restart redis
docker-compose restart app
```

### Issue: All IPs Share the Same Quota

**Cause:** Key function is incorrect.

```python
# ❌ WRONG: counts all users
limiter = Limiter(key_func=lambda request: "global")

# ✓ CORRECT: per IP
limiter = Limiter(key_func=get_remote_address)

# ✓ CORRECT: per user
limiter = Limiter(key_func=get_user_id)
```

### Issue: Legitimate Users Getting 429 Errors

**Cause:** Limits too strict.

```python
# Increase burst or window size
@limiter.limit("50/minute;500/hour")  # Add hourly quota
async def endpoint():
    pass
```

## 🚀 Production Considerations

1. **Monitor Redis Memory**: Rate limit keys can accumulate
   ```bash
   redis-cli INFO memory
   redis-cli FLUSHDB  # Clear if needed (warning: deletes all data)
   ```

2. **Set Expiration**: Keys auto-expire, but verify
   ```bash
   redis-cli TTL slowapi:127.0.0.1:/api/v1/login
   ```

3. **Scale with Load**: If adding more app instances, Redis remains singleton
   ```yaml
   # All instances share same Redis for unified quota
   services:
     app-1:
       env: REDIS_URL=redis://shared-redis:6379
     app-2:
       env: REDIS_URL=redis://shared-redis:6379
   ```

4. **DDoS Mitigation**: Combine with Nginx limits
   - Nginx: 100 req/min general, 20 req/min auth
   - App: More granular per-endpoint limits
   - Firewall: Connection limits at OS level

## 📚 References

- [slowapi Documentation](https://github.com/laurenceisla/slowapi)
- [Redis Documentation](https://redis.io/docs/)
- [FastAPI Security](https://fastapi.tiangolo.com/advanced/security/)
- [Nginx Rate Limiting](https://nginx.org/en/docs/http/ngx_http_limit_req_module.html)

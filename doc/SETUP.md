# Initial Setup & Firewall Configuration

## When to Run firewall-rules.sh

**Timing: RUN ONCE, BEFORE docker-compose up**

The `firewall-rules.sh` script must be executed **on the host machine** before launching the Docker containers. This is a **one-time setup** action that:

1. Enables the UFW firewall
2. Sets default drop policies
3. Allows SSH, HTTP, HTTPS traffic
4. **Blocks direct access** to FastAPI (8000) and Redis (6379) ports
5. Optional: Applies nftables advanced rate limiting

### Why This Order?

```
1. sudo bash firewall-rules.sh      ← FIRST: Lock down the host
2. docker-compose up -d             ← SECOND: Start services (behind firewall)
3. All traffic → Nginx → FastAPI    ← Result: Protected architecture
```

If you run docker-compose **before** firewall-rules.sh, ports will be exposed to the internet briefly until the firewall is configured.

## Setup Checklist

### Step 1: Prepare Environment

```bash
cd /path/to/DEMO_FastAPI

# Generate strong SECRET_KEY
SECRET_KEY=$(openssl rand -hex 32)
echo "Generated SECRET_KEY: $SECRET_KEY"

# Copy and customize environment
cp .env.docker .env.docker.prod
nano .env.docker.prod

# Update in .env.docker.prod:
# - SECRET_KEY=<paste-generated-value>
# - REDIS_PASSWORD=<strong-random-password>
# - DATABASE_URL=<your-database-url>
```

### Step 2: Apply Firewall Rules (Host OS)

Run this **on the host machine, before starting containers**:

```bash
# Make script executable
chmod +x firewall-rules.sh

# Run with sudo (required for firewall)
sudo bash firewall-rules.sh

# Verify rules were applied
sudo ufw status numbered

# Expected output:
#  To                         Action      From
#  --                         ------      ----
# 22/tcp                     ALLOW       Anywhere
# 80/tcp                     ALLOW       Anywhere
# 443/tcp                    ALLOW       Anywhere
# 8000/tcp                   DENY        Anywhere
# 6379/tcp                   DENY        Anywhere
# 6379/udp                   DENY        Anywhere
```

### Step 3: Start Docker Services

Now it's safe to start the containers (they're behind the firewall):

```bash
# Load environment variables
export $(cat .env.docker.prod | xargs)

# Start services
docker-compose up -d

# Verify all services started
docker-compose ps

# Expected output:
# NAME         COMMAND                 STATE
# demo_redis   redis-server ...        Up (healthy)
# demo_nginx   nginx ...               Up (healthy)
# demo_app     python -m uvicorn ...   Up (healthy)
```

### Step 4: Verify Everything Works

```bash
# Test Nginx → FastAPI path (should work)
curl -i http://localhost/health
# Expected: 200 OK

# Test Redis connectivity (from app container)
docker-compose exec app python -c "
from redis import Redis
import os
redis_url = os.getenv('REDIS_URL', 'redis://:change_me@redis:6379')
r = Redis.from_url(redis_url)
print('Redis ping:', r.ping())
"
# Expected: Redis ping: True

# Check app logs for slowapi initialization
docker-compose logs app | grep -i "limiter initialized"
# Expected: "Rate limiter initialized with Redis storage"
```

### Step 5: Monitor & Backup

```bash
# Monitor logs initially
docker-compose logs -f

# Create regular backups
docker-compose exec redis redis-cli SAVE
docker exec demo_redis cp /data/dump.rdb /backups/

# Check Redis memory usage
docker-compose exec redis redis-cli INFO memory
```

## Firewall Details

### What firewall-rules.sh Does

**UFW Configuration:**
- Enables UFW firewall with drop-by-default policy
- Allows SSH (22/tcp) — critical, prevents lockout
- Allows HTTP (80/tcp) — Nginx public interface
- Allows HTTPS (443/tcp) — Nginx public interface
- Denies FastAPI (8000/tcp) — only accessible via Nginx
- Denies Redis (6379/tcp+udp) — internal only

**Optional nftables Rules:**
- TCP SYN flood protection (limit 25/sec)
- ICMP echo (ping) rate limiting (limit 5/sec)
- Connection state tracking

### Modifying Firewall Rules

If you need to adjust rules after running the script:

```bash
# List all rules
sudo ufw status numbered

# Delete a rule
sudo ufw delete 5  # Delete rule number 5

# Add a custom rule
sudo ufw allow from 192.168.1.0/24 to any port 80  # Allow subnet

# Reload
sudo systemctl restart ufw

# View verbose status
sudo ufw status verbose
```

### Emergency: Temporarily Disable Firewall

⚠️ **WARNING:** Only for debugging, not for production

```bash
sudo ufw disable

# Do your debugging...

# Re-enable
sudo ufw enable
```

## Troubleshooting Setup

### Issue: Connection Timeout on First Access

**Symptom:** `curl http://localhost/health` hangs or times out

**Cause:** Firewall still initializing or rules not fully applied

**Fix:**
```bash
# Check firewall status
sudo ufw status

# Force reload
sudo ufw disable && sudo ufw enable

# Check if Nginx is actually running
docker-compose ps nginx

# Check Nginx logs
docker-compose logs nginx
```

### Issue: "Cannot Connect to Docker Daemon"

**Symptom:** `docker-compose ps` fails with permission error

**Cause:** User not in docker group

**Fix:**
```bash
# Add your user to docker group
sudo usermod -aG docker $USER

# Apply group change (logout and login, or run)
newgrp docker

# Test
docker ps
```

### Issue: Port 80/443 Already in Use

**Symptom:** `docker-compose up` fails with "Address already in use"

**Cause:** Another service using the ports (web server, reverse proxy, etc.)

**Fix:**
```bash
# Find what's using port 80
sudo lsof -i :80
# or
sudo netstat -tlnp | grep :80

# Stop the conflicting service
sudo systemctl stop apache2  # or nginx, etc.

# Then start docker-compose
docker-compose up -d
```

### Issue: "sudo bash firewall-rules.sh" Fails

**Symptom:** `ufw: command not found` or permission errors

**Cause:** UFW not installed or running as wrong user

**Fix:**
```bash
# Install UFW (Ubuntu/Debian)
sudo apt-get update
sudo apt-get install ufw

# Verify sudo works
sudo whoami
# Should return: root

# Try script again
sudo bash firewall-rules.sh
```

### Issue: Docker Containers Can't Reach Each Other

**Symptom:** App container can't connect to Redis

**Cause:** Firewall blocking internal traffic or Docker network misconfigured

**Check:**
```bash
# Verify Docker network
docker network inspect demo_fastapi_demo_network

# Test connectivity from app to redis
docker-compose exec app ping redis

# If ping fails, restart networking
docker-compose down
docker-compose up -d
```

## Production Deployment

### Deploying to a Remote Server

```bash
# 1. SSH into server
ssh user@production.server.com

# 2. Clone repo
git clone <repo-url>
cd DEMO_FastAPI

# 3. Apply firewall rules FIRST
sudo bash firewall-rules.sh

# 4. Configure environment
cp .env.docker .env.prod
# Edit with real values
nano .env.prod

# 5. Start services
export $(cat .env.prod | xargs)
docker-compose up -d

# 6. Verify
curl https://production.server.com/health
```

### Multi-Server Setup (Optional)

For horizontal scaling with separate Redis server:

```yaml
# docker-compose.yml
services:
  app:
    environment:
      REDIS_URL: "redis://:password@redis.internal.server:6379"
      # Don't include redis service here
```

```bash
# On redis server
docker run -d --name redis \
  -p 6379:6379 \
  redis:7-alpine redis-server \
  --requirepass your_password

# On app servers  
docker-compose up -d  # Multiple app instances
```

## Monitoring After Setup

```bash
# Check system resource usage
docker stats

# Monitor logs in real-time
docker-compose logs -f --tail=100

# Check firewall stats
sudo ufw show added

# Monitor network connections
sudo netstat -tlnp | grep -E ':(80|443|6379|8000)'
```

## Next Steps

After successful setup:

1. **Test the API** — See endpoints at http://localhost/docs (Swagger UI)
2. **Configure rate limits** — See [doc/RATE_LIMITING.md](./RATE_LIMITING.md)
3. **Deploy to production** — See [doc/DEPLOYMENT.md](./DEPLOYMENT.md)
4. **Enable SSL/TLS** — Uncomment cert lines in `nginx/nginx.conf`
5. **Setup monitoring** — Add Prometheus/Grafana for metrics
6. **Backup strategy** — Automate Redis + database backups

## References

- [UFW Documentation](https://ubuntu.com/server/docs/ufw)
- [Docker Compose Networking](https://docs.docker.com/compose/networking/)
- [Nginx Security](https://nginx.org/en/docs/)
- [Redis Security](https://redis.io/topics/security)

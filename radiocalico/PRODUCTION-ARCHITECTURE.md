# Production Architecture & Security Best Practices

Complete guide to Radio Calico's production deployment architecture and security considerations.

---

## Production Network Architecture

### Correct Production Setup (Secure)

```
┌─────────────────────────────────────────────────────────────┐
│                      Internet (Public)                      │
└─────────────────────┬───────────────────────────────────────┘
                      │
                      │ HTTP/HTTPS Port 80 (EXPOSED)
                      ▼
┌─────────────────────────────────────────────────────────────┐
│                    Nginx Reverse Proxy                      │
│                  (radiocalico-nginx container)              │
│  - Rate limiting                                            │
│  - Security headers (X-Frame-Options, X-XSS-Protection)    │
│  - SSL/TLS termination (if configured)                      │
│  - Request routing                                          │
└─────────────────────┬───────────────────────────────────────┘
                      │
                      │ TCP Port 5000 (INTERNAL Docker network only)
                      │ NOT exposed to host machine
                      ▼
┌─────────────────────────────────────────────────────────────┐
│                   Flask Application                         │
│              (radiocalico-prod container)                   │
│  - Gunicorn with 4 workers                                  │
│  - Health checks enabled                                    │
│  - Only accessible via Docker network                       │
└─────────────────────┬───────────────────────────────────────┘
                      │
                      │ TCP Port 5432 (INTERNAL Docker network only)
                      │
                      ▼
┌─────────────────────────────────────────────────────────────┐
│                   PostgreSQL Database                       │
│              (radiocalico-postgres container)               │
│  - NOT exposed to host machine                              │
│  - Only accessible via Docker network                       │
└─────────────────────────────────────────────────────────────┘
```

### What Ports Are Exposed?

| Port | Protocol | Container | Exposed To | Security |
|------|----------|-----------|------------|----------|
| 80 | HTTP | Nginx | Public (Internet) | ✅ Proxy layer, rate limited |
| 443 | HTTPS | Nginx | Public (Internet) | ✅ Encrypted, proxy layer |
| 5000 | TCP | Flask (Gunicorn) | **Internal Docker network ONLY** | ✅ Not exposed |
| 5432 | TCP | PostgreSQL | **Internal Docker network ONLY** | ✅ Not exposed |

**Key principle:** Only the reverse proxy (Nginx) is exposed to the public internet. All application services are internal.

---

## Port Exposure Explained

### docker-compose.prod.yml Port Configuration

**Correct (as implemented):**
```yaml
radiocalico:  # Flask app
  expose:
    - "5000"  # Available internally, NOT exposed to host
  # No 'ports' section = not accessible from outside Docker network

nginx:  # Reverse proxy
  ports:
    - "80:80"  # ONLY this is exposed to public
```

**Why?**
- `expose` — Makes port available to other containers in the same network (internal only)
- `ports` — Maps container port to host port (exposes to Internet/localhost)

### Incorrect Setup (Security Risk)

```yaml
# ❌ DON'T DO THIS
radiocalico:
  ports:
    - "5000:5000"  # Exposes Flask directly to host machine!
```

**Why this is bad:**
- Direct access to application bypasses Nginx security layer
- Bypasses rate limiting
- Bypasses security headers
- Exposes internal ports unnecessarily
- Makes Nginx routing irrelevant

---

## Recent Fix

### What Changed

**Before (Incorrect):**
```yaml
radiocalico:
  ports:
    - "5000:5000"  # ❌ Exposed directly
```

**After (Correct):**
```yaml
radiocalico:
  expose:
    - "5000"  # ✅ Internal only
  # No 'ports' section
```

### Impact

| Scenario | Before | After |
|----------|--------|-------|
| `localhost:80` | ✅ Works (via Nginx) | ✅ Works (via Nginx) |
| `localhost:5000` | ✅ Works (direct Flask) | ❌ Not accessible |
| Internal to Nginx | ✅ Works | ✅ Works |
| Security | ⚠️ Risky (bypass Nginx) | ✅ Secure (forced through Nginx) |

### Why This is Better

1. **Security** — Flask only accessible through Nginx security layer
2. **Enforcement** — Forces all traffic through rate limiting and security headers
3. **Best Practice** — Matches standard production architectures
4. **Clarity** — Explicit that Nginx is the only entry point
5. **Compliance** — Follows containerization best practices

---

## Production Security Layers

### Layer 1: Network (Docker)
```
Internal Docker network (radiocalico-network)
  └─ Only containers in this network can communicate
  └─ PostgreSQL: Port 5432 (internal only)
  └─ Flask: Port 5000 (internal only)
  └─ Nginx can reach both
```

### Layer 2: Nginx Reverse Proxy
```
Port 80 (public)
  └─ Rate limiting (10 req/s general, 100 req/s API)
  └─ Security headers (X-Frame-Options, X-XSS-Protection, CSP)
  └─ Request routing to Flask
  └─ SSL/TLS termination (if configured)
  └─ Static file caching
```

### Layer 3: Flask Application
```
Port 5000 (internal Docker network only)
  └─ CSRF protection (Flask-WTF)
  └─ Input validation
  └─ SQL injection prevention (SQLAlchemy ORM)
  └─ XSS prevention (Jinja2 auto-escaping)
  └─ Session management
  └─ Health checks
```

### Layer 4: Database
```
Port 5432 (internal Docker network only)
  └─ PostgreSQL auth (username/password)
  └─ No public exposure
  └─ Connection only from Flask
```

---

## Port Access Verification

### Verify Correct Setup

**After fix, these should work:**
```bash
# ✅ Public access (should work)
curl http://localhost/              # Via Nginx
curl http://localhost/api/health    # Via Nginx

# ❌ Direct Flask access (should NOT work)
curl http://localhost:5000/         # Connection refused (correct!)
curl http://localhost:5000/api/health  # Connection refused (correct!)
```

**Why**:
- Port 80 (Nginx) is exposed → accessible
- Port 5000 (Flask) is NOT exposed → not accessible
- This is the correct production behavior

### Check Docker Configuration

```bash
# Verify ports
docker-compose -f docker-compose.prod.yml ps
# Should show:
# - nginx: 0.0.0.0:80→80/tcp (EXPOSED TO PUBLIC)
# - radiocalico: (no port mapping, INTERNAL only)
# - postgres: (no port mapping, INTERNAL only)

# Verify network
docker network inspect radiocalico_radiocalico-network
# Shows all three containers connected

# Verify Flask is NOT publicly accessible
docker ps | grep radiocalico-prod
# Port mapping should show nothing (or empty)
```

---

## Development vs Production Architecture

### Development (docker-compose.yml)

```yaml
radiocalico-dev:
  ports:
    - "5000:5000"  # ✅ OK in dev: direct access for debugging
```

**Why different:**
- Development needs direct Flask access for debugging
- Hot reload requires direct access
- Security headers less critical
- Rate limiting not needed for one developer
- No reverse proxy required

### Production (docker-compose.prod.yml)

```yaml
radiocalico:
  expose:
    - "5000"  # ✅ Correct: internal only, via Nginx
nginx:
  ports:
    - "80:80"  # ✅ Only external port
```

**Why different:**
- Production needs security layers
- Reverse proxy handles requests
- Rate limiting protects against abuse
- Security headers required
- Flask never exposed directly

---

## Nginx Configuration

### nginx.conf (Rate Limiting & Security)

```nginx
# Rate limiting
limit_req_zone $binary_remote_addr zone=general:10m rate=10r/s;
limit_req_zone $binary_remote_addr zone=api:10m rate=100r/s;

# Security headers
add_header X-Frame-Options "SAMEORIGIN" always;
add_header X-XSS-Protection "1; mode=block" always;
add_header X-Content-Type-Options "nosniff" always;
add_header Referrer-Policy "no-referrer-when-downgrade" always;

# Forward requests to internal Flask
upstream flask_app {
    server radiocalico:5000;  # Uses internal Docker network
}

server {
    listen 80;
    location / {
        limit_req zone=general burst=20 nodelay;
        proxy_pass http://flask_app;
    }
    location /api {
        limit_req zone=api burst=50 nodelay;
        proxy_pass http://flask_app;
    }
}
```

**Key points:**
- `upstream flask_app` references `radiocalico:5000` (internal Docker hostname)
- Does NOT use `localhost:5000` (would bypass Docker network)
- Enforces rate limits before reaching Flask
- Adds security headers to all responses

---

## Common Mistakes & How to Avoid Them

### ❌ Mistake 1: Exposing Flask Directly

```yaml
# BAD
radiocalico:
  ports:
    - "5000:5000"  # Allows direct bypass of Nginx
```

**Why bad:**
- Nginx security layers are bypailable
- Rate limiting can be circumvented
- Security headers not applied
- Defeats purpose of reverse proxy

**Fix:**
```yaml
# GOOD
radiocalico:
  expose:
    - "5000"  # Internal only
```

### ❌ Mistake 2: Exposing Database

```yaml
# BAD
postgres:
  ports:
    - "5432:5432"  # Anyone with network access can connect!
```

**Why bad:**
- Direct database access without app logic
- Bypasses input validation
- SQL injection becomes easier
- Compliance violation

**Fix:**
```yaml
# GOOD
postgres:
  # No 'ports' section - internal only
```

### ❌ Mistake 3: Localhost in Nginx Config

```nginx
# BAD
upstream flask_app {
    server localhost:5000;  # Doesn't work in Docker!
}
```

**Why bad:**
- Inside Docker container, `localhost` means the container itself
- Flask is in a different container
- Connection fails

**Fix:**
```nginx
# GOOD
upstream flask_app {
    server radiocalico:5000;  # Uses Docker network DNS
}
```

---

## Verification Checklist

### After Starting Production

```bash
# 1. Verify Nginx is accessible
✅ curl http://localhost/api/health
   Expected: {"status":"ok"}

✅ curl http://localhost:80/
   Expected: Homepage

# 2. Verify Flask is NOT directly accessible
❌ curl http://localhost:5000/api/health
   Expected: Connection refused (correct!)

❌ curl http://localhost:5000/
   Expected: Connection refused (correct!)

# 3. Verify PostgreSQL is NOT directly accessible
❌ psql -h localhost -U radiocalico radiocalico
   Expected: Connection refused (correct!)

# 4. Check Docker containers
✅ docker-compose -f docker-compose.prod.yml ps
   Should show three containers running

# 5. Check port mappings
✅ docker ps --format "table {{.Names}}\t{{.Ports}}"
   radiocalico-nginx: 0.0.0.0:80→80
   radiocalico-prod: (empty)
   radiocalico-postgres: (empty)

# 6. Test rate limiting
# Make 15 rapid requests to API
for i in {1..15}; do curl http://localhost/api/health; done
# Requests 11-15 should be rate limited (429 Too Many Requests)
```

---

## Debugging Production Issues

### Problem: "Connection refused" on localhost:5000

**Expected behavior** (not a problem):
```bash
curl http://localhost:5000/
# curl: (7) Failed to connect to localhost port 5000: Connection refused
```

**Why:** Port 5000 is intentionally not exposed. This is correct!

**Access application correctly:**
```bash
curl http://localhost/        # Use port 80
curl http://localhost:80/     # Explicitly use Nginx port
```

### Problem: "Connection refused" on localhost:80

**This IS a problem** — Nginx not responding.

**Diagnose:**
```bash
# Check if Nginx is running
docker ps | grep nginx

# Check Nginx logs
docker logs radiocalico-nginx

# Verify Docker network
docker network inspect radiocalico_radiocalico-network

# Restart production
make prod-stop
make prod
sleep 5
make health
```

### Problem: Nginx shows "502 Bad Gateway"

**Cause:** Flask not running or not responding

**Diagnose:**
```bash
# Check Flask container
docker ps | grep radiocalico-prod

# Check Flask logs
docker logs radiocalico-prod

# Check health
docker exec radiocalico-prod curl http://localhost:5000/api/health

# Restart
make prod-stop
make prod
sleep 5
curl http://localhost/api/health
```

---

## Summary: Production vs Development

| Aspect | Development | Production |
|--------|-------------|-----------|
| **Flask Port** | `ports: "5000:5000"` (exposed) | `expose: "5000"` (internal) |
| **Nginx** | Not used | Port 80 (exposed) |
| **Security** | Debug mode enabled | Debug mode disabled |
| **Access** | Direct or via dev server | Only through Nginx |
| **Rate Limiting** | No | Yes (Nginx) |
| **Database Port** | Exposed (for dev) | Internal only |
| **Use Case** | Development, debugging | Production, public internet |

---

## Best Practices Checklist

✅ **Do:**
- [ ] Use reverse proxy (Nginx) in production
- [ ] Expose only Nginx port (80/443)
- [ ] Keep Flask port internal (Docker network only)
- [ ] Keep database port internal
- [ ] Implement rate limiting (Nginx)
- [ ] Add security headers (Nginx)
- [ ] Use environment variables for secrets
- [ ] Monitor container logs
- [ ] Verify ports before deploying

❌ **Don't:**
- [ ] Expose Flask port directly in production
- [ ] Expose database port
- [ ] Skip reverse proxy
- [ ] Use debug mode in production
- [ ] Hardcode secrets
- [ ] Ignore security headers
- [ ] Skip rate limiting
- [ ] Use localhost in Nginx config (inside Docker)

---

## Related Documentation

- [DOCKER-IMAGE-MANAGEMENT.md](DOCKER-IMAGE-MANAGEMENT.md) — Image building and deployment
- [DATABASE-MANAGEMENT.md](DATABASE-MANAGEMENT.md) — Database backup and cleanup
- [CLAUDE.md](CLAUDE.md) — Development guide
- [DOCKER.md](DOCKER.md) — Docker setup and configuration

---

## Key Takeaway

**Production Security Principle:**
```
Public Internet
      ↓
   Port 80/443
      ↓
  Nginx (Security Layer)
      ↓
  Port 5000 (Internal Only)
      ↓
   Flask App
```

**Never expose application ports directly. Always route through a reverse proxy.**

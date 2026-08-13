# Docker Deployment Guide - Radio Calico

This guide covers containerizing and deploying the Radio Calico application using Docker with both development and production configurations.

## Overview

The Docker setup includes:
- **Development Image**: Flask with hot-reload, debug mode, SQLite database, all dev dependencies
- **Production Image**: Optimized with Gunicorn, minimal dependencies, non-root user
- **PostgreSQL 16**: Production database (Alpine Linux, health-checked, internal only)
- **Nginx Reverse Proxy**: Production-grade reverse proxy on port 80 (only external port)
- **Docker Compose**: Orchestration for both dev and prod environments
- **Health Checks**: PostgreSQL readiness check + Flask HTTP health check
- **Security Architecture**: See [PRODUCTION-ARCHITECTURE.md](PRODUCTION-ARCHITECTURE.md) for detailed port exposure and security best practices

## Architecture

```
Development:
┌─────────────────────────┐
│  docker-compose.yml     │
│  ┌───────────────────┐  │
│  │  radiocalico:dev  │  │
│  │  Flask + Reload   │  │
│  │  Port 5000        │  │
│  └───────────────────┘  │
└─────────────────────────┘

Production:
┌─────────────────────────────────────────┐
│  docker-compose.prod.yml                │
│  ┌──────────────────────────────────┐   │
│  │  nginx (reverse proxy)           │   │
│  │  Port 80/443                     │   │
│  │  ├─ SSL/TLS termination          │   │
│  │  ├─ Rate limiting                │   │
│  │  └─ Static file caching          │   │
│  └────────────┬─────────────────────┘   │
│               │                         │
│  ┌────────────▼─────────────────────┐   │
│  │  radiocalico:prod (x4 workers)   │   │
│  │  Gunicorn + Flask                │   │
│  │  Port 5000 (internal)            │   │
│  │  Health check enabled            │   │
│  └────────────┬─────────────────────┘   │
│               │                         │
│  ┌────────────▼─────────────────────┐   │
│  │  radiocalico-data (volume)       │   │
│  │  Persistent SQLite database      │   │
│  └──────────────────────────────────┘   │
└─────────────────────────────────────────┘
```

## Prerequisites

- Docker 20.10+ ([install](https://docs.docker.com/get-docker/))
- Docker Compose 2.0+ ([install](https://docs.docker.com/compose/install/))
- Git

## Quick Start

### Development Mode (with hot reload)

```bash
# Option 1: Using provided script
./docker-run.sh dev

# Option 2: Using docker compose directly
docker compose up

# Option 3: Building first, then running
docker build --target=dev -t radiocalico:dev .
docker run -it -p 5000:5000 -v $(pwd):/app radiocalico:dev
```

**Access**: 
- **http://localhost:5000** ← Recommended
- **http://127.0.0.1:5000** ← Also works (same as localhost)

Both URLs are equivalent on your local machine. Use whichever you prefer.

**Features**:
- Flask debug mode enabled
- Auto-reload on code changes
- Full dev dependencies (pytest, coverage, etc.)
- All test files included

### Production Mode (with Nginx)

⚠️ **REQUIRED: Set DB_PASSWORD environment variable BEFORE starting**

```bash
# STEP 1: Generate a secure password (MUST DO THIS)
export DB_PASSWORD=$(openssl rand -base64 32)
echo "Save this password securely: $DB_PASSWORD"

# STEP 2: Verify password is set
echo $DB_PASSWORD  # Should output your secure password, NOT empty

# STEP 3: Start production stack
# Option A: Using docker compose directly (requires DB_PASSWORD exported)
docker compose -f docker-compose.prod.yml up -d

# Option B: Using .env file (copy .env.production.example)
cp .env.production.example .env.production
# Edit .env.production and set DB_PASSWORD
docker compose -f docker-compose.prod.yml --env-file .env.production up -d
```

**Access**: 
- **http://localhost** ← Recommended
- **http://127.0.0.1** ← Also works (same as localhost)

Both URLs are equivalent on your local machine. Nginx serves on port 80 (HTTP only in this setup).

**Features**:
- Gunicorn with 4 workers
- Nginx reverse proxy
- Health checks every 30 seconds
- Persistent data volume
- Non-root user (security)
- Gzip compression
- Rate limiting
- Security headers

## Localhost vs 127.0.0.1 - No Conflict

Both `localhost` and `127.0.0.1` work interchangeably on your local machine. They refer to the same address (loopback interface). You can freely use either one.

### URL Compatibility Across Deployments

| Deployment | Port | URLs that work |
|---|---|---|
| **Non-Docker** (native Flask) | 5000 | `http://localhost:5000` and `http://127.0.0.1:5000` |
| **Docker Dev** (docker compose up) | 5000 | `http://localhost:5000` and `http://127.0.0.1:5000` |
| **Docker Prod** (docker compose -f docker-compose.prod.yml up) | 80 | `http://localhost` and `http://127.0.0.1` |

**Key Point**: The Flask app binds to `0.0.0.0`, which means it listens on all interfaces including both `127.0.0.1` and `localhost`. You can switch between the three deployment modes without changing your URL preferences.

**Example**: If you prefer using `127.0.0.1:5000`, you can:
1. Run non-Docker: `python run.py` → access at `http://127.0.0.1:5000`
2. Run Docker dev: `docker compose up` → access at `http://127.0.0.1:5000` (also works)
3. Switch back to non-Docker anytime → access at `http://127.0.0.1:5000`

No port conflicts, no state issues. Each mode has its own containers/processes.

## Building Images

**⚡ Auto-Build vs. Explicit Build:**
- `make dev` — Auto-builds image if missing (recommended for normal development)
- `make build` — Always builds both images explicitly (when you need guaranteed fresh builds)

For complete guide on when to build images and what triggers rebuilds, see **[DOCKER-IMAGE-MANAGEMENT.md](DOCKER-IMAGE-MANAGEMENT.md)**.

### Build both dev and prod images

```bash
# Using Makefile (recommended)
make build

# Using docker build directly
docker build --target=dev -t radiocalico:dev .
docker build --target=prod -t radiocalico:prod .

# With cache disabled (fresh build)
docker build --no-cache --target=dev -t radiocalico:dev .
docker build --no-cache --target=prod -t radiocalico:prod .
```

### Build individual images

```bash
# Development image only
make build-dev
# or
docker build --target=dev -t radiocalico:dev .

# Production image only
make build-prod
# or
docker build --target=prod -t radiocalico:prod .
```

**When to use explicit build:** After changing `requirements.txt`, `Dockerfile`, Python version, or base image. See [DOCKER-IMAGE-MANAGEMENT.md](DOCKER-IMAGE-MANAGEMENT.md) for complete decision tree.

### View built images

```bash
docker images radiocalico

REPOSITORY      TAG        IMAGE ID        CREATED         SIZE
radiocalico     dev        abc123def456    2 minutes ago    520MB
radiocalico     prod       xyz789ghi012    2 minutes ago    380MB
```

**Note**: Both build stages automatically minify CSS and HTML assets during the build process (via `python scripts/minify.py`), reducing file sizes by ~20% on CSS and 5-22% on HTML templates. For manual minification before committing, use `make minify` or `make minify-watch`. See [MINIFICATION.md](MINIFICATION.md) for details.

## Running Containers

### Development

```bash
# Start with compose (includes logs)
docker compose up

# Start with compose in background
docker compose up -d

# View logs
docker compose logs -f

# Run tests
docker compose exec radiocalico-dev pytest tests/

# Stop
docker compose down
```

### Production

```bash
# Start with compose
docker compose -f docker-compose.prod.yml up -d

# View logs
docker compose -f docker-compose.prod.yml logs -f radiocalico

# Check health
docker compose -f docker-compose.prod.yml ps

# Stop
docker compose -f docker-compose.prod.yml down
```

### Direct Docker commands

```bash
# Development
docker run -it \
  -p 5000:5000 \
  -v $(pwd):/app \
  -e FLASK_ENV=development \
  radiocalico:dev

# Production
docker run -d \
  --name radiocalico \
  --restart always \
  -p 5000:5000 \
  -v radiocalico-data:/app/instance \
  radiocalico:prod

# Stop and remove
docker stop radiocalico
docker rm radiocalico
```

## Configuration

### Environment Variables

**Development** (docker-compose.yml):
```yaml
- FLASK_APP=run.py
- FLASK_ENV=development
- FLASK_DEBUG=1
```

**Production** (docker-compose.prod.yml):
```yaml
- FLASK_ENV=production
- FLASK_DEBUG=0
```

### Ports

- **Development**: 5000 (direct Flask, accessible as http://localhost:5000 or http://127.0.0.1:5000)
- **Production**: 
  - 80 (HTTP, accessible as http://localhost or http://127.0.0.1)
  - 5000 (internal Flask, not exposed)

### Volumes

**Development**:
- `.:/app` - Mount entire project for hot reload
- `/app/venv` - Exclude venv (use container's version)
- `/app/instance` - SQLite database file

**Production**:
- `radiocalico-db:/var/lib/postgresql/data` - PostgreSQL data persistence

### Database Configuration

**Development** (SQLite):
- File-based database at `instance/radiocalico.db`
- No additional configuration needed
- Auto-creates on first run

**Production** (PostgreSQL 16):
- Container: `radiocalico-postgres`
- Database: `radiocalico`
- User: `radiocalico`
- Password: Set via `DB_PASSWORD` env var (defaults to `radiocalico`)
- Connection: `postgresql://radiocalico:password@postgres:5432/radiocalico`

⚠️ **SECURITY WARNING: Production Database Password**

The default password `radiocalico` is suitable **only for development and testing**. For production deployments, you **MUST** set a strong password via the `DB_PASSWORD` environment variable.

**Generate a secure password:**
```bash
# Option 1: Using OpenSSL (Linux/macOS)
export DB_PASSWORD=$(openssl rand -base64 32)

# Option 2: Using Python
export DB_PASSWORD=$(python3 -c "import secrets; print(secrets.token_urlsafe(32))")

# Option 3: Manually (minimum 32 characters, mix of upper/lower/numbers/special chars)
export DB_PASSWORD="YourV3ryStr0ng!P@ssw0rd#WithSpecialChars"
```

**Start production with secure password:**
```bash
# Before starting, set the password
export DB_PASSWORD=$(openssl rand -base64 32)
echo "Using DB_PASSWORD: $DB_PASSWORD"  # Save this somewhere safe!

# Now start production
docker compose -f docker-compose.prod.yml up -d
```

**Store the password securely:**
- Do NOT commit `.env` files to git (they're in `.gitignore`)
- Use your infrastructure's secret management (e.g., AWS Secrets Manager, HashiCorp Vault)
- For self-hosted, use a `.env.production` file (gitignored) accessible only to deployment scripts
- Consider Docker Secrets or Kubernetes Secrets if using orchestration

**Verify the connection works:**
```bash
# Check if PostgreSQL is healthy
docker compose -f docker-compose.prod.yml ps

# Test the Flask app can connect to PostgreSQL
curl http://localhost/api/health
# Should return: {"status":"ok"}
```

**Changing Password**:
```bash
# Before starting, set environment variable
export DB_PASSWORD=your_secure_password
docker compose -f docker-compose.prod.yml up -d
```

**Database Initialization**:
- Flask automatically creates tables on startup
- Default user seeded: Pankaj Jha (pankaj.psu@gmail.com)
- Data persists in `radiocalico-db` volume

### SSL/TLS (Production - Optional)

The current setup runs Nginx on HTTP (port 80). For production with HTTPS:

**Option 1: Self-signed certificates (testing)**

```bash
# Generate self-signed cert (valid for 365 days)
mkdir -p ssl
openssl req -x509 -newkey rsa:4096 -nodes \
  -out ssl/cert.pem -keyout ssl/key.pem -days 365

# Uncomment HTTPS block in nginx.conf
# Add port 443 to docker-compose.prod.yml ports section
# Restart containers: docker compose -f docker-compose.prod.yml up -d
```

**Option 2: Let's Encrypt (recommended for production)**

```bash
# Install certbot
sudo apt-get install certbot python3-certbot-nginx

# Get certificate
sudo certbot certonly --standalone -d yourdomain.com

# Mount certs in docker-compose.prod.yml:
# volumes:
#   - /etc/letsencrypt/live/yourdomain.com:/etc/nginx/ssl:ro
```

**For this demo setup**, HTTP-only is fine. Upgrade to HTTPS when deploying to production.

## Health Checks

Production containers include automated health checks:

**Health Check Implementation:**
- **Flask App**: Uses Python's built-in `urllib`, checks `/api/health` endpoint every 30 seconds
- **PostgreSQL**: Uses `pg_isready` command every 10 seconds
- Containers show "Up (healthy)" or "Up (unhealthy)" status

**View container health:**

```bash
# Quick status check
docker ps

# Detailed health info with history
docker inspect radiocalico-prod --format='{{json .State.Health}}'
```

**Health Check Endpoints:**

Access these links to verify services are running (requires services to be started):

- **Flask API Health** (internal): [http://localhost:5000/api/health](http://localhost:5000/api/health)
- **Nginx Proxy Health**: [http://localhost/api/health](http://localhost/api/health)
- **Curl command**:
  ```bash
  curl http://localhost/api/health
  # Response: {"status":"ok"}
  ```

**Expected output when healthy:**
```
radiocalico-nginx      Up (healthy)   0.0.0.0:80->80/tcp
radiocalico-prod       Up (healthy)   0.0.0.0:5000->5000/tcp
radiocalico-postgres   Up (healthy)   5432/tcp
```

## Logs and Monitoring

### View logs

```bash
# All services
docker compose logs

# Specific service
docker compose logs radiocalico-dev

# Follow logs in real-time
docker compose logs -f

# Last 100 lines
docker compose logs --tail=100
```

### View resource usage

```bash
# Real-time stats
docker stats radiocalico-dev

# One-time stats
docker stats --no-stream
```

## Troubleshooting

### Container won't start

```bash
# Check logs
docker logs radiocalico-dev

# Check if port is in use
lsof -i :5000

# Kill process on port
kill -9 $(lsof -t -i:5000)
```

### Database issues

```bash
# Reset database (dev only)
docker compose down -v
docker compose up

# Inspect database volume
docker volume ls
docker volume inspect radiocalico_radiocalico-data
```

### Permission denied

```bash
# Fix file permissions
docker compose exec radiocalico-dev chmod 777 instance/

# Or rebuild with correct ownership
docker build --target=prod --no-cache -t radiocalico:prod .
```

### Out of disk space

```bash
# Clean up unused images
docker image prune -a

# Clean up unused volumes
docker volume prune

# Clean up unused networks
docker network prune
```

## Security Best Practices

✅ **Implemented**:
- Non-root user (appuser, UID 1000)
- Minimal attack surface (production image)
- Health checks
- Security headers (nginx)
- SSL/TLS support
- Rate limiting
- HTTPS redirect

✅ **Recommendations**:
- Use strong passwords for any credentials
- Keep images up to date: `docker pull radiocalico:prod`
- Use private registry for sensitive images
- Enable Docker daemon security: `--icc=false`
- Use secrets management for sensitive data
- Regular security audits: `docker scan radiocalico:prod`

## Deployment Strategies

### Single Host

```bash
# Pull and run
docker pull radiocalico:prod
docker compose -f docker-compose.prod.yml up -d
```

### Docker Swarm

```bash
# Initialize swarm
docker swarm init

# Deploy service
docker service create \
  --name radiocalico \
  --publish 5000:5000 \
  --replicas 3 \
  radiocalico:prod
```

### Kubernetes

```bash
# Apply manifests (create k8s/ directory with manifests)
kubectl apply -f k8s/

# Check deployment
kubectl get pods
kubectl get svc
```

### Docker Hub/Private Registry

```bash
# Tag image
docker tag radiocalico:prod docker.io/yourorg/radiocalico:1.0.0

# Push
docker push docker.io/yourorg/radiocalico:1.0.0

# Pull on another host
docker pull docker.io/yourorg/radiocalico:1.0.0
docker run -d docker.io/yourorg/radiocalico:1.0.0
```

## Performance Optimization

### Development

- Hot reload: Changes reflected immediately
- Full debug logging
- Test dependencies included

### Production

- Gunicorn workers: 4 (tune with `--workers N`)
- Gzip compression: Reduces response size by 60-70%
- Caching: Static assets cached for 30 days
- Rate limiting: 10 req/s general, 100 req/s API
- Connection pooling: Persistent HTTP connections

### Scaling

```bash
# Increase Gunicorn workers in docker-compose.prod.yml
command: gunicorn --workers 8 ...

# Or use docker swarm replicas
docker service update --replicas 3 radiocalico
```

## CI/CD Integration

### Docker Build & Test Workflow

Radio Calico includes an automated Docker build and smoke test workflow (`.github/workflows/docker-build.yml`) that runs on every PR and push.

**Workflow Features:**
- ✅ Builds both dev and prod images with layer caching
- ✅ Smoke tests: verifies Flask startup, health endpoints, all services
- ✅ Image verification: confirms Python/Gunicorn versions and non-root user
- ✅ PR comments: posts build status and detailed results

**When it runs:**
- On push to `main` branch
- On pull requests to `main` branch
- Manual trigger via GitHub Actions UI
- Only when Docker-related files change (Dockerfile, docker-compose, nginx.conf, requirements)

**Test Coverage:**
1. **Dev image** — Flask startup + `/api/health` endpoint
2. **Prod image** — All services (Nginx, Flask, PostgreSQL) + health checks
3. **Security** — Verifies non-root user (UID 1000)
4. **Registry** — Logs into GitHub Container Registry (on push to main)

**Example PR Comment:**
```
## 🐳 Docker Build & Test Results

**Build Status**: ✅ PASSED

### Tests Completed
- ✅ Dev image build
- ✅ Prod image build
- ✅ Dev smoke test (health check)
- ✅ Prod smoke test (all services + health check)
- ✅ Image verification (Python, Gunicorn, permissions)

### Access URLs (when running locally)
- **Dev**: http://localhost:5000 (Flask + SQLite)
- **Prod**: http://localhost (Nginx + Gunicorn + PostgreSQL)
```

### Custom GitHub Actions Workflows

Additional workflows in `.github/workflows/`:
- **tests.yml** — Unit tests with pytest (88% coverage gate)
- **claude-code-review.yml** — AI-powered code review
- **claude.yml** — Claude integration responder
- **docker-build.yml** — Docker build and smoke tests (new)

## Maintenance

### Update images

```bash
# Rebuild with latest dependencies
docker build --no-cache -t radiocalico:prod .

# Update running container
docker compose -f docker-compose.prod.yml up -d --force-recreate
```

### Backup database

```bash
# Backup volume
docker run --rm -v radiocalico_radiocalico-data:/data \
  -v $(pwd):/backup \
  busybox tar czf /backup/db-backup.tar.gz /data

# Restore
docker run --rm -v radiocalico_radiocalico-data:/data \
  -v $(pwd):/backup \
  busybox tar xzf /backup/db-backup.tar.gz -C /
```

## Additional Resources

- [Docker Documentation](https://docs.docker.com/)
- [Docker Compose Documentation](https://docs.docker.com/compose/)
- [Gunicorn Documentation](https://gunicorn.org/)
- [Nginx Documentation](https://nginx.org/en/docs/)
- [Flask Documentation](https://flask.palletsprojects.com/)

## Troubleshooting

### Issue: Container exits immediately with import error

**Error message:**
```
ModuleNotFoundError: No module named 'flask_wtf'
```

**Cause:** 
Docker image was built before new dependencies were added to `requirements.txt`

**Fix:**
```bash
# Rebuild the affected image
docker build --target=dev -t radiocalico:dev .    # For dev only
# Or use make:
make build-dev

docker build --target=prod -t radiocalico:prod .  # For prod only
# Or use make:
make prod-build

# Rebuild both (recommended):
docker build --target=dev -t radiocalico:dev . && docker build --target=prod -t radiocalico:prod .
# Or use make (recommended):
make build
```

---

### Issue: 502 Bad Gateway or password authentication failed

**Error message:**
```
FATAL: password authentication failed for user "radiocalico"
```

**Cause:**
- PostgreSQL volume was initialized with a different password
- Flask and PostgreSQL passwords don't match

**Fix:**
```bash
# Stop services
docker compose -f docker-compose.prod.yml down
# Or use make:
make prod-stop

# Remove stale database volume
docker volume rm radiocalico_radiocalico-db

# Set secure password and restart
export DB_PASSWORD=$(openssl rand -base64 32)
docker compose -f docker-compose.prod.yml up -d
# Or use make:
make prod

# Wait for PostgreSQL to initialize (8-10 seconds)
sleep 10

# Verify it works
curl http://localhost/api/health
# Or use make:
make health
# Should return: {"status":"ok"}
```

---

### Issue: Connection refused on startup

**Error message:**
```
connection to server at "postgres" failed: Connection refused
```

**Cause:**
Race condition - Flask starts before PostgreSQL is ready

**Fix:**
Just wait for PostgreSQL to be ready:
```bash
# PostgreSQL health check needs 5-10 seconds
sleep 10
curl http://localhost/api/health
```

If it persists after 30 seconds, check PostgreSQL logs:
```bash
docker compose -f docker-compose.prod.yml logs postgres
# Or use make:
make logs-prod
# (then look for postgres service logs)
```

---

### Issue: Port already in use

**Error message:**
```
bind: address already in use
```

**Cause:**
Another process is using port 5000 (dev) or 80 (prod)

**Fix:**
```bash
# Stop all containers and clean up
docker compose down && docker compose -f docker-compose.prod.yml down
# Or use make:
make stop

# Kill any lingering processes (if needed)
docker kill $(docker ps -q) 2>/dev/null || true

# Restart development
docker compose up
# Or use make:
make dev

# Or restart production
docker compose -f docker-compose.prod.yml up -d
# Or use make:
make prod
```

---

### Issue: Database volume out of sync

**Symptoms:**
- Changes to code don't reflect in database
- Schema mismatches
- Stale data from previous runs

**Fix:**
```bash
# Stop services
docker compose down
# Or use make:
make dev-stop

# For production:
docker compose -f docker-compose.prod.yml down
# Or use make:
make prod-stop

# Remove database volume
docker volume rm radiocalico_radiocalico-db

# Restart - database will be fresh with new initialization
docker compose up
# Or use make:
make dev

# Or for production:
docker compose -f docker-compose.prod.yml up -d
# Or use make:
make prod
```

---

### Issue: Can't connect to container

**Error message:**
```
Error: No such container
```

**Cause:**
Container doesn't exist or has different name

**Fix:**
```bash
# List all containers
docker ps -a

# Check compose status
docker compose ps
# Or use make:
make status

# Check production status
docker compose -f docker-compose.prod.yml ps
# Or use make:
make status

# Restart containers (development)
docker compose up
# Or use make:
make dev

# Or restart production
docker compose -f docker-compose.prod.yml up -d
# Or use make:
make prod
```

---

### Debugging Commands

**View container logs:**
```bash
# Development
docker compose logs -f radiocalico-dev
# Or use make:
make logs-dev

# Production (Flask)
docker compose -f docker-compose.prod.yml logs -f radiocalico
# Or use make:
make logs-prod

# Production (PostgreSQL)
docker compose -f docker-compose.prod.yml logs -f postgres

# Production (Nginx)
docker compose -f docker-compose.prod.yml logs -f nginx
```

**Check environment variables:**
```bash
docker compose -f docker-compose.prod.yml exec radiocalico env | grep DB
docker compose -f docker-compose.prod.yml exec radiocalico env | grep FLASK
```

**Test database connectivity:**
```bash
# From Flask container
docker compose -f docker-compose.prod.yml exec radiocalico python -c \
  "from app import create_app; app = create_app(); print('✅ Database connected')"

# From PostgreSQL container
docker compose -f docker-compose.prod.yml exec postgres pg_isready -U radiocalico
```

**Inspect volumes:**
```bash
# List all volumes
docker volume ls | grep radiocalico

# Inspect volume details
docker volume inspect radiocalico_radiocalico-db
```

**Full reset (nuclear option):**
```bash
# Stop everything
docker compose down && docker compose -f docker-compose.prod.yml down
# Or use make:
make stop

# Remove all volumes
docker volume rm radiocalico_radiocalico-db

# Remove all images
docker rmi radiocalico:dev radiocalico:prod

# Remove all stopped containers
docker container prune

# Start fresh - rebuild images
docker build --target=dev -t radiocalico:dev . && docker build --target=prod -t radiocalico:prod .
# Or use make:
make build

# Start development
docker compose up
# Or use make:
make dev

# Or start production
docker compose -f docker-compose.prod.yml up -d
# Or use make (don't forget to set DB_PASSWORD first):
export DB_PASSWORD=$(openssl rand -base64 32)
make prod
```

---

### When to Rebuild Docker Images

Rebuild Docker images when:
- ✅ Dependencies in `requirements.txt` change (new/updated packages)
- ✅ Python version changes in Dockerfile
- ✅ System packages change (apt-get packages)
- ✅ Base image (Python version) changes
- ✅ After switching git branches with different dependencies

**Rebuild command:**
```bash
# Rebuild both (recommended)
docker build --target=dev -t radiocalico:dev . && docker build --target=prod -t radiocalico:prod .
# Or use make (recommended):
make build

# Or rebuild specific target
docker build --target=dev -t radiocalico:dev .
# Or use make:
make build-dev

# Or for production
docker build --target=prod -t radiocalico:prod .
# Or use make:
make prod-build
```

---

### When to Remove Volumes

Remove database volumes when:
- ✅ Password changes (DB_PASSWORD)
- ✅ Starting with a clean database
- ✅ Testing database initialization
- ✅ Previous initialization failed

**Remove command:**
```bash
docker volume rm radiocalico_radiocalico-db
# Note: After removing, restart with:
# make prod (for production)
# or
# make dev (for development)
```

---

## Support

For issues or questions:
1. Check the Troubleshooting section above
2. View logs: `docker compose logs -f`
3. Check Docker documentation
4. Open an issue on GitHub with:
   - Error message (full output)
   - Steps to reproduce
   - Docker version: `docker --version`
   - Docker Compose version: `docker compose --version`

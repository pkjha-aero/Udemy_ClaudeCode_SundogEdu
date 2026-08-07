# Docker Deployment Guide - Radio Calico

This guide covers containerizing and deploying the Radio Calico application using Docker with both development and production configurations.

## Overview

The Docker setup includes:
- **Development Image**: Flask with hot-reload, debug mode, all dev dependencies
- **Production Image**: Optimized with Gunicorn, minimal dependencies, non-root user
- **Nginx Reverse Proxy**: Production-grade load balancing and SSL termination
- **Docker Compose**: Orchestration for both dev and prod environments
- **Health Checks**: Automatic container health monitoring

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

# Option 2: Using docker-compose directly
docker-compose up

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

```bash
# Option 1: Using provided script
./docker-run.sh prod

# Option 2: Using docker-compose directly
docker-compose -f docker-compose.prod.yml up -d

# Option 3: Building first, then running
docker build --target=prod -t radiocalico:prod .
docker run -d -p 80:80 radiocalico:prod
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
| **Docker Dev** (docker-compose up) | 5000 | `http://localhost:5000` and `http://127.0.0.1:5000` |
| **Docker Prod** (docker-compose -f docker-compose.prod.yml up) | 80 | `http://localhost` and `http://127.0.0.1` |

**Key Point**: The Flask app binds to `0.0.0.0`, which means it listens on all interfaces including both `127.0.0.1` and `localhost`. You can switch between the three deployment modes without changing your URL preferences.

**Example**: If you prefer using `127.0.0.1:5000`, you can:
1. Run non-Docker: `python run.py` → access at `http://127.0.0.1:5000`
2. Run Docker dev: `docker-compose up` → access at `http://127.0.0.1:5000` (also works)
3. Switch back to non-Docker anytime → access at `http://127.0.0.1:5000`

No port conflicts, no state issues. Each mode has its own containers/processes.

## Building Images

### Build both dev and prod images

```bash
./docker-build.sh

# With custom version
./docker-build.sh v1.0.0

# With custom registry
./docker-build.sh v1.0.0 docker.io/yourorg
```

### Build individually

```bash
# Development image only
docker build --target=dev -t radiocalico:dev .

# Production image only
docker build --target=prod -t radiocalico:prod .
```

### View built images

```bash
docker images radiocalico

REPOSITORY      TAG        IMAGE ID        CREATED         SIZE
radiocalico     dev        abc123def456    2 minutes ago    520MB
radiocalico     prod       xyz789ghi012    2 minutes ago    380MB
```

## Running Containers

### Development

```bash
# Start with compose (includes logs)
docker-compose up

# Start with compose in background
docker-compose up -d

# View logs
docker-compose logs -f

# Run tests
docker-compose exec radiocalico-dev pytest tests/

# Stop
docker-compose down
```

### Production

```bash
# Start with compose
docker-compose -f docker-compose.prod.yml up -d

# View logs
docker-compose -f docker-compose.prod.yml logs -f radiocalico

# Check health
docker-compose -f docker-compose.prod.yml ps

# Stop
docker-compose -f docker-compose.prod.yml down
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
- `/app/instance` - Persist database

**Production**:
- `radiocalico-data:/app/instance` - Persist database

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
# Restart containers: docker-compose -f docker-compose.prod.yml up -d
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

Production containers include automated health checks (defined in Dockerfile):

**Health Check Implementation:**
- Uses Python's built-in `urllib` (no external dependencies)
- Checks `/api/health` endpoint every 30 seconds
- Container shows "Up (healthy)" or "Up (unhealthy)" status

**View container health:**

```bash
# Quick status check
docker ps

# Detailed health info with history
docker inspect radiocalico-prod --format='{{json .State.Health}}'

# Manual health check (curl also works)
curl http://localhost:5000/api/health
# Response: {"status": "ok"}
```

**Expected output when healthy:**
```
radiocalico-prod    Up (healthy)   0.0.0.0:5000->5000/tcp
```

## Logs and Monitoring

### View logs

```bash
# All services
docker-compose logs

# Specific service
docker-compose logs radiocalico-dev

# Follow logs in real-time
docker-compose logs -f

# Last 100 lines
docker-compose logs --tail=100
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
docker-compose down -v
docker-compose up

# Inspect database volume
docker volume ls
docker volume inspect radiocalico_radiocalico-data
```

### Permission denied

```bash
# Fix file permissions
docker-compose exec radiocalico-dev chmod 777 instance/

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
docker-compose -f docker-compose.prod.yml up -d
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

### GitHub Actions Example

```yaml
name: Build and Push Docker Image
on: [push]
jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Build image
        run: docker build -t radiocalico:${{ github.sha }} .
      
      - name: Push to registry
        run: docker push radiocalico:${{ github.sha }}
      
      - name: Deploy
        run: docker-compose -f docker-compose.prod.yml up -d
```

## Maintenance

### Update images

```bash
# Rebuild with latest dependencies
docker build --no-cache -t radiocalico:prod .

# Update running container
docker-compose -f docker-compose.prod.yml up -d --force-recreate
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

## Support

For issues or questions:
1. Check logs: `docker-compose logs -f`
2. Review this guide's Troubleshooting section
3. Check Docker documentation
4. Open an issue on GitHub

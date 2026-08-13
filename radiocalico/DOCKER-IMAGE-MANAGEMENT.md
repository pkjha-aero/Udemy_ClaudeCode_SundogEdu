# Docker Image Management Guide

Complete reference for when Docker images are built vs. used in Radio Calico development and deployment workflows.

---

## Quick Reference

### Auto-Build Commands (Build if missing, use if exists)
```bash
make dev              # ✅ AUTO-BUILD + RUN (dev image)
make prod             # ✅ AUTO-BUILD + RUN (prod image)
docker compose up     # ✅ AUTO-BUILD + RUN (dev image)
```

### Explicit Build Commands (Always build)
```bash
make build            # ✅ BUILD BOTH (dev + prod)
make build-dev        # ✅ BUILD DEV ONLY
make build-prod       # ✅ BUILD PROD ONLY
make prod-build       # ✅ BUILD PROD ONLY (alias for build-prod)
docker build --target=dev ...  # ✅ BUILD DEV
docker build --target=prod ... # ✅ BUILD PROD
```

### Image Inspection (Check without building)
```bash
docker images radiocalico  # List existing images
docker ps                  # Show running containers
docker inspect radiocalico:dev  # Inspect image details
```

---

## Detailed Behavior Matrix

### Development Workflow

| Command | Builds? | Runs? | Image Used | When to Use |
|---------|---------|-------|-----------|------------|
| `make dev` | ✅ If missing | ✅ Yes | radiocalico:dev | Normal dev startup |
| `make dev-clean` | ✅ If missing | ✅ Yes | radiocalico:dev | Fresh start (removes volumes) |
| `make build-dev` | ✅ Always | ❌ No | radiocalico:dev | Force rebuild before `make dev` |
| `make dev-stop` | ❌ No | ❌ No | — | Stop running dev container |
| `make clean` | ❌ No | ❌ No | — | Remove images/volumes (doesn't rebuild) |

### Production Workflow

| Command | Builds? | Runs? | Image Used | When to Use |
|---------|---------|-------|-----------|------------|
| `make prod` | ✅ If missing | ✅ Yes | radiocalico:prod | Normal prod startup |
| `make prod-build` | ✅ Always | ❌ No | radiocalico:prod | Force rebuild before `make prod` |
| `make build-prod` | ✅ Always | ❌ No | radiocalico:prod | Alternative to prod-build |
| `make prod-stop` | ❌ No | ❌ No | — | Stop running prod container |

### Universal Build Commands

| Command | Builds? | What? | When to Use |
|---------|---------|-------|------------|
| `make build` | ✅ Always | Dev + Prod | Initial setup or update both |
| `make build --no-cache` | ✅ Always (fresh) | Dev + Prod | Force fresh build (ignore cache) |

---

## Docker Compose Behavior

### What docker-compose.yml specifies
```yaml
services:
  radiocalico-dev:
    build:
      context: .
      dockerfile: Dockerfile
      target: dev
    # Has 'build' section → Auto-build on 'up' if image missing
```

### What docker-compose.prod.yml specifies
```yaml
services:
  radiocalico:
    build:
      context: .
      dockerfile: Dockerfile
      target: prod
    # Has 'build' section → Auto-build on 'up' if image missing
```

### Implication
- ✅ `docker compose up` = Build dev image if missing, then start
- ✅ `docker compose -f docker-compose.prod.yml up` = Build prod image if missing, then start

---

## When to Build New Images

### ✅ ALWAYS build new images when:

1. **Dependencies Changed** (requirements.txt, requirements-dev.txt)
   ```bash
   # Example: Added new package
   echo "new-package==1.0.0" >> requirements.txt
   make build-dev    # ← Rebuild to install new package
   make dev
   ```

2. **Dockerfile Changed**
   ```bash
   # Example: Edited Dockerfile
   vim Dockerfile
   make build        # ← Rebuild to apply changes
   make dev
   ```

3. **Python Version Changed**
   ```bash
   # Example: Upgraded Python version
   # Dockerfile: FROM python:3.13-slim
   make build        # ← Rebuild with new Python
   make dev
   ```

4. **Environment-specific Secrets Changed**
   ```bash
   # Example: DB_PASSWORD changed in production
   export DB_PASSWORD=$(openssl rand -base64 32)
   make prod-build   # ← Rebuild to encode new config
   make prod
   ```

5. **After Major Git Changes**
   ```bash
   # After switching branches with different deps
   git checkout feature/new-dependency
   make build        # ← Rebuild to get new dependencies
   make dev
   ```

6. **After Docker/Docker Compose Updates**
   ```bash
   # After updating Docker daemon
   docker system prune
   make build
   make dev
   ```

7. **Base Image Security Updates**
   ```bash
   # Example: New Python slim image with security fix
   docker pull python:3.12-slim
   make build        # ← Rebuild to get latest base
   make dev
   ```

### ❌ DO NOT rebuild when:

- ✅ Just changing Python code (hot reload handles it)
- ✅ Just changing templates/CSS/JS (hot reload handles it)
- ✅ Just changing environment variables (pass at runtime)
- ✅ Just changing database credentials (pass at runtime)
- ✅ Just changing configuration files (volume mounts handle it)

---

## Common Workflows

### Workflow 1: Initial Setup (Fresh Clone)
```bash
git clone <repo>
cd radiocalico

# Option A: Auto-build on first run (simplest)
make dev              # ← Auto-builds dev image, runs server
# Image built automatically, everything works

# Option B: Explicit build for control
make build            # ← Build both dev and prod images explicitly
make dev              # ← Run dev server (image already built)
```

### Workflow 2: Add New Dependency
```bash
# Edit requirements.txt
echo "requests==2.31.0" >> requirements.txt

# Rebuild BEFORE running
make build-dev        # ← Rebuild to install new package
make dev              # ← Run with updated dependencies

# OR: Let docker-compose auto-build
rm -f venv/bin/python  # Force clean state
make dev              # ← Auto-builds (because image will be stale)
```

### Workflow 3: Switch Git Branch
```bash
git checkout feature/new-database-driver

# Check if dependencies changed
git diff main -- requirements.txt
# Yes, they changed? → Rebuild
make build-dev
make dev

# No changes? → Just restart
make dev-stop
make dev
```

### Workflow 4: Iterative Development (No Rebuilding)
```bash
# Start dev server (build if needed)
make dev              # ← Builds image (if first time)

# Make code changes
vim app/routes.py     # ← Hot reload: no rebuild needed
vim app/templates/index.html  # ← Hot reload: no rebuild needed

# Just keep server running, changes are live
# (Press Ctrl+C to stop when done)
```

### Workflow 5: Production Deployment
```bash
# Build production image explicitly
make prod-build       # ← Always build for prod

# Set secure password
export DB_PASSWORD=$(openssl rand -base64 32)
echo "Save password: $DB_PASSWORD"

# Start production stack
make prod             # ← Uses built image (no rebuild)

# Verify it's running
make health           # ← Check endpoints
```

### Workflow 6: CI/CD Pipeline (GitHub Actions)
```bash
# .github/workflows/docker-build.yml does:
docker build --target=dev -t radiocalico:dev .   # Always explicit build
docker build --target=prod -t radiocalico:prod .  # Always explicit build

# CI/CD best practice: Always build explicitly
# (Don't rely on auto-build for reproducibility)
```

---

## Makefile Reference

### Build Targets (Always build)
```makefile
make build         # Build BOTH dev and prod images
make build-dev     # Build dev image only
make build-prod    # Build prod image only
make prod-build    # Alias for build-prod
```

**Behavior:** These commands ALWAYS build, even if image exists.

### Run Targets (Auto-build if missing)
```makefile
make dev           # Run dev server (auto-builds if image missing)
make prod          # Run prod stack (auto-builds if image missing)
```

**Behavior:** These commands check if image exists:
- Image exists → Use it, start container
- Image missing → Build it, then start container

### Inspect/Stop Targets (Don't build)
```makefile
make dev-stop      # Stop dev container (no build)
make prod-stop     # Stop prod container (no build)
make stop          # Stop all containers (no build)
make clean         # Remove images/volumes (no build)
docker images      # List images (no build)
```

**Behavior:** These commands never build anything.

---

## Docker CLI Reference

### Build Images
```bash
# Build dev image (explicit)
docker build --target=dev -t radiocalico:dev .

# Build prod image (explicit)
docker build --target=prod -t radiocalico:prod .

# Build with cache disabled (fresh build)
docker build --no-cache --target=dev -t radiocalico:dev .

# Build with build args
docker build --build-arg KEY=VALUE --target=prod -t radiocalico:prod .
```

### Run from docker-compose
```bash
# Auto-build and run dev (if image missing)
docker compose up

# Auto-build and run dev (rebuild if image old)
docker compose up --build

# Rebuild (ignore cache) and run dev
docker compose up --build --no-cache

# Auto-build and run prod (if image missing)
docker compose -f docker-compose.prod.yml up

# Rebuild and run prod (ignore cache)
docker compose -f docker-compose.prod.yml up --build --no-cache
```

### Inspect Images
```bash
# List all radiocalico images
docker images radiocalico

# Inspect image details (size, layers, config)
docker inspect radiocalico:dev

# View image history (layer by layer)
docker history radiocalico:dev

# Run container from image (one-off)
docker run -it -p 5000:5000 radiocalico:dev
```

---

## Troubleshooting

### Problem: Changes to code don't appear
**Likely cause:** Stale image (needs rebuild)
```bash
# Solution: Rebuild image
make build-dev
make dev
```

### Problem: New dependencies not installed
**Likely cause:** Image built before requirements.txt updated
```bash
# Solution: Rebuild image
make build-dev
make dev
```

### Problem: Docker runs old version of code
**Likely cause:** Image cached from previous build
```bash
# Solution: Clear Docker cache and rebuild
make clean
make build
make dev
```

### Problem: Port already in use
**Not an image issue** — container still running
```bash
# Solution: Stop containers
make stop
make dev
```

### Problem: "Image not found" error
**Likely cause:** Image never built
```bash
# Solution: Build image first
make build
make dev
# OR: Let docker-compose auto-build
make dev  # ← Auto-builds if missing
```

---

## Best Practices

### ✅ Development Best Practices

1. **Let docker-compose auto-build on first run**
   ```bash
   make dev  # ← Simplest for first-time setup
   ```

2. **After changing dependencies, rebuild explicitly**
   ```bash
   make build-dev
   make dev
   ```

3. **Use dev-clean for complete reset**
   ```bash
   make dev-clean  # ← Removes volumes, rebuilds, starts fresh
   ```

4. **Don't manually build unless necessary**
   ```bash
   make dev       # ← Simpler than: make build-dev && make dev
   ```

### ✅ Production Best Practices

1. **Always build images explicitly (don't rely on auto-build)**
   ```bash
   make prod-build  # ← Explicit, reproducible
   export DB_PASSWORD=$(openssl rand -base64 32)
   make prod
   ```

2. **Pin image tags for reproducibility**
   ```bash
   docker build -t radiocalico:prod:v1.2.3 .  # ← Semantic versioning
   ```

3. **Build once, deploy many**
   ```bash
   docker build -t radiocalico:prod:v1.0.0 .
   # Deploy to dev, staging, prod all with same image
   ```

4. **Use .dockerignore to exclude unnecessary files**
   ```
   # .dockerignore
   .git
   tests/
   *.md
   ```

### ✅ CI/CD Best Practices

1. **Always build explicitly in pipelines**
   ```yaml
   - run: make build  # ← Reproducible, not auto-build
   ```

2. **Build only once, test many times**
   ```bash
   docker build -t myapp:sha-${{ github.sha }} .
   docker run ... myapp:sha-${{ github.sha }}
   ```

3. **Use Docker layer caching**
   ```bash
   docker build --target=prod -t radiocalico:prod .
   # Second build uses cache, much faster
   ```

---

## Decision Tree: When to Rebuild?

```
Did requirements.txt change?
├─ YES → make build-dev && make dev
└─ NO ↓

Did Dockerfile change?
├─ YES → make build && make dev
└─ NO ↓

Did base image change (Python version)?
├─ YES → make build && make dev
└─ NO ↓

Did git branch change?
├─ YES → Check if deps changed
│        YES → make build
│        NO → just make dev
└─ NO ↓

Is this first time running?
├─ YES → make dev (auto-builds)
└─ NO ↓

JUST CHANGED CODE FILES → make dev (no rebuild, hot reload)
```

---

## Summary

| Scenario | Command | Builds? |
|----------|---------|---------|
| First time setup | `make dev` | ✅ Auto-build |
| Added dependency | `make build-dev && make dev` | ✅ Always build |
| Changed code | `make dev` | ❌ No rebuild (hot reload) |
| Switch branch (deps changed) | `make build && make dev` | ✅ Always build |
| Switch branch (deps same) | `make dev` | ❌ No rebuild |
| Production deployment | `make prod-build && make prod` | ✅ Always build |
| Check image exists | `docker images radiocalico` | ❌ No build |
| Full reset | `make clean && make build && make dev` | ✅ Clean rebuild |

**Key takeaway:** `make dev` and `make prod` are smart — they auto-build if needed. Explicit builds (`make build-*`) are for when you want guaranteed fresh builds.

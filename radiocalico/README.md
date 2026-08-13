# Radio Calico (local prototype)

Flask webserver + SQLite database for local prototyping. Full containerization with Docker dev/prod, automated testing, and AI-powered code review.

## Quick Start

**With Docker** (recommended):
```bash
make dev    # Start development server with hot reload
make test   # Run all tests
make prod   # Start production stack (PostgreSQL + Nginx)
```

**Manual Setup:**
```bash
python3 -m venv venv
./venv/bin/python -m pip install -r requirements.txt
./venv/bin/python run.py
```

Server runs at http://127.0.0.1:5000 or http://localhost:5000

## Features

- `/` — homepage with user management and items list
- `/player` — **HLS radio player** for lossless audio streaming
- `/api/health` — health check
- `/api/items` — JSON list of items
- `/api/users` — JSON list of users

## Radio Player

Access the HLS radio player at: **http://127.0.0.1:5000/player**

- Plays lossless HLS stream from CloudFront CDN
- Play/Pause/Stop controls
- Browser compatibility: Chrome, Firefox, Safari, Edge (iOS 10+, Android 6+)
- Uses HLS.js library for cross-browser support

The SQLite database is created automatically at `instance/radiocalico.db` on first run.

## Testing & Security

**Run Tests Locally:**
```bash
make test              # Run unit tests (pytest)
make test-coverage     # Generate coverage report
make security          # Run security analysis (Bandit + Safety)
```

**Automated on Every PR:**
- ✅ Unit tests (pytest, 88% coverage gate)
- ✅ Security scanning (Bandit, Safety, Trivy, Hadolint, CodeQL, TruffleHog)
- ✅ Security best practices (OpenSSF Scorecard)
- ✅ AI code review (Claude Haiku 4.5)
- ✅ Docker build & smoke tests
- ✅ Issue classification & analysis

**Dependency Updates:**
- Weekly automatic updates via Dependabot (Python packages, Docker images, GitHub Actions)
- Nightly OWASP comprehensive dependency analysis

**Local Commands:**
- `make help` — Show all available targets
- `make test-coverage` — Generate coverage report
- `make security` — Run local security analysis
- `make perf` — Generate performance analysis report
- `make minify` — Minify CSS and HTML assets (20% reduction)
- `make minify-watch` — Auto-minify on file changes
- `make clean` — Clean up containers and cache

## Documentation

- **[CLAUDE.md](CLAUDE.md)** — Architecture, development guide, and troubleshooting
- **[DOCKER.md](DOCKER.md)** — Containerization and production deployment
- **[API.md](API.md)** — REST API reference and examples
- **[MINIFICATION.md](MINIFICATION.md)** — Asset minification and optimization
- **[PERFORMANCE.md](PERFORMANCE.md)** — Performance analysis and optimization roadmap
- **[SECURITY.md](../SECURITY.md)** — Security policies and vulnerability disclosure
- **[CHANGELOG.md](CHANGELOG.md)** — Project version history
- **[FEATURES.md](FEATURES.md)** — Current features and roadmap

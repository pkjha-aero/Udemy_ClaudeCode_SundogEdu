# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

# Radio Calico

Local prototype website. Flask + SQLite, native install (no Docker) in a Python virtualenv.

## Style Guide
- A text version of the styling guide for the webpage is at `radioCalico_Style_Guide.txt`
- The Radio Calico logo is at `RadioCalicoLogoTM.png`

## Stack

- **Webserver**: Flask (app factory pattern in `app/__init__.py`)
- **Database**: 
  - Development: SQLite via Flask-SQLAlchemy, file at `instance/radiocalico.db`
  - Production: PostgreSQL 16 (via Docker)
- **Env**: Python 3.12 virtualenv at `venv/` (gitignored)
- **Production**: Gunicorn WSGI server + Nginx reverse proxy (Docker)

## Development

**Quick Start with Make** (recommended):
```bash
make dev              # Start development server with Docker
make test             # Run all tests
make prod             # Start production stack
make help             # Show all available targets
```

**Manual Setup**:
```bash
python3 -m venv venv
./venv/bin/python -m pip install -r requirements.txt
```

**Run dev server** (debug mode, port 5000):
```bash
./venv/bin/python run.py
```
Accessible at: http://127.0.0.1:5000 or http://localhost:5000

**Or run in Docker** (with hot reload):
```bash
docker compose up
```
Accessible at: http://127.0.0.1:5000 or http://localhost:5000

**Production mode in Docker** (with Nginx on port 80):
```bash
docker compose -f docker-compose.prod.yml up -d
```
Accessible at: http://127.0.0.1 or http://localhost

## Architecture

**App structure (app factory pattern):**
- `app/__init__.py` — factory function `create_app()`, DB init, seeds default User on startup
- `app/models.py` — four ORM models: `User`, `Item`, `Song`, `Rating` (see Models section below)
- `app/routes.py` — Flask Blueprint with HTML routes and JSON API endpoints; uses `template_helpers.py` to prepare context data
- `app/template_helpers.py` — context preparation functions that compute URLs and format data for templates (separates Python logic from template layer)
- `app/templates/` — Jinja2 templates for HTML pages; templates receive pre-computed context from helpers
- `app/static/` — CSS and image assets; `index.css` contains all homepage styling

**Models:**
- `User` — name, email (unique); seeded default: Pankaj Jha (pankaj.psu@gmail.com)
- `Item` — name, created_at (app structure allows extensibility; no form to create yet)
- `Song` — title, artist, album, date; created dynamically from player metadata queries
- `Rating` — song_id, session_id, is_thumbs_up (one rating per song per session, enforced by unique constraint)

**Session management:** Flask session stores `session_id` (per-browser); used to track one rating per song per unique visitor. No database cleanup needed—stale ratings accumulate but don't affect queries (filtered by current session_id).

**Template layer:** Context data (URLs, formatted lists, etc.) is prepared in Python helper functions (`template_helpers.py`) before passing to Jinja2 templates. This keeps template files focused on display logic rather than mixing Python/Jinja2 logic with HTML. Templates receive pre-computed URLs instead of calling `url_for()` in markup.

**Routes:**
- GET `/` → homepage (lists users, items, add-user form)
- GET `/player` → HLS radio player page
- POST `/users` → add user (duplicate email rejected)
- GET `/api/health`, `/api/items`, `/api/users` → JSON responses
- GET `/api/song/current` → song metadata + user's rating for that song (creates Song if new)
- POST `/api/song/rate` → thumbs up/down (creates or updates Rating)

## Radio Player

- **Route**: `/player` → http://127.0.0.1:5000/player (non-Docker) or http://localhost:5000/player (Docker dev) or http://localhost/player (Docker prod)
- **Stream**: Lossless HLS from CloudFront CDN (m3u8 URL in `stream_URL.txt`)
- **Library**: HLS.js (from CDN) for cross-browser playback; falls back to native HLS on Safari/iOS
- **Layout**: Full-width teal header with logo, two-column layout (album art left, track info right)
- **Player features**:
  - Custom controls: play/pause, time display, volume slider
  - Dynamic album art from metadata (SVG placeholder fallback)
  - Track info: artist (Forest Green), title, album, quality specs
  - Rating system: thumbs up/down (Forest Green/Orange) with aggregate counts per song
  - Previous tracks history with Mint background

## Brand & Styling

Site implements Radio Calico brand style guide:
- **Color Palette**: Mint (#D8F2D5), Forest Green (#1F4E23), Teal (#38A29D), Calico Orange (#EFA63C), Charcoal (#231F20), Cream (#F5EADA), White (#FFFFFF)
- **Typography**: Montserrat (headings) and Open Sans (body) from Google Fonts
- **Logo**: Official RadioCalicoLogoTM.png in `app/static/` (56px display size)
- **Layout**: Max-width 1200px, 64px vertical rhythm, 24px horizontal gutters
- **Components**: Primary buttons (Forest Green bg), secondary buttons (border-based), teal focus states on forms

## Environment (this machine)

- OS: Ubuntu 24.04.4 LTS (Noble), user `pkjha`, hostname `pkjha-xps`, kernel `6.8.0-136-generic`
- Repo lives on an NTFS-mounted drive at `/media/pkjha/Wind_D/...` (see gotchas below)

## Environment gotchas (this machine)

- `python3-venv` not installed by default — **user runs `sudo apt install python3.12-venv` themselves** in a separate terminal.
- `pip install --user` blocked by PEP 668; always use venv, never `--user` or `--break-system-packages`.
- NTFS-mounted repo: executable bits on files in `venv/bin/` aren't reliable. `./venv/bin/pip` may fail with "Permission denied". Use `./venv/bin/python -m pip ...` instead (always works).
- Git repository root is **one directory above** `radiocalico/` (i.e. `Udemy_ClaudeCode_SundogEdu/`). Run git commands from there, not from `radiocalico/`; `git status` at the repo root will show `radiocalico/` as a subpath.

## Makefile Targets

For convenience, use `make` to manage the project:

**Development:**
- `make dev` — Start dev server (Flask + SQLite, port 5000)
- `make dev-clean` — Clean and restart dev environment
- `make setup` — Install dependencies in virtual environment

**Production:**
- `make prod` — Start prod stack (PostgreSQL + Gunicorn + Nginx, port 80)
- `make prod-build` — Build production Docker images
- `make prod-stop` — Stop production stack

**Testing:**
- `make test` — Run all tests with pytest
- `make test-coverage` — Run tests with HTML coverage report
- `make test-specific TEST=tests/test_api.py` — Run specific test file
- `make test-watch` — Run tests in watch mode (requires pytest-watch)

**Security:**
- `make security` — Run local security analysis (Bandit SAST + Safety dependency check)
- `make security-docker` — Run full security stack (includes Trivy + Hadolint checks)

**Utilities:**
- `make build` — Build all Docker images
- `make logs-dev` — View development logs
- `make logs-prod` — View production logs
- `make health` — Check health endpoints
- `make status` — Show container status
- `make stop` — Stop all containers
- `make clean` — Remove containers and volumes
- `make reset` — Full reset to clean state

**Examples:**
```bash
make help                         # Show all targets
make dev                          # Start development
make test && make dev             # Run tests then start dev
DB_PASSWORD=secret make prod      # Start prod with custom password
make test-coverage                # Run tests with coverage report
make all-tests                    # Clean, setup, and run all tests
```

## Testing

**Test Framework:** pytest + pytest-flask + pytest-cov (in-memory SQLite for isolation)

**Setup:**
```bash
pip install -r requirements-dev.txt
```

**Run all tests with coverage:**
```bash
pytest --cov=app --cov-report=html --cov-report=term-missing
```

**Run specific test file:**
```bash
pytest tests/test_models.py -v
pytest tests/test_api.py -v
pytest tests/test_ratings_system.py -v
```

**View coverage report:**
```bash
pytest --cov=app --cov-report=html
# Open: htmlcov/index.html
```

**Test Structure (8 phases, 120+ test cases):**
- Phase 1: Infrastructure (conftest.py fixtures)
- Phase 2: Model tests (User, Item, Song, Rating CRUD, uniqueness)
- Phase 3: Template helper tests (prepare_index_context)
- Phase 4: Route & API tests (/, /player, /users, /api/*)
- Phase 5: Integration tests (full player workflows, session persistence)
- Phase 6: Ratings system tests (unique constraints, vote counting, updates)
- Phase 7: Edge cases (validation, error handling, XSS, concurrency)
- Phase 8: Session management (ID generation, isolation, persistence)

**Coverage Target:** 88% overall (95% models, 90% routes/API, 100% helpers, 85% integration)

**Test Files:**
- `tests/conftest.py` — shared fixtures (app, client, db_session, sample fixtures)
- `tests/test_models.py` — model CRUD and constraints (35 tests)
- `tests/test_template_helpers.py` — context preparation (11 tests)
- `tests/test_routes.py` — HTML route handlers (12 tests)
- `tests/test_api.py` — JSON API endpoints (42 tests)
- `tests/test_integration.py` — full workflows (15 tests)
- `tests/test_ratings_system.py` — ratings constraints (20 tests)
- `tests/test_edge_cases.py` — error handling (20 tests)
- `tests/test_session_management.py` — session isolation (15 tests)

**CI/CD:** Automated testing, code review, and containerization on every PR:
- `.github/workflows/tests.yml` — Pytest suite with 88% coverage gate
- `.github/workflows/claude-code-review.yml` — AI code review (Claude Haiku 4.5)
- `.github/workflows/docker-build.yml` — Docker image builds + smoke tests
- `.github/scripts/` — Standalone Python scripts for code review, issue analysis, doc generation (Haiku 4.5)

## GitHub Automation & Claude Integration

The repository includes AI-powered automation using Claude Haiku 4.5 for cost-effective intelligent workflows:

**Workflows triggered on PR:**
- **Code Review** — Claude analyzes diffs for bugs, quality, security, performance, test coverage
- **Docker Build & Test** — Builds and smoke-tests dev/prod images on containerization changes
- **Unit Tests** — Pytest with 88% coverage gate (blocks merge if fails)

**Issue & Comment Automation:**
- **@claude mentions** — Respond to `@claude` in PR/issue comments (`.github/workflows/claude.yml`)
- **Issue Analysis** — Auto-classify bugs/features, suggest priority (`.github/scripts/process_issues.py`)
- **Code Review Script** — Standalone script for detailed PR review (`.github/scripts/claude_code_review.py`)
- **Doc Generation** — Auto-generate API docs from codebase (`.github/scripts/generate_docs.py`)

**Why Claude Haiku 4.5:**
- 90% cheaper than Opus 5 (~$0.08/month vs $0.60/month)
- Sufficient for all automation tasks: code quality, classification, analysis
- Faster responses (better for CI/CD workflows)
- Can upgrade to Opus 5 for complex architectural reviews

## Security

**Comprehensive Security Scanning** (`.github/workflows/security.yml`):
- **Secrets Scanning** — TruffleHog detects exposed credentials and tokens
- **Python SAST** — Bandit identifies code vulnerabilities (SQL injection, XSS, etc.)
- **Dependency Scanning** — Safety checks for known vulnerabilities in packages
- **Container Scanning** — Trivy scans Docker images for CVEs
- **Dockerfile Linting** — Hadolint enforces security best practices
- **Code Analysis** — CodeQL performs advanced static analysis
- **Runs** — Every PR + daily schedule (via `schedule` trigger)

**Automated Dependency Updates** (`.github/dependabot.yml`):
- Weekly Python package updates (from `requirements.txt`)
- Weekly Docker base image updates (python, postgres, nginx)
- Weekly GitHub Actions updates
- Creates PRs with security/dependency labels for review

**Docker Security:**
- Non-root execution (UID 1000)
- Minimal images (slim, alpine variants)
- Health checks for automatic container restart
- No secrets in images (env vars only)

**Application Security:**
- SQLAlchemy ORM prevents SQL injection
- Jinja2 template auto-escaping prevents XSS
- Nginx security headers (X-Frame-Options, X-XSS-Protection, etc.)
- Rate limiting (10 req/s general, 100 req/s API)
- CORS configured appropriately

**Vulnerability Disclosure:**
See [SECURITY.md](../SECURITY.md) for:
- Security policy and contact information
- Vulnerability reporting process
- Known limitations and considerations
- Security checklist for contributors

### Running Security Checks Locally

**Quick security scan** (Bandit + Safety):
```bash
make security
```
Runs Python security analysis locally without Docker. Installs Bandit (SAST) and Safety (dependency check) and reports vulnerabilities. Outputs CSV report to `/tmp/bandit-report.csv`.

**Full security stack** (simulates CI/CD):
```bash
make security-docker
```
Attempts to run the same tools as GitHub Actions (Trivy, Hadolint, etc.). Requires optional tools to be installed locally (see output for installation commands).

**Common workflows:**
```bash
make test && make security        # Test code, then verify security
make clean && make security       # Clean environment, then scan
make build && make security-docker # Build images, then scan containers
```

**What gets checked:**
| Target | Tools | Checks |
|--------|-------|--------|
| `make security` | Bandit, Safety | Python code vulnerabilities, known CVEs in dependencies |
| `make security-docker` | Trivy, Hadolint | Docker image CVEs, Dockerfile best practices |
| GitHub Actions (PR) | All 7 tools | Secrets, code quality, images, dependencies (comprehensive) |
| GitHub Actions (nightly) | OWASP | Deep dependency analysis, transitive vulnerabilities |

**Fixing security issues:**
1. Run `make security` to identify local issues
2. Fix issues in code or update dependencies
3. Push a PR to run full GitHub Actions security suite
4. Address any remaining findings before merge
5. Dependabot PRs keep dependencies patched

## Current state

- Homepage features hero section with "Listen Now" CTA, user list + add-user form (duplicate email validation), items list, link to player. Full brand styling applied.
- Radio player at `/player` streams lossless HLS with teal header/logo, two-column layout, dynamic album art, track info, and session-based song ratings (thumbs up/down with aggregate counts).
- `Item` model exists but no form to create items yet.
- Unit testing infrastructure in place: 120+ test cases across 8 phases covering models, routes, API, integration, ratings system, edge cases, and session management.
- Docker containerization complete with dev/prod targets, Nginx reverse proxy, and PostgreSQL for production.

## Production Deployment

**Database**: PostgreSQL 16 (Alpine)
- Configure via `DB_PASSWORD` environment variable (defaults to "radiocalico")
- Connection string: `postgresql://radiocalico:password@postgres:5432/radiocalico`

**Services**:
- Flask + Gunicorn: Application server on port 5000 (internal)
- PostgreSQL: Database server on port 5432 (internal)
- Nginx: Reverse proxy on port 80 (external)

**Health Checks**:
- PostgreSQL: `pg_isready` check every 10s
- Flask: HTTP health check to `/api/health` every 30s

**Startup**:
```bash
# Set custom password (optional, defaults to "radiocalico")
export DB_PASSWORD=your_secure_password

# Start production stack
docker compose -f docker-compose.prod.yml up -d
```

**Health Check**:
- [http://localhost/api/health](http://localhost/api/health) — API health endpoint (through Nginx)
- Run `docker compose -f docker-compose.prod.yml ps` to verify all services are healthy

See `docker_doc/DOCKER.md` for complete production setup and configuration guide.

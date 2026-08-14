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

**System Design:** See [ARCHITECTURE.md](ARCHITECTURE.md) for comprehensive Mermaid diagrams covering:
- High-level system architecture
- Component interactions and data flow
- Docker deployment topology
- Database schema (ER diagram)
- API endpoints
- Security layers
- Performance optimization
- Deployment environments

**Viewing Architecture Diagrams:**

✅ **Works out of the box (no installation):**
- GitHub repository — Mermaid diagrams render automatically
- VS Code — Install "Markdown Preview Mermaid Support" extension
- GitLab, Gitea — Native Mermaid support
- [Mermaid Live Editor](https://mermaid.live/) — Copy/paste diagram code online

🔧 **Optional export to images** (for presentations, exports):
- Install: `npm install -g @mermaid-js/mermaid-cli`
- Export: `make arch-html` or `mmdc -i ARCHITECTURE.md -o ARCHITECTURE.html`
- **This is completely optional** — not required for dev or prod builds

**Complete viewing guide:** See [ARCHITECTURE-VIEWING-GUIDE.md](ARCHITECTURE-VIEWING-GUIDE.md) for:
- Detailed setup instructions
- Viewing options for all platforms
- Build compatibility (clean/edited builds work perfectly)
- Export options
- Troubleshooting
- FAQ

**Important:** mermaid-cli is NOT a build dependency. Clean builds and edited builds work perfectly without it. The diagrams use standard Mermaid syntax that renders natively in modern markdown viewers and GitHub.

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

**Image Building Note:** See [DOCKER-IMAGE-MANAGEMENT.md](DOCKER-IMAGE-MANAGEMENT.md) for comprehensive guide on when Docker images are built vs. used. Quick summary:
- `make dev` / `make prod` — ⚡ Auto-build image if missing, then run
- `make build` / `make build-dev` / `make build-prod` — 🔨 Always build (explicit)

**Development:**
- `make dev` — Start dev server (Flask + SQLite, port 5000) [⚡ auto-builds image if missing]
- `make dev-clean` — Clean and restart dev environment (removes volumes, rebuilds image)
- `make setup` — Install dependencies in virtual environment

**Asset Optimization:**
- `make minify` — Minify CSS and HTML assets once (20% reduction on CSS, 5-22% on HTML)
- `make minify-watch` — Auto-minify CSS/HTML on file changes (watch mode for active development)
- **Note:** Minification runs automatically in Docker builds (dev and prod); these targets are for pre-commit optimization

**Architecture & Design:**
- `make arch` — Show architecture diagram locations and viewing options
- `make arch-html` — Export HTML version of diagrams (optional, requires mermaid-cli)
  - **Note:** Diagrams render automatically in GitHub, VS Code, and most markdown viewers
  - mermaid-cli is NOT required for development or production builds

**Production:**
- `make prod` — Start prod stack (PostgreSQL + Gunicorn + Nginx, port 80) [⚡ auto-builds image if missing] **Requires DB_PASSWORD env var**
  ```bash
  export DB_PASSWORD=$(openssl rand -base64 32)
  make prod
  ```
- `make prod-build` — Build production Docker images explicitly (🔨 always builds)
- `make prod-stop` — Stop production stack

**Docker Image Building:**
- `make build` — Build both dev and prod images explicitly (🔨 always builds)
- `make build-dev` — Build dev image explicitly (🔨 always builds)
- `make build-prod` — Build prod image explicitly (🔨 always builds)
- **When to use:** After changing requirements.txt, Dockerfile, or dependencies — see [DOCKER-IMAGE-MANAGEMENT.md](DOCKER-IMAGE-MANAGEMENT.md)

**Database Management:**
- `make db-help` — Show all database commands with descriptions
- `make db-status` — Show status of dev (SQLite) and prod (PostgreSQL) databases
- `make db-backup` — Backup both databases
- **Development (SQLite):**
  - `make db-init-dev` — Initialize database manually
  - `make db-clean-dev` — Remove database (hard delete)
  - `make db-reset-dev` — Clean + reinitialize (fresh start)
  - `make db-backup-dev` — Backup SQLite file
  - `make db-status-dev` — Show dev database status
- **Production (PostgreSQL):**
  - `make db-init-prod` — Initialize database manually
  - `make db-clean-prod` — Remove database (hard delete)
  - `make db-reset-prod` — Clean + reinitialize (fresh start)
  - `make db-backup-prod` — Backup PostgreSQL database
  - `make db-restore-prod` — Restore from backup: `make db-restore-prod BACKUP=backups/prod-2026-08-12.sql`
  - `make db-status-prod` — Show prod database status
- **When to clean:** See [DATABASE-MANAGEMENT.md](DATABASE-MANAGEMENT.md) for complete decision tree

**Testing:**
- `make test` — Run all 149 tests (fast, no coverage requirement) — use during development for quick feedback
- `make test-coverage` — Run all tests with coverage measurement and 88% threshold (same as GitHub Actions) — use before pushing to verify PR will pass
- `make test-specific TEST=tests/test_api.py` — Run specific test file (e.g., for debugging)
- `make test-watch` — Run tests in watch mode (requires pytest-watch) — useful for TDD

**Security:**
- `make security` — Run local security analysis (Bandit SAST + Safety dependency check)
- `make security-docker` — Run full security stack (includes Trivy + Hadolint checks)

**Performance:**
- `make perf` — Generate performance analysis report (outputs to `PERFORMANCE.md`)
- `make perf-commit` — Generate performance report and commit it to git

**Utilities:**
- `make logs-dev` — View development logs
- `make logs-prod` — View production logs
- `make health` — Check health endpoints
- `make status` — Show container status
- `make stop` — Stop all containers (dev and prod)
- `make clean` — Remove containers and volumes (doesn't rebuild)
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

### Local vs GitHub Actions Testing

**`make test` (Quick local validation):**
```bash
make test
```
- Runs all 149 tests with verbose output
- No coverage requirement
- Fast feedback (~11 seconds)
- Use this for rapid development iteration

**`make test-coverage` (Full local validation with coverage gate):**
```bash
make test-coverage
```
- Runs all 149 tests with coverage measurement
- Enforces 88% minimum coverage (same as GitHub Actions)
- Generates HTML coverage report at `htmlcov/index.html`
- Use this before pushing to verify GitHub Actions will pass

**GitHub Actions Workflow (`.github/workflows/tests.yml`):**
- Runs same 149 test suite as `make test`
- Enforces 88% minimum code coverage (fails if below threshold)
- Sets `PYTHONPATH=.` to resolve module imports correctly
- Blocks PR merge if:
  - ❌ Any test fails, OR
  - ❌ Code coverage drops below 88%
- Uploads coverage reports to Codecov

**Recommended workflow before pushing:**
```bash
make test-coverage        # Verify tests pass AND coverage meets 88% threshold
make security             # Run security checks locally
git push                  # GitHub Actions will run automatically
```

**CI/CD:** Automated testing, code review, and containerization on every PR:
- `.github/workflows/tests.yml` — Pytest suite with 88% coverage gate (requires PYTHONPATH=. for module resolution)
- `.github/workflows/claude-code-review.yml` — AI code review (Claude Sonnet 5)
- `.github/workflows/docker-build.yml` — Docker image builds + smoke tests
- `.github/scripts/generate_perf_report.py` — Performance report generator (pure Python, no Claude; run via `make perf`)

## GitHub Automation & Claude Integration

Claude automation runs on **Claude Sonnet 5** (automated PR review) and **Claude Opus 5**
(`@claude`) via the official
[`anthropics/claude-code-action@v1`](https://github.com/anthropics/claude-code-action),
authenticated with a `CLAUDE_CODE_OAUTH_TOKEN` repository secret so usage bills against a
**Claude Pro subscription rather than API credits**.

**Setup:** See [`.github/CLAUDE_GITHUB_SETUP.md`](../.github/CLAUDE_GITHUB_SETUP.md) for
token generation (`claude setup-token`), GitHub App installation, and troubleshooting.

**Workflows:**
- **`claude.yml`** (interactive) — responds to `@claude` in issues, PR comments, reviews, and new issues. Output: a comment on the issue/PR.
- **`claude-code-review.yml`** (automation) — runs the `code-review` plugin on every PR touching code paths. Output: the **Actions run log**, not a PR comment.

**Non-Claude workflows:** `tests.yml`, `security.yml`, `scorecard.yml`, `docker-build.yml`
require no Claude credentials.

**Why `CLAUDE_CODE_OAUTH_TOKEN` and not `ANTHROPIC_API_KEY`:**
- An OAuth token bills the Pro subscription; an API key bills API credits
- It is **not** a drop-in swap — the token only works with `claude-code-action` or the
  Claude Code CLI, never with the raw `anthropic` Python SDK
- The token is tied to the subscription of whoever ran `claude setup-token`; for shared or
  org-wide use, prefer an API key or workload identity federation

**Cost controls in place:** `timeout-minutes: 20` on both jobs, `--max-turns 15` on the
responder, `paths:` filters on the reviewer, and an `if:` guard that avoids starting a
runner for comments without `@claude`.

## Security

**Comprehensive Security Scanning** (`.github/workflows/security.yml` and `.github/workflows/scorecard.yml`):
- **Secrets Scanning** — TruffleHog detects exposed credentials and tokens
- **Python SAST** — Bandit identifies code vulnerabilities (SQL injection, XSS, etc.)
- **Dependency Scanning** — Safety checks for known vulnerabilities in packages
- **Container Scanning** — Trivy scans Docker images for CVEs
- **Dockerfile Linting** — Hadolint enforces security best practices
- **Code Analysis** — CodeQL performs advanced static analysis
- **Security Maturity** — OpenSSF Scorecard assesses repository best practices (SLSA alignment)
- **Runs** — Every PR + daily schedule (via `schedule` trigger) + weekly scorecard

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
Runs Trivy and Hadolint in Docker containers (no local installation needed). Scans Docker images for CVEs and validates Dockerfile best practices.

**Common workflows:**
```bash
make test && make security        # Test code, then verify security
make clean && make security       # Clean environment, then scan
make build && make security-docker # Build images, then scan containers
```

### Local Make vs GitHub Actions Security Workflows

**Important:** Local `make security` targets and GitHub Actions workflows are **separate but complementary** — they do NOT call each other.

#### Local Development (`make security` / `make security-docker`)

**Purpose:** Rapid feedback for developers before pushing

**Tools invoked directly by Makefile:**
- `make security` → Bandit (Python SAST) + Safety (dependencies)
- `make security-docker` → Trivy (image scanning) + Hadolint (Dockerfile linting)

**Workflow:** Developer runs locally → sees output in terminal → fixes issues → commits → pushes PR

**Advantages:**
- ✅ Fast feedback loop (seconds)
- ✅ No network calls to GitHub
- ✅ Local debugging and iteration
- ✅ Works offline

#### CI/CD Security Scanning (`.github/workflows/security.yml` / `scorecard.yml`)

**Purpose:** Comprehensive automated security checks on every PR and schedule

**Tools invoked directly by GitHub Actions (NOT via make targets):**
- TruffleHog → Secrets scanning
- Bandit → Python SAST (via workflow, not `make security`)
- Safety → Dependency vulnerabilities (via workflow)
- Trivy → Docker image scanning (via GitHub Action, not `make security-docker`)
- Hadolint → Dockerfile linting (via GitHub Action)
- CodeQL → Code analysis
- OpenSSF Scorecard → Security best practices assessment

**Workflow:** Developer pushes PR → GitHub runs 7 security tools → results appear in Security tab + PR comments → developer fixes findings → reruns workflows

**Advantages:**
- ✅ 7 comprehensive tools (vs 2-4 locally)
- ✅ Automated SARIF upload to Security tab
- ✅ PR comments with summaries
- ✅ Artifact storage for reports
- ✅ Secrets scanning (not in local make targets)
- ✅ Fresh environment (no local configuration drift)

#### Comparison Table

| Aspect | `make security` | `make security-docker` | GitHub Actions |
|--------|---|---|---|
| **When** | Local development | Local development | Every PR + schedule |
| **Tools** | Bandit, Safety | Trivy, Hadolint | All 7 tools |
| **Speed** | ~5-10 seconds | ~30-60 seconds | ~2-3 minutes |
| **Setup Required** | Python venv | Docker only | None (runs on GitHub) |
| **SARIF/Reports** | Local files only | Local files only | ✅ Uploaded to GitHub Security tab |
| **Secrets Scanning** | ❌ Not included | ❌ Not included | ✅ TruffleHog |
| **Code Analysis** | ❌ Not included | ❌ Not included | ✅ CodeQL |
| **Best Practices** | ❌ Not included | ❌ Not included | ✅ OpenSSF Scorecard |

#### Recommended Workflow

```
1. Before pushing:
   make test && make security              # Run local Python checks
   
2. After pushing PR:
   GitHub Actions runs automatically        # 7 comprehensive tools
   
3. Review results:
   - Terminal: Local findings
   - GitHub Security tab: Comprehensive results
   - GitHub PR comments: Summary + artifacts
   
4. Fix findings:
   Update code/dependencies
   Commit and push (workflow reruns)
   
5. Merge:
   All security checks pass → ready to merge
```

#### Why They're Separate (Not Consolidated)

GitHub Actions workflows do NOT call `make security` because:

1. **GitHub integration benefits lost** — Direct tool invocation enables:
   - Automatic SARIF upload to Security tab
   - Fine-grained artifact handling
   - Workflow-specific report formatting
   - Per-tool result aggregation

2. **Explicit CI/CD logic** — Workflows show exactly what runs in CI/CD:
   - No hidden dependencies on Makefile
   - Easy to modify without breaking local development
   - Clear separation of concerns

3. **Different tool versions** — GitHub Actions can pin specific tool versions independently:
   - Security tools update frequently
   - Local and CI/CD can use different versions if needed
   - No version conflicts between environments

**Fixing security issues:**
1. Run `make security` locally to identify Python issues
2. Run `make security-docker` locally to check Docker issues
3. Fix issues in code or update dependencies
4. Push PR to trigger full GitHub Actions security suite (7 tools)
5. Address any additional findings from CodeQL/TruffleHog/Scorecard
6. Merge when all checks pass

## Current state

- Homepage features hero section with "Listen Now" CTA, user list + add-user form (duplicate email validation), items list, link to player. Full brand styling applied.
- Radio player at `/player` streams lossless HLS with teal header/logo, two-column layout, dynamic album art, track info, and session-based song ratings (thumbs up/down with aggregate counts).
- `Item` model exists but no form to create items yet.
- Unit testing infrastructure in place: 164 test cases across 8 phases covering models, routes, API, integration, ratings system, edge cases, and session management (88% coverage).
- Docker containerization complete with dev/prod targets, Nginx reverse proxy, and PostgreSQL for production.
- **Performance optimizations fully implemented** (~550ms total improvement):
  - ✅ Font preconnect + weight reduction (~80ms)
  - ✅ Conditional metadata polling + localStorage cache (~70% fewer API calls)
  - ✅ SQL query optimization using func.count() aggregation (~100ms)
  - ✅ Gzip compression (100-200ms, 60-70% size reduction)
  - ✅ HTTP cache headers (200-400ms on repeat visits)
  - ✅ CSS code split (27KB HTML → 4KB + 9.4KB CSS file)
  - ✅ Asset minification (CSS 20%, HTML 5-22%, 2.7 KB saved)
    - Automatic in Docker builds (dev/prod)
    - Manual: `make minify` or `make minify-watch`
    - See [MINIFICATION.md](MINIFICATION.md) for details

## Production Deployment

**Security Architecture:** See [PRODUCTION-ARCHITECTURE.md](PRODUCTION-ARCHITECTURE.md) for:
- Correct port exposure (Nginx on 80, Flask internal, PostgreSQL internal)
- Security layers (reverse proxy, rate limiting, security headers)
- Verification checklist
- Common mistakes and how to avoid them

**Database**: PostgreSQL 16 (Alpine)
- Configure via `DB_PASSWORD` environment variable (defaults to "radiocalico")
- Connection string: `postgresql://radiocalico:password@postgres:5432/radiocalico`

**⚠️ SECURITY: Database Password**

The default password `radiocalico` is **ONLY for development**. For production:

```bash
# Generate a secure password (minimum 32 characters)
export DB_PASSWORD=$(openssl rand -base64 32)
echo "Save this password securely: $DB_PASSWORD"

# Or use Python
export DB_PASSWORD=$(python3 -c "import secrets; print(secrets.token_urlsafe(32))")

# Start production with secure password
docker compose -f docker-compose.prod.yml up -d
```

**Services**:
- Flask + Gunicorn: Application server on port 5000 (internal)
- PostgreSQL: Database server on port 5432 (internal)
- Nginx: Reverse proxy on port 80 (external)

**Security Features**:
- ✅ CSRF protection enabled (Flask-WTF)
- ✅ Nginx security headers (X-Frame-Options, X-XSS-Protection, etc.)
- ✅ Rate limiting (10 req/s general, 100 req/s API)
- ✅ Non-root container execution (UID 1000)
- ✅ Health checks with automatic restart

**Health Checks**:
- PostgreSQL: `pg_isready` check every 10s
- Flask: HTTP health check to `/api/health` every 30s

**Startup**:
```bash
# Set secure password BEFORE starting (see ⚠️ SECURITY above)
export DB_PASSWORD=$(openssl rand -base64 32)

# Start production stack
docker compose -f docker-compose.prod.yml up -d
```

**Health Check**:
- [http://localhost/api/health](http://localhost/api/health) — API health endpoint (through Nginx)
- Run `docker compose -f docker-compose.prod.yml ps` to verify all services are healthy

See `docker_doc/DOCKER.md` for complete production setup and configuration guide.

## Troubleshooting Docker Issues

### Problem: `ModuleNotFoundError: No module named 'flask_wtf'` (or other imports)

**Symptoms:**
- Container exits immediately with import error
- `make dev` or `make prod` shows: `ModuleNotFoundError: No module named 'X'`
- Error appears in first few lines of container startup

**Root Cause:** 
Docker image was built before new dependencies were added to `requirements.txt`

**Solution:**

**Step 1: Identify which mode has the issue**
```bash
# For development issues:
make dev
# Look for ModuleNotFoundError in output

# For production issues:
make prod
# Check logs: docker compose -f docker-compose.prod.yml logs radiocalico
```

**Step 2: Rebuild the appropriate Docker image**
```bash
# For development:
docker build --target=dev -t radiocalico:dev .
# Or use make:
make build-dev

# For production:
docker build --target=prod -t radiocalico:prod .
# Or use make:
make prod-build

# Or rebuild both (recommended):
docker build --target=dev -t radiocalico:dev . && docker build --target=prod -t radiocalico:prod .
# Or use make:
make build
```

**Step 3: Restart the service**
```bash
# For development:
make dev-clean

# For production:
make prod-stop
make prod
```

**When This Happens:**
- After adding new packages to `requirements.txt`
- After switching branches with different dependencies
- After pulling changes that update dependencies

---

### Problem: `502 Bad Gateway` or `password authentication failed`

**Symptoms:**
- Website shows: 502 Bad Gateway
- Logs show: `FATAL: password authentication failed for user "radiocalico"`
- PostgreSQL container is running but Flask can't connect

**Root Causes:**
1. Stale PostgreSQL volume with old password
2. DB_PASSWORD not set when starting production
3. Flask image missing dependencies

**Solution:**

**For password authentication failures:**

```bash
# Step 1: Stop production
docker compose -f docker-compose.prod.yml down
# Or use make:
make prod-stop

# Step 2: Remove stale database volume
docker volume rm radiocalico_radiocalico-db

# Step 3: Set secure password
export DB_PASSWORD=$(openssl rand -base64 32)
echo "Save this: $DB_PASSWORD"

# Step 4: Restart production
docker compose -f docker-compose.prod.yml up -d
# Or use make:
make prod

# Step 5: Verify it works (wait 5-10 seconds for PostgreSQL to initialize)
sleep 8
curl http://localhost/api/health
# Should return: {"status":"ok"}
```

**For missing dependency errors (Flask won't start):**
- Follow the "ModuleNotFoundError" solution above
- Also run the password solution above

---

### Problem: `Connection refused` when Flask starts

**Symptoms:**
- Flask starts but can't connect to PostgreSQL
- Error: `connection to server at "postgres" ... failed: Connection refused`
- Happens immediately on startup

**Root Cause:** 
Race condition - Flask is starting before PostgreSQL is ready

**Solution:**
Just wait - PostgreSQL takes a few seconds to initialize:

```bash
# Wait 8-10 seconds for PostgreSQL health check to pass
sleep 10

# Then test health endpoint
curl http://localhost/api/health
# Or use make:
make health
```

If it persists after 30 seconds, check PostgreSQL logs:
```bash
docker compose -f docker-compose.prod.yml logs postgres
```

---

### Problem: Port already in use

**Symptoms:**
- Error: `bind: address already in use`
- Can't start `make dev` or `make prod`

**Solution:**
```bash
# Stop all containers
docker compose down && docker compose -f docker-compose.prod.yml down
# Or use make:
make stop

# Kill any lingering containers (if needed)
docker kill $(docker ps -q) 2>/dev/null || true

# Remove all containers (if needed)
docker rm $(docker ps -a -q) 2>/dev/null || true

# Restart
make dev   # or make prod
```

---

### Quick Troubleshooting Checklist

When **any** Docker issue occurs:

```bash
# 1. Check if containers are running
docker compose -f docker-compose.prod.yml ps
# Or use make:
make status

# 2. View recent logs
docker compose -f docker-compose.prod.yml logs -f radiocalico
# Or use make:
make logs-prod

# 3. If import error → rebuild image
docker build --target=dev -t radiocalico:dev . && docker build --target=prod -t radiocalico:prod .
# Or use make (recommended):
make build

# 4. If password error → remove volume and restart
docker volume rm radiocalico_radiocalico-db
docker compose -f docker-compose.prod.yml up -d
# Or use make:
# (remove volume manually, then:)
make prod

# 5. If connection error → wait for PostgreSQL
sleep 10 && curl http://localhost/api/health
# Or use make:
sleep 10 && make health

# 6. If still failing → full reset
docker compose down && docker compose -f docker-compose.prod.yml down
docker volume rm radiocalico_radiocalico-db
docker build --target=dev -t radiocalico:dev . && docker build --target=prod -t radiocalico:prod .
# Or use make (recommended):
make clean
docker volume rm radiocalico_radiocalico-db
make build
export DB_PASSWORD=$(openssl rand -base64 32)
make prod
```

---

### Common Docker Commands for Debugging

```bash
# View all container logs
docker compose -f docker-compose.prod.yml logs radiocalico  # Last 100 lines
docker compose -f docker-compose.prod.yml logs -f radiocalico  # Follow logs

# Check container status
docker ps -a
docker compose -f docker-compose.prod.yml ps

# View environment variables in running container
docker compose -f docker-compose.prod.yml exec radiocalico env | grep DB

# Test database connection from Flask container
docker compose -f docker-compose.prod.yml exec radiocalico python -c \
  "import psycopg2; conn = psycopg2.connect('postgresql://radiocalico:password@postgres:5432/radiocalico'); print('Connected!')"

# Check PostgreSQL is accepting connections
docker compose -f docker-compose.prod.yml exec postgres pg_isready -U radiocalico
```

# Changelog

All notable changes to Radio Calico are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/), and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [Unreleased]

### Changed
- **Claude GitHub automation migrated to Opus 5 on Pro subscription billing**
  - Replaced hand-rolled `anthropic` SDK calls with official `anthropics/claude-code-action@v1`
  - Auth switched from `ANTHROPIC_API_KEY` (API credits) to `CLAUDE_CODE_OAUTH_TOKEN` (Pro subscription)
  - Model upgraded from `claude-haiku-4-5-20251001` to `claude-opus-5`
  - Rationale: the OAuth token is a Claude Code credential, not an API key — it cannot be
    passed to the raw `anthropic` SDK, so subscription billing required the official action
  - Removed duplicate PR review (both `claude-code-review.yml` and `claude-integration.yml`
    were reviewing every PR, costing two Claude calls per PR)
  - Deleted: `claude-integration.yml`, `validate-claude-integration.yml`,
    `claude_code_review.py`, `process_issues.py`, `generate_docs.py`, `CLAUDE_INTEGRATION_SETUP.md`
  - Retained: `generate_perf_report.py` (pure Python, no Claude dependency)
  - **Behaviour change:** PR review findings now appear in the Actions run log rather than
    as a PR comment
  - New setup guide: `.github/CLAUDE_GITHUB_SETUP.md`

### Added
- High-priority documentation: API.md with complete REST endpoint reference
- System Architecture documentation: ARCHITECTURE.md with 9 Mermaid diagrams
  - High-level architecture (external services, layers, infrastructure)
  - Component architecture (presentation, application, data layers)
  - Data flow (user rating workflow sequence diagram)
  - Docker deployment topology
  - API endpoints and response data
  - Database schema (ER diagram with relationships)
  - Performance optimization layers
  - Deployment environments (dev → prod progression)
  - Security architecture (9-layer defense in depth)
  - Make targets: `make arch`, `make arch-html`
  - Viewing guide: ARCHITECTURE-VIEWING-GUIDE.md (setup, troubleshooting, FAQ)
  - **Important:** No build dependencies, works with clean/edited builds, mermaid-cli is optional
- Docker Image Management documentation: DOCKER-IMAGE-MANAGEMENT.md
  - Clear explanation: auto-build vs. explicit build commands
  - When to build new images (requirements.txt, Dockerfile, dependencies change)
  - Detailed behavior matrix for all make/docker commands
  - Common workflows and decision tree
  - CI/CD best practices
  - Troubleshooting guide
  - Make targets clarified: `make dev/prod` (⚡ auto-build), `make build-*` (🔨 explicit)
- Database Management documentation: DATABASE-MANAGEMENT.md
  - When to clean up databases (decision tree included)
  - SQLite (dev) vs PostgreSQL (prod) management
  - Backup and restore procedures
  - Common workflows and troubleshooting
  - Best practices for dev, prod, and CI/CD
  - New make targets: `make db-*` for managing databases
  - Status commands: `make db-status`, `make db-status-dev`, `make db-status-prod`
  - Backup commands: `make db-backup`, `make db-backup-dev`, `make db-backup-prod`
  - Clean/reset commands: `make db-clean-*`, `make db-reset-*`, `make db-restore-prod`
- Development environment template (.env.development.example)
- CHANGELOG.md for tracking project evolution
- FEATURES.md documenting current and planned capabilities
- Automatic asset minification (CSS 20%, HTML 5-22% reduction)
  - `make minify` — Minify assets once
  - `make minify-watch` — Auto-minify on file changes (watch mode)
  - Integrated into Docker builds (dev and prod stages)
  - New: MINIFICATION.md documentation and scripts/minify.py

### Fixed
- **Production port exposure security issue**: Flask port (5000) no longer exposed directly in production
  - Changed from `ports: "5000:5000"` to `expose: "5000"` (internal Docker network only)
  - Only Nginx (port 80) is now exposed externally
  - Forces all traffic through security layers (rate limiting, security headers)
  - Matches production security best practices
- Track rating functionality restored by exempting JSON API endpoints from CSRF protection
- Import errors resolved by using correct csrf.exempt decorator
- Docker Compose warnings eliminated by removing obsolete version attribute
- README.md broken links updated (docker_doc → root directory)

### Changed
- DOCKER.md moved from docker_doc/ to radiocalico/ root for better accessibility
- Asset minification now runs automatically in Docker builds (no user action needed)
- Production architecture documented in new PRODUCTION-ARCHITECTURE.md

### Added
- Production Architecture documentation: PRODUCTION-ARCHITECTURE.md
  - Correct production network architecture (Nginx → Flask → PostgreSQL)
  - Port exposure policy (only Nginx external, all others internal)
  - Security layers explanation
  - Verification checklist for production setup
  - Debugging guide for common issues
  - Common mistakes and how to avoid them
  - Development vs production architecture comparison
  - Best practices checklist

---

## [2026-08-12] - Production Ready Release

### Added
- Comprehensive integration tests (164 total tests, 100% passing)
- Full Docker containerization (dev and prod stacks)
- Production setup: PostgreSQL + Nginx + Gunicorn
- Security scanning infrastructure (7 tools: TruffleHog, Bandit, Safety, Trivy, Hadolint, CodeQL, Scorecard)
- Automated dependency updates via Dependabot
- AI-powered code review on PRs (Claude Haiku 4.5)
- Health check endpoints for monitoring
- Audio player with dynamic quality streaming
- Track rating system (thumbs up/down with vote counts)
- Session-based user identification
- CSRF protection on form submissions

### Features
- HLS radio player with lossless audio streaming
- User management (add users, track in database)
- Items catalog display
- RESTful JSON API
- Comprehensive test suite
- Security best practices (branch protection, secrets scanning, code analysis)

### Infrastructure
- Multi-stage Docker builds (dev/prod separation)
- Docker Compose orchestration (SQLite dev, PostgreSQL prod)
- Nginx reverse proxy with rate limiting and security headers
- Gunicorn WSGI server for production
- GitHub Actions CI/CD pipeline
- Makefile targets for common operations

### Documentation
- CLAUDE.md: 500+ line development guide with architecture, setup, testing, troubleshooting
- DOCKER.md: Complete containerization and deployment guide
- SECURITY.md: Security policies and vulnerability disclosure process
- README.md: Quick start and feature overview
- radioCalico_Style_Guide.txt: Brand styling guidelines

---

## [2026-08-11] - Audio Player Enhancement

### Added
- Default player volume set to 100% (was 70%)
- Dynamic stream quality based on metadata and bandwidth

### Fixed
- Audio player initialization and state management

---

## [2026-08-10] - CSRF Protection & Security Hardening

### Added
- Flask-WTF CSRF protection on all form submissions
- Security headers via Nginx (X-Frame-Options, X-Content-Type-Options, etc.)
- Dependency scanning via Safety
- Secret scanning via TruffleHog
- Dockerfile linting via Hadolint

### Changed
- Enhanced security scanning workflow with 7 comprehensive tools

---

## [2026-08-09] - Docker Finalization

### Added
- Nginx configuration with security headers
- PostgreSQL integration for production
- Health checks for all services
- Production Docker image with Gunicorn

### Fixed
- Docker build errors and dependency issues
- Flask app binding to all interfaces (0.0.0.0)
- Database initialization in containers

---

## [2026-08-08] - Testing Infrastructure

### Added
- Comprehensive test suite: 149+ tests across 8 phases
- Test coverage reporting (88% threshold in CI/CD)
- Unit tests for models, routes, API endpoints
- Integration tests for workflows
- Session management tests
- Error handling tests

### Infrastructure
- GitHub Actions CI/CD pipeline
- Test coverage gates
- Automated test runs on PRs

---

## [2026-08-07] - Core Features

### Added
- Flask web server with SQLite database
- User management API
- Items catalog API
- HLS radio player at `/player`
- Track metadata fetching
- Rating system (thumbs up/down)
- Session-based user tracking
- RESTful JSON API endpoints

### Features
- Homepage with user list and add user form
- Player page with stream controls
- Rating buttons with vote counts
- API health check

---

## Legend

- **Added** - New features
- **Changed** - Changes to existing functionality
- **Deprecated** - Soon-to-be removed features
- **Removed** - Removed features
- **Fixed** - Bug fixes
- **Security** - Security vulnerability fixes
- **Infrastructure** - DevOps, CI/CD, tooling changes

---

## Versioning

This project follows [Semantic Versioning](https://semver.org/):
- **MAJOR** - Breaking changes (incompatible API changes)
- **MINOR** - New features (backwards compatible)
- **PATCH** - Bug fixes (backwards compatible)

Current version: **In active development** (unreleased)

---

## How to Report Issues

See [SECURITY.md](../SECURITY.md) for security issues.

For other bugs, open a GitHub issue with:
- Clear description of the problem
- Steps to reproduce
- Expected vs actual behavior
- Environment details (OS, browser, Docker version, etc.)

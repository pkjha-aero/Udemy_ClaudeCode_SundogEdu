# Changelog

All notable changes to Radio Calico are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/), and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [Unreleased]

### Added
- High-priority documentation: API.md with complete REST endpoint reference
- Development environment template (.env.development.example)
- CHANGELOG.md for tracking project evolution
- FEATURES.md documenting current and planned capabilities

### Fixed
- Track rating functionality restored by exempting JSON API endpoints from CSRF protection
- Import errors resolved by using correct csrf.exempt decorator
- Docker Compose warnings eliminated by removing obsolete version attribute
- README.md broken links updated (docker_doc → root directory)

### Changed
- DOCKER.md moved from docker_doc/ to radiocalico/ root for better accessibility

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

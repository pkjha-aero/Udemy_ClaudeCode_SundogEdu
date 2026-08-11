# Security Policy

## Overview

This document outlines the security practices and vulnerability disclosure process for the Radio Calico project.

## Supported Versions

| Version | Status | Support |
|---------|--------|---------|
| main | Active | Security patches |
| Other branches | Development | Best-effort |

## Reporting Security Vulnerabilities

**Please do NOT open a public issue for security vulnerabilities.**

Instead, please report security vulnerabilities privately via GitHub's Security Advisory feature:

1. Go to the [Security](https://github.com/pkjha-aero/Udemy_ClaudeCode_SundogEdu/security/advisories) tab
2. Click "Report a vulnerability"
3. Provide:
   - Description of the vulnerability
   - Affected components/versions
   - Steps to reproduce (if applicable)
   - Impact assessment
   - Suggested fixes (if available)

**Response time:** We aim to respond to security reports within 48 hours and publish fixes within 1 week for critical issues.

## Automated Security Enforcement

To ensure consistent security practices, we use automated scanning on every PR and nightly:

### What Developers Encounter on PRs

**6 Security Tools Run Automatically:**
1. **TruffleHog** — Detects exposed secrets (API keys, passwords, tokens)
2. **Bandit** — Scans Python code for security vulnerabilities (SQL injection, XSS, etc.)
3. **Safety** — Checks Python dependencies for known CVEs
4. **Trivy** — Scans Docker images for container vulnerabilities
5. **Hadolint** — Lints Dockerfile for security and best practice violations
6. **CodeQL** — Performs deep code analysis for security and quality issues

**On Every PR:**
- Security scan results appear in PR comments
- Detailed reports available in Artifacts tab
- CodeQL results visible in Security tab
- Failed checks must be addressed before merge

**Nightly (Scheduled):**
- OWASP Dependency-Check runs comprehensive dependency analysis
- Detects transitive dependencies and supply chain risks

### Dependabot for Automatic Updates

- **Weekly updates** for Python packages, Docker images, and GitHub Actions
- Creates PRs with security labels
- Prevents security drift over time

This automated enforcement is part of our "shift-left security" approach—catching issues early in development rather than during manual security reviews.

## Security Best Practices

### Code Security

- **SAST Scanning:** Bandit runs on all Python code to detect common security issues
- **Dependency Scanning:** Safety checks for known vulnerabilities in dependencies
- **Secrets Scanning:** TruffleHog scans for exposed credentials
- **Code Analysis:** CodeQL performs comprehensive code analysis

### Container Security

- **Non-root execution:** All containers run as non-root user (UID 1000)
- **Minimal images:** Uses slim base images to reduce attack surface
- **Vulnerability scanning:** Trivy scans Docker images for CVEs
- **Dockerfile linting:** Hadolint enforces security best practices

### Dependency Management

- **Automated updates:** Dependabot creates PRs for dependency updates
- **Weekly scans:** Security workflow runs on schedule to detect issues
- **Pinned versions:** All dependencies use exact version pins
- **Dev/Prod separation:** Development dependencies isolated from production

## Security Features

### Authentication & Authorization
- Flask session management for browser-based requests
- Per-session rating tracking (no persistent user sessions)
- No password storage (data is read-only for demo)

### Data Protection
- SQLite for development (in-memory during tests)
- PostgreSQL for production with basic password protection
- No sensitive data stored in code or config files
- Use environment variables for secrets (`.env` ignored)

### Network Security
- Nginx reverse proxy with security headers:
  - `X-Frame-Options: SAMEORIGIN` (clickjacking protection)
  - `X-Content-Type-Options: nosniff` (MIME type sniffing prevention)
  - `X-XSS-Protection: 1; mode=block` (XSS prevention)
  - `Referrer-Policy: strict-origin-when-cross-origin`
- Rate limiting (10 req/s general, 100 req/s API)
- HTTPS support available (commented in nginx.conf)

### Input Validation
- Flask-SQLAlchemy ORM prevents SQL injection
- Jinja2 template engine auto-escapes to prevent XSS
- Input validation in route handlers
- CSRF protection available (Flask-WTF can be added if needed)

### Error Handling
- Generic error messages (no stack traces to users)
- Detailed logging in containers for debugging
- Health checks verify service availability

## CI/CD Security

### Automated Scanning
- Security workflow runs on every PR and daily schedule
- Tests run before merge (88% coverage requirement)
- Code review before merge (AI-powered analysis)
- Docker builds tested and scanned

### Secrets Management
- No secrets committed to repo
- Dependabot secrets scanning enabled
- GitHub Actions use environment variables only
- Production passwords via env vars

## Deployment Security

### Docker Production
```bash
# Use environment variables for sensitive data
export DB_PASSWORD=your_secure_password

# Start with security defaults
docker compose -f docker-compose.prod.yml up -d
```

### SSL/TLS
HTTPS is optional but recommended for production:
- Option 1: Self-signed certificates (testing)
- Option 2: Let's Encrypt (production)
- See [DOCKER.md](radiocalico/docker_doc/DOCKER.md#ssltls-production---optional) for setup

## Known Limitations

1. **No persistent authentication:** Demo application, not production-ready for multi-user auth
2. **No audit logging:** Session/activity logging not implemented
3. **HTTPS optional:** Can be added but not enforced in this demo
4. **No 2FA:** Not implemented for this demo application

## Third-Party Dependencies

Security scanning includes monitoring of:
- **Python packages:** Flask, Flask-SQLAlchemy, psycopg2
- **System libraries:** Python 3.12 slim image
- **Docker base images:** python:3.12-slim, postgres:16-alpine, nginx:alpine
- **GitHub Actions:** Maintained by GitHub/community

See `radiocalico/requirements.txt` for full dependency list.

## Security Checklist for Contributors

Before submitting a PR:

- [ ] No hardcoded secrets (API keys, passwords, tokens)
- [ ] No SQL injection vulnerabilities
- [ ] No XSS vulnerabilities
- [ ] Input validation on user-facing endpoints
- [ ] Error messages don't leak sensitive info
- [ ] Dependencies are up-to-date
- [ ] Unit tests pass (88% coverage minimum)
- [ ] Security scanning passes (no high/critical findings)

## Security Tools

| Tool | Purpose | Frequency |
|------|---------|-----------|
| **Bandit** | Python SAST | Every PR + daily |
| **Safety** | Dependency vulnerabilities | Every PR + daily |
| **TruffleHog** | Secrets scanning | Every PR + daily |
| **Trivy** | Container image scanning | Every PR |
| **Hadolint** | Dockerfile linting | Every PR |
| **CodeQL** | Code analysis | Every PR + daily |
| **Dependabot** | Dependency updates | Weekly |
| **pytest** | Unit tests | Every PR |

## Contact

For security questions or concerns (non-vulnerability):
- Open a discussion in GitHub Discussions
- For vulnerabilities, see "Reporting Security Vulnerabilities" above

## References

- [OWASP Top 10](https://owasp.org/www-project-top-ten/)
- [Flask Security](https://flask.palletsprojects.com/en/2.3.x/security/)
- [Docker Security Best Practices](https://docs.docker.com/engine/security/)
- [Nginx Security](https://nginx.org/en/docs/http/ngx_http_core_module.html#variables_http)

## Version History

| Date | Changes |
|------|---------|
| 2026-08-10 | Initial security policy document |

.PHONY: help setup minify minify-watch dev prod stop logs test test-coverage security build clean perf perf-commit

# Variables
VENV_DIR := venv
PYTHON := $(VENV_DIR)/bin/python
PIP := $(VENV_DIR)/bin/pip
DOCKER_COMPOSE_DEV := docker compose
DOCKER_COMPOSE_PROD := docker compose -f docker-compose.prod.yml
DB_PASSWORD_ENV := $(shell echo $$DB_PASSWORD)

# Colors for output
BLUE := \033[0;34m
GREEN := \033[0;32m
YELLOW := \033[0;33m
NC := \033[0m # No Color

help: ## Show this help message
	@echo "$(BLUE)Radio Calico - Make Targets$(NC)"
	@echo ""
	@echo "$(GREEN)Development:$(NC)"
	@echo "  make setup          - Set up virtual environment and install dependencies"
	@echo "  make dev            - Start development server (SQLite, port 5000)"
	@echo "  make dev-clean      - Clean and start fresh development environment"
	@echo ""
	@echo "$(GREEN)Minification:$(NC)"
	@echo "  make minify         - Minify CSS and HTML assets once"
	@echo "  make minify-watch   - Watch and auto-minify CSS/HTML on changes"
	@echo ""
	@echo "$(GREEN)Production:$(NC)"
	@echo "  make prod           - Start production stack (PostgreSQL, Nginx, port 80)"
	@echo "  make prod-build     - Build production images"
	@echo ""
	@echo "$(GREEN)Testing:$(NC)"
	@echo "  make test           - Run all tests with pytest"
	@echo "  make test-coverage  - Run tests with coverage report"
	@echo "  make test-watch     - Run tests in watch mode (requires pytest-watch)"
	@echo ""
	@echo "$(GREEN)Security:$(NC)"
	@echo "  make security       - Run local security analysis (Bandit, Safety)"
	@echo "  make security-docker - Run full security stack in Docker"
	@echo ""
	@echo "$(GREEN)Performance:$(NC)"
	@echo "  make perf           - Generate performance analysis report (PERFORMANCE.md)"
	@echo "  make perf-commit    - Generate report and commit it to git"
	@echo ""
	@echo "$(GREEN)Utilities:$(NC)"
	@echo "  make logs-dev       - View development logs"
	@echo "  make logs-prod      - View production logs"
	@echo "  make stop           - Stop all containers"
	@echo "  make clean          - Clean up containers and volumes"
	@echo "  make build          - Build Docker images"
	@echo "  make health         - Check health endpoints"
	@echo ""
	@echo "$(GREEN)Examples:$(NC)"
	@echo "  make test && make dev             - Run tests then start dev"
	@echo "  make minify                       - Minify assets before commit"
	@echo "  make minify-watch                 - Auto-minify during development"
	@echo "  make security                     - Run local security analysis"
	@echo "  make perf                         - Generate performance report"
	@echo "  make perf-commit                  - Generate and commit performance report"
	@echo "  DB_PASSWORD=mysecret make prod    - Start prod with custom DB password"
	@echo "  make test && make security        - Test and verify security"

## Setup & Installation

setup: ## Set up virtual environment and install dependencies
	@echo "$(BLUE)Setting up Python virtual environment...$(NC)"
	python3 -m venv $(VENV_DIR)
	@echo "$(BLUE)Installing dependencies...$(NC)"
	$(PIP) install --upgrade pip
	$(PIP) install -r requirements.txt
	@echo "$(GREEN)✅ Setup complete!$(NC)"
	@echo "Activate with: source $(VENV_DIR)/bin/activate"

## Asset Minification

minify: ## Minify CSS and HTML assets once
	@echo "$(BLUE)🔧 Running asset minification...$(NC)"
	$(PYTHON) scripts/minify.py
	@echo "$(GREEN)✅ Minification complete$(NC)"

minify-watch: ## Watch and auto-minify CSS/HTML on changes
	@echo "$(BLUE)👀 Starting minification watch mode...$(NC)"
	$(PYTHON) scripts/minify.py watch

## Development Mode

dev: ## Start development server (Flask + SQLite)
	@echo "$(BLUE)🚀 Starting Radio Calico in DEVELOPMENT mode...$(NC)"
	@echo "   - Flask debug enabled"
	@echo "   - Hot reload on file changes"
	@echo "   - SQLite database"
	@echo "   - Accessible at http://127.0.0.1:5000"
	@echo ""
	$(DOCKER_COMPOSE_DEV) up

dev-clean: ## Clean and start fresh development environment
	@echo "$(BLUE)Cleaning up development environment...$(NC)"
	$(DOCKER_COMPOSE_DEV) down --remove-orphans -v
	rm -f instance/radiocalico.db
	@echo "$(GREEN)✅ Development environment cleaned$(NC)"
	$(MAKE) dev

dev-stop: ## Stop development container
	@echo "$(BLUE)Stopping development container...$(NC)"
	$(DOCKER_COMPOSE_DEV) down

## Production Mode

prod: ## Start production stack (PostgreSQL + Gunicorn + Nginx)
	@if [ -z "$(DB_PASSWORD_ENV)" ]; then \
		echo "$(YELLOW)❌ ERROR: DB_PASSWORD environment variable is required for production!$(NC)"; \
		echo ""; \
		echo "Set a secure password before starting:"; \
		echo "  export DB_PASSWORD=\$$(openssl rand -base64 32)"; \
		echo "  echo \"Save this password securely: \$$DB_PASSWORD\""; \
		echo ""; \
		echo "Then run: make prod"; \
		echo ""; \
		echo "Or use .env.production file:"; \
		echo "  cp .env.production.example .env.production"; \
		echo "  # Edit .env.production and set DB_PASSWORD"; \
		echo "  docker compose -f docker-compose.prod.yml --env-file .env.production up -d"; \
		exit 1; \
	fi
	@echo "$(BLUE)🚀 Starting Radio Calico in PRODUCTION mode...$(NC)"
	@echo "   - Gunicorn with 4 workers"
	@echo "   - PostgreSQL database"
	@echo "   - Nginx reverse proxy"
	@echo "   - Health checks enabled"
	@echo "   - Accessible at http://localhost"
	@echo ""
	@export DB_PASSWORD="$(DB_PASSWORD_ENV)" && $(DOCKER_COMPOSE_PROD) up -d
	@echo "$(GREEN)✅ Services running in background$(NC)"
	@echo "   View logs:  make logs-prod"
	@echo "   Stop:       make stop"
	@echo "   Health:     make health"

prod-build: ## Build production Docker images
	@echo "$(BLUE)Building production Docker images...$(NC)"
	docker build --target=prod -t radiocalico:prod .
	@echo "$(GREEN)✅ Production images built$(NC)"

prod-stop: ## Stop production stack
	@echo "$(BLUE)Stopping production stack...$(NC)"
	$(DOCKER_COMPOSE_PROD) down

## Testing

test: ## Run all tests with pytest
	@echo "$(BLUE)Running tests...$(NC)"
	$(PYTHON) -m pytest tests/ -v

test-coverage: ## Run tests with coverage report (HTML + terminal)
	@echo "$(BLUE)Running tests with coverage...$(NC)"
	$(PYTHON) -m pytest --cov=app --cov-report=html --cov-report=term-missing tests/
	@echo "$(GREEN)✅ Coverage report generated$(NC)"
	@echo "   HTML report: htmlcov/index.html"

test-specific: ## Run specific test file (usage: make test-specific TEST=tests/test_api.py)
	@if [ -z "$(TEST)" ]; then \
		echo "$(YELLOW)Usage: make test-specific TEST=tests/test_file.py$(NC)"; \
		exit 1; \
	fi
	@echo "$(BLUE)Running $(TEST)...$(NC)"
	$(PYTHON) -m pytest $(TEST) -v

test-watch: ## Run tests in watch mode (requires pytest-watch)
	@echo "$(BLUE)Running tests in watch mode...$(NC)"
	$(PYTHON) -m ptw tests/ -- -v

## Security Testing

security: ## Run local security analysis (Bandit, Safety)
	@echo "$(BLUE)🔐 Running local security analysis...$(NC)"
	@echo ""
	@echo "$(BLUE)Installing security tools...$(NC)"
	$(PYTHON) -m pip install --upgrade bandit safety
	@echo ""
	@echo "$(BLUE)Running Bandit (Python SAST)...$(NC)"
	$(PYTHON) -m bandit -r app -f csv -o /tmp/bandit-report.csv
	$(PYTHON) -m bandit -r app -f txt
	@echo ""
	@echo "$(BLUE)Running Safety (Dependency check)...$(NC)"
	$(PYTHON) -m safety scan --json
	@echo ""
	@echo "$(GREEN)✅ Security analysis complete$(NC)"
	@echo "   Full reports: See output above"
	@echo "   Bandit CSV: /tmp/bandit-report.csv"

security-docker: ## Run Docker-based security checks (Trivy + Hadolint)
	@echo "$(BLUE)🔐 Running Docker-based security checks...$(NC)"
	@echo ""
	@echo "$(BLUE)Building production Docker image...$(NC)"
	docker build --target=prod -t radiocalico:prod . > /dev/null 2>&1
	@echo "$(GREEN)✅ Image built$(NC)"
	@echo ""
	@echo "$(BLUE)Running Trivy vulnerability scanner on Docker image...$(NC)"
	@docker run --rm -v /var/run/docker.sock:/var/run/docker.sock aquasec/trivy image --severity HIGH,CRITICAL radiocalico:prod
	@echo ""
	@echo "$(BLUE)Running Hadolint Dockerfile linter...$(NC)"
	@if command -v hadolint >/dev/null 2>&1; then \
		echo "$(GREEN)✓ Hadolint found locally$(NC)"; \
		hadolint Dockerfile || true; \
	else \
		echo "$(YELLOW)✓ Running Hadolint in Docker...$(NC)"; \
		docker run --rm -i hadolint/hadolint < Dockerfile || true; \
	fi
	@echo ""
	@echo "$(GREEN)✅ Docker security checks complete$(NC)"
	@echo ""
	@echo "$(BLUE)Full CI/CD security stack coverage:$(NC)"
	@echo "  ✅ Docker image scanning (Trivy) - Done above"
	@echo "  ✅ Dockerfile linting (Hadolint) - Done above"
	@echo "  ✅ Python security (Bandit + Safety) - Run: make security"
	@echo "  → Secrets scanning (TruffleHog) - Push PR to trigger"
	@echo "  → Code analysis (CodeQL) - Push PR to trigger"

## Logging & Monitoring

logs-dev: ## View development logs
	@echo "$(BLUE)Development logs:$(NC)"
	$(DOCKER_COMPOSE_DEV) logs -f

logs-prod: ## View production logs
	@echo "$(BLUE)Production logs:$(NC)"
	$(DOCKER_COMPOSE_PROD) logs -f

health: ## Check health endpoints
	@echo "$(BLUE)Checking health endpoints...$(NC)"
	@echo "Development (port 5000):"
	@curl -s http://localhost:5000/api/health || echo "$(YELLOW)Dev not running$(NC)"
	@echo ""
	@echo "Production (port 80):"
	@curl -s http://localhost/api/health || echo "$(YELLOW)Prod not running$(NC)"

status: ## Show container status
	@echo "$(BLUE)Container Status:$(NC)"
	@echo "Development:"
	@$(DOCKER_COMPOSE_DEV) ps || true
	@echo ""
	@echo "Production:"
	@$(DOCKER_COMPOSE_PROD) ps || true

## Building & Images

build: ## Build Docker images (dev and prod)
	@echo "$(BLUE)Building Docker images...$(NC)"
	docker build --target=dev -t radiocalico:dev .
	docker build --target=prod -t radiocalico:prod .
	@echo "$(GREEN)✅ Docker images built$(NC)"
	docker images | grep radiocalico

build-dev: ## Build development Docker image only
	@echo "$(BLUE)Building development image...$(NC)"
	docker build --target=dev -t radiocalico:dev .
	@echo "$(GREEN)✅ Development image built$(NC)"

build-prod: ## Build production Docker image only
	@echo "$(BLUE)Building production image...$(NC)"
	docker build --target=prod -t radiocalico:prod .
	@echo "$(GREEN)✅ Production image built$(NC)"

## Cleanup

stop: ## Stop all containers (dev and prod)
	@echo "$(BLUE)Stopping all containers...$(NC)"
	@$(DOCKER_COMPOSE_DEV) down 2>/dev/null || true
	@$(DOCKER_COMPOSE_PROD) down 2>/dev/null || true
	@echo "$(GREEN)✅ All containers stopped$(NC)"

clean: ## Remove containers, volumes, and cache
	@echo "$(BLUE)Cleaning up containers, volumes, and cache...$(NC)"
	@$(DOCKER_COMPOSE_DEV) down -v 2>/dev/null || true
	@$(DOCKER_COMPOSE_PROD) down -v 2>/dev/null || true
	@find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	@find . -type f -name "*.pyc" -delete 2>/dev/null || true
	@rm -rf .pytest_cache htmlcov .coverage 2>/dev/null || true
	@echo "$(GREEN)✅ Cleanup complete$(NC)"

clean-db: ## Remove database files (development only)
	@echo "$(BLUE)Removing database files...$(NC)"
	rm -f instance/radiocalico.db
	@echo "$(GREEN)✅ Database files removed$(NC)"

## Performance Analysis

perf: ## Generate performance analysis report (PERFORMANCE.md)
	@echo "$(BLUE)📊 Generating performance analysis report...$(NC)"
	@$(PYTHON) ../.github/scripts/generate_perf_report.py
	@echo ""
	@echo "$(GREEN)✅ Report complete!$(NC)"
	@echo "   File: PERFORMANCE.md"
	@echo "   Review the recommendations and prioritize optimizations"

perf-commit: perf ## Generate performance report and commit it
	@echo "$(BLUE)📝 Committing performance report...$(NC)"
	@if git diff --quiet PERFORMANCE.md 2>/dev/null && ! git ls-files --others --exclude-standard | grep -q PERFORMANCE.md; then \
		echo "$(YELLOW)⚠ No changes to PERFORMANCE.md$(NC)"; \
	else \
		git add PERFORMANCE.md && \
		git commit -m "docs: Update performance analysis report" && \
		echo "$(GREEN)✅ Performance report committed$(NC)" || echo "$(YELLOW)⚠ No changes to commit$(NC)"; \
	fi

## Quick Workflows

run: dev ## Alias for 'make dev'

start-prod: prod ## Alias for 'make prod'

all-tests: clean setup test ## Clean, setup, and run all tests

reset: clean setup ## Full reset: clean and reinstall dependencies
	@echo "$(GREEN)✅ Project reset to clean state$(NC)"
	@echo "Run 'make dev' to start development"

.DEFAULT_GOAL := help

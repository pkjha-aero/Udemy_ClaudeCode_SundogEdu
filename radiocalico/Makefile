.PHONY: help setup minify minify-watch arch arch-html dev prod stop logs test test-coverage security build clean perf perf-commit db-init-dev db-clean-dev db-reset-dev db-backup-dev db-status-dev db-init-prod db-clean-prod db-reset-prod db-backup-prod db-restore-prod db-status-prod db-status db-backup db-help

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
	@echo "$(GREEN)Documentation & Architecture:$(NC)"
	@echo "  make arch           - View system architecture (Mermaid diagrams in ARCHITECTURE.md)"
	@echo "  make arch-html      - Generate HTML version of architecture diagrams"
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
	@echo "$(GREEN)Database Management:$(NC)"
	@echo "  make db-status      - Show database status (dev and prod)"
	@echo "  make db-backup      - Backup both databases"
	@echo "  make db-help        - Show all database commands"
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
	@echo "  make arch                         - View architecture diagrams"
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

## Architecture & Documentation

arch: ## View system architecture diagrams (in ARCHITECTURE.md)
	@echo "$(BLUE)📐 System Architecture - Radio Calico$(NC)"
	@echo ""
	@echo "$(GREEN)✅ No installation needed - diagrams render automatically!$(NC)"
	@echo ""
	@echo "9 Mermaid diagrams in ARCHITECTURE.md:"
	@echo "  1️⃣  High-Level Architecture"
	@echo "  2️⃣  Component Architecture"
	@echo "  3️⃣  Data Flow - Rating Workflow"
	@echo "  4️⃣  Docker Deployment Architecture"
	@echo "  5️⃣  API Endpoints Architecture"
	@echo "  6️⃣  Database Schema (ER Diagram)"
	@echo "  7️⃣  Performance Optimization Layers"
	@echo "  8️⃣  Deployment Environments"
	@echo "  9️⃣  Security Architecture"
	@echo ""
	@echo "$(GREEN)Viewing options:$(NC)"
	@echo "  • GitHub:             https://github.com/pkjha-aero/Udemy_ClaudeCode_SundogEdu/blob/main/radiocalico/ARCHITECTURE.md"
	@echo "  • VS Code:            Install 'Markdown Preview Mermaid Support' extension"
	@echo "  • Mermaid Live:       https://mermaid.live/ (copy/paste diagrams)"
	@echo "  • Complete guide:     See ARCHITECTURE-VIEWING-GUIDE.md"
	@echo ""
	@echo "$(GREEN)Info:$(NC)"
	@echo "  • Works with clean and edited builds (pure documentation)"
	@echo "  • NOT a build dependency"
	@echo "  • Optional: make arch-html (requires npm, only for PNG/SVG export)"
	@echo ""

arch-html: ## Generate HTML version of architecture diagrams
	@echo "$(BLUE)🌐 Generating HTML architecture diagrams...$(NC)"
	@if command -v mmdc >/dev/null 2>&1; then \
		echo "$(GREEN)✓ mermaid-cli found$(NC)"; \
		mmdc -i ARCHITECTURE.md -o ARCHITECTURE.html || echo "$(YELLOW)⚠️  Generation failed (optional)$(NC)"; \
	else \
		echo "$(YELLOW)ℹ️  mermaid-cli not installed (optional)$(NC)"; \
		echo "Install with: npm install -g @mermaid-js/mermaid-cli"; \
		echo "Or use: https://mermaid.live/ for interactive viewing"; \
	fi

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

## Database Management

db-help: ## Show all database commands
	@echo "$(BLUE)Database Management - Radio Calico$(NC)"
	@echo ""
	@echo "$(GREEN)Development (SQLite):$(NC)"
	@echo "  make db-init-dev    - Initialize dev database (manual)"
	@echo "  make db-clean-dev   - Remove dev database (hard delete)"
	@echo "  make db-reset-dev   - Clean + reinitialize (fresh start)"
	@echo "  make db-backup-dev  - Backup dev database"
	@echo "  make db-status-dev  - Show dev database status"
	@echo ""
	@echo "$(GREEN)Production (PostgreSQL):$(NC)"
	@echo "  make db-init-prod    - Initialize prod database (manual)"
	@echo "  make db-clean-prod   - Remove prod database (hard delete)"
	@echo "  make db-reset-prod   - Clean + reinitialize (fresh start)"
	@echo "  make db-backup-prod  - Backup prod database"
	@echo "  make db-restore-prod - Restore from backup (BACKUP=file.sql)"
	@echo "  make db-status-prod  - Show prod database status"
	@echo ""
	@echo "$(GREEN)Both:$(NC)"
	@echo "  make db-status      - Show status of both databases"
	@echo "  make db-backup      - Backup both databases"
	@echo ""
	@echo "$(GREEN)When to clean:$(NC)"
	@echo "  • Testing (want fresh data)"
	@echo "  • Schema changes (models.py updated)"
	@echo "  • Data corruption (invalid state)"
	@echo "  • Production reset (complete wipe)"
	@echo ""
	@echo "See DATABASE-MANAGEMENT.md for complete guide"
	@echo ""

# Development Database (SQLite)

db-init-dev: ## Initialize development database (manual)
	@echo "$(BLUE)Initializing development database...$(NC)"
	@if [ -f instance/radiocalico.db ]; then \
		echo "$(YELLOW)⚠️  Database already exists at instance/radiocalico.db$(NC)"; \
		exit 1; \
	fi
	$(PYTHON) -c "from app import create_app; create_app().app_context().push(); from flask_sqlalchemy import SQLAlchemy; print('Database initialized')"
	@echo "$(GREEN)✅ Development database initialized$(NC)"

db-clean-dev: ## Remove development database (hard delete)
	@echo "$(BLUE)Removing development database...$(NC)"
	@if [ ! -f instance/radiocalico.db ]; then \
		echo "$(YELLOW)⚠️  Database not found (already removed)$(NC)"; \
		exit 0; \
	fi
	@echo "$(YELLOW)⚠️  This will DELETE all development data$(NC)"
	@read -p "Continue? (y/N) " -n 1 -r; \
	echo; \
	if [[ $$REPLY =~ ^[Yy]$$ ]]; then \
		rm -f instance/radiocalico.db && echo "$(GREEN)✅ Database removed$(NC)"; \
	else \
		echo "$(YELLOW)Cancelled$(NC)"; \
	fi

db-reset-dev: ## Clean and reinitialize development database (fresh start)
	@echo "$(BLUE)Resetting development database...$(NC)"
	make db-clean-dev
	make dev

db-backup-dev: ## Backup development database
	@echo "$(BLUE)Backing up development database...$(NC)"
	@if [ ! -f instance/radiocalico.db ]; then \
		echo "$(YELLOW)⚠️  Database not found, nothing to backup$(NC)"; \
		exit 1; \
	fi
	cp instance/radiocalico.db instance/radiocalico.db-backup
	@echo "$(GREEN)✅ Backup created: instance/radiocalico.db-backup$(NC)"

db-status-dev: ## Show development database status
	@echo "$(BLUE)Development Database Status:$(NC)"
	@if [ -f instance/radiocalico.db ]; then \
		echo "$(GREEN)✓ Database exists$(NC)"; \
		ls -lh instance/radiocalico.db | awk '{print "  Size: " $$5}'; \
		stat -f "  Modified: %Sm" instance/radiocalico.db 2>/dev/null || stat -c "  Modified: %y" instance/radiocalico.db 2>/dev/null; \
		echo "$(YELLOW)Note: Use sqlite3 to inspect data$(NC)"; \
		echo "  sqlite3 instance/radiocalico.db '.tables'"; \
	else \
		echo "$(YELLOW)⚠️  Database not found (will be created on next 'make dev')$(NC)"; \
	fi
	@echo ""

# Production Database (PostgreSQL)

db-init-prod: ## Initialize production database (manual)
	@if [ -z "$(DB_PASSWORD_ENV)" ]; then \
		echo "$(YELLOW)⚠️  ERROR: DB_PASSWORD environment variable required$(NC)"; \
		exit 1; \
	fi
	@echo "$(BLUE)Initializing production database...$(NC)"
	@docker exec radiocalico-postgres psql -U radiocalico -c "SELECT version();" > /dev/null 2>&1 && \
		echo "$(YELLOW)⚠️  Database already exists$(NC)" || \
		(echo "$(GREEN)✅ PostgreSQL ready$(NC)" && echo "Database initializes automatically on first start")

db-clean-prod: ## Remove production database (hard delete)
	@echo "$(BLUE)Removing production database...$(NC)"
	@echo "$(YELLOW)⚠️  This will DELETE all production data (irreversible!)$(NC)"
	@read -p "Continue? (y/N) " -n 1 -r; \
	echo; \
	if [[ $$REPLY =~ ^[Yy]$$ ]]; then \
		$(DOCKER_COMPOSE_PROD) down > /dev/null 2>&1; \
		docker volume rm radiocalico_radiocalico-db 2>/dev/null && \
			echo "$(GREEN)✅ Production database removed$(NC)" || \
			echo "$(YELLOW)⚠️  Volume already removed$(NC)"; \
	else \
		echo "$(YELLOW)Cancelled$(NC)"; \
	fi

db-reset-prod: ## Clean and reinitialize production database (fresh start)
	@echo "$(BLUE)Resetting production database...$(NC)"
	make db-clean-prod
	@if [ -z "$(DB_PASSWORD_ENV)" ]; then \
		echo "$(YELLOW)Set DB_PASSWORD environment variable first$(NC)"; \
		exit 1; \
	fi
	make prod

db-backup-prod: ## Backup production database
	@echo "$(BLUE)Backing up production database...$(NC)"
	@mkdir -p backups
	@BACKUP_FILE="backups/prod-$$(date +%Y-%m-%d-%H-%M-%S).sql"; \
	docker exec radiocalico-postgres pg_dump -U radiocalico radiocalico > $$BACKUP_FILE 2>/dev/null && \
		echo "$(GREEN)✅ Backup created: $$BACKUP_FILE$(NC)" || \
		(rm -f $$BACKUP_FILE && echo "$(YELLOW)⚠️  PostgreSQL not running, cannot backup$(NC)" && exit 1)

db-restore-prod: ## Restore production database from backup (BACKUP=file.sql)
	@if [ -z "$(BACKUP)" ]; then \
		echo "$(YELLOW)Usage: make db-restore-prod BACKUP=backups/prod-2026-08-12.sql$(NC)"; \
		exit 1; \
	fi
	@if [ ! -f "$(BACKUP)" ]; then \
		echo "$(YELLOW)⚠️  Backup file not found: $(BACKUP)$(NC)"; \
		exit 1; \
	fi
	@echo "$(BLUE)Restoring production database from: $(BACKUP)$(NC)"
	@echo "$(YELLOW)⚠️  This will restore data from backup (overwrites current)$(NC)"
	@read -p "Continue? (y/N) " -n 1 -r; \
	echo; \
	if [[ $$REPLY =~ ^[Yy]$$ ]]; then \
		if docker ps | grep -q radiocalico-postgres; then \
			docker exec -i radiocalico-postgres psql -U radiocalico radiocalico < "$(BACKUP)" && \
				echo "$(GREEN)✅ Database restored$(NC)" || \
				echo "$(YELLOW)⚠️  Restore failed$(NC)"; \
		else \
			echo "$(YELLOW)⚠️  PostgreSQL not running, start production first: make prod$(NC)"; \
			exit 1; \
		fi; \
	else \
		echo "$(YELLOW)Cancelled$(NC)"; \
	fi

db-status-prod: ## Show production database status
	@echo "$(BLUE)Production Database Status:$(NC)"
	@if docker ps | grep -q radiocalico-postgres; then \
		echo "$(GREEN)✓ PostgreSQL container running$(NC)"; \
		docker exec radiocalico-postgres pg_isready -U radiocalico > /dev/null && \
			echo "$(GREEN)✓ Database responsive$(NC)" || \
			echo "$(YELLOW)⚠️  Database not responding$(NC)"; \
		docker volume inspect radiocalico_radiocalico-db 2>/dev/null | grep -q "radiocalico" && \
			echo "$(GREEN)✓ Volume exists: radiocalico_radiocalico-db$(NC)" || \
			echo "$(YELLOW)⚠️  Volume not found$(NC)"; \
		VOLUME_SIZE=$$(docker volume inspect -f "{{.Mountpoint}}" radiocalico_radiocalico-db 2>/dev/null | xargs du -sh 2>/dev/null | awk '{print $$1}'); \
		[ -n "$$VOLUME_SIZE" ] && echo "  Size: $$VOLUME_SIZE" || echo "  Size: unknown"; \
	else \
		echo "$(YELLOW)⚠️  PostgreSQL not running$(NC)"; \
		echo "  Start with: make prod"; \
	fi
	@echo ""

# Universal Database Commands

db-status: ## Show status of both databases
	@make db-status-dev
	@make db-status-prod

db-backup: ## Backup both databases
	@echo "$(BLUE)Backing up all databases...$(NC)"
	@make db-backup-dev 2>/dev/null || true
	@make db-backup-prod 2>/dev/null || true
	@echo "$(GREEN)✅ Backup operations complete$(NC)"

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

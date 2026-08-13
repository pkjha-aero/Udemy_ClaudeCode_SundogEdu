# Multi-stage Dockerfile for Radio Calico
# Build: dev, prod
# Usage: docker build --target=dev -t radiocalico:dev .
#        docker build --target=prod -t radiocalico:prod .

FROM python:3.12-slim as base

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Create app directory
WORKDIR /app

# Copy requirements
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# ============================================================================
# DEVELOPMENT STAGE
# ============================================================================
FROM base as dev

# Install dev dependencies
COPY requirements-dev.txt .
RUN pip install --no-cache-dir -r requirements-dev.txt

# Copy entire app
COPY . .

# Minify assets
RUN python scripts/minify.py

# Create instance directory for database
RUN mkdir -p /app/instance

# Create a non-root user
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

# Expose port
EXPOSE 5000

# Run with debug enabled and reload on changes
CMD ["python", "-m", "flask", "run", "--host=0.0.0.0"]

# ============================================================================
# PRODUCTION STAGE
# ============================================================================
FROM base as prod

# Install gunicorn (before switching to non-root user so pip works)
RUN pip install --no-cache-dir gunicorn==23.0.0

# Copy app (excluding dev files)
COPY --chown=1000:1000 app ./app
COPY --chown=1000:1000 run.py .
COPY --chown=1000:1000 stream_URL.txt .
COPY --chown=1000:1000 RadioCalico_Style_Guide.txt .
COPY --chown=1000:1000 RadioCalicoLogoTM.png .
COPY --chown=1000:1000 scripts ./scripts

# Minify assets (before switching to non-root user so Python can write)
RUN python scripts/minify.py

# Create instance directory for database with correct ownership
RUN mkdir -p /app/instance && chown -R 1000:1000 /app/instance

# Create a non-root user
RUN useradd -m -u 1000 appuser
USER appuser

# Expose port
EXPOSE 5000

# Health check (using built-in urllib, no external dependencies)
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:5000/api/health', timeout=5)" || exit 1

# Run with gunicorn for production
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "4", "--timeout", "120", "--access-logfile", "-", "--error-logfile", "-", "run:app"]

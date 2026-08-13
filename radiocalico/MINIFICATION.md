# Asset Minification for Radio Calico

Automatic CSS and HTML minification is now integrated into the build pipeline for both development and production.

## Overview

Minification reduces asset file sizes by:
- Removing whitespace and comments
- Compressing CSS (rcssmin)
- Compressing HTML (htmlmin2)
- Preserving Jinja2 template logic

**Benefits:**
- Smaller downloads (2.7 KB saved on current assets)
- Faster page loads
- Automatic in Docker builds (dev and prod)
- Optional watch mode for active development

## Usage

### Development

**Minify once before committing:**
```bash
make minify
```

**Auto-minify on file changes (watch mode):**
```bash
make minify-watch
```
This watches `app/static/` and `app/templates/` for changes and minifies automatically.

### Production

Minification runs automatically during Docker build:
```bash
docker build --target=prod -t radiocalico:prod .
```
or via make:
```bash
make prod-build
```

### Manual Script

Run the minification script directly:
```bash
python scripts/minify.py              # Minify once
python scripts/minify.py watch        # Watch mode
```

## How It Works

### Minification Script
Located at `scripts/minify.py`, handles:
- **CSS minification** — removes whitespace, comments via `rcssmin`
- **HTML minification** — removes extra whitespace, comments via `htmlmin2`
- **Jinja2 templates** — preserves template tags (`{{ }}`, `{% %}`)
- **Watch mode** — auto-minifies on file changes

### Docker Integration
- **Dev stage** — `Dockerfile` runs `python scripts/minify.py` after copying app
- **Prod stage** — Same minification step before switching to non-root user
- **Result** — Minified assets in both containers

### Makefile Targets
- `make minify` — Run minification once
- `make minify-watch` — Enable watch mode
- Integrated into `make dev` and `make prod-build` automatically

## Performance Impact

On current Radio Calico assets:
- **index.css** — 3.3 KB → 2.7 KB (20% reduction)
- **player.css** — 4.5 KB → 3.6 KB (21% reduction)
- **index.html** — 2.5 KB → 1.9 KB (22% reduction)
- **player.html** — 10.9 KB → 10.3 KB (5% reduction)

**Total savings:** 2.7 KB per page load

## Workflow

### Before Pushing
```bash
# Option 1: Minify once
make minify

# Option 2: Auto-minify while developing
make minify-watch
```

### In Docker Build
Minification runs automatically (no action needed):
```bash
make dev       # Auto-minifies on startup
make prod      # Auto-minifies during build
docker build   # Auto-minifies during image build
```

### CI/CD
- GitHub Actions doesn't need to run minification separately
- Docker images already contain minified assets from build stage
- Minified files are committed to git (tracked)

## Dependencies

Added to `requirements.txt`:
- `rcssmin==1.1.2` — Fast CSS minification (pure Python)
- `htmlmin2==0.1.13` — HTML minification (preserves templates)

Added to `requirements-dev.txt`:
- `watchdog==4.0.1` — File watching for watch mode

## Troubleshooting

### Watch mode not detecting changes
Ensure watchdog is installed:
```bash
pip install watchdog
```

### Files not minifying in Docker
- Rebuild image: `docker build --target=dev -t radiocalico:dev .`
- Check Docker output for minification step

### Want to skip minification in Docker
Edit `Dockerfile` and comment out `RUN python scripts/minify.py` lines, then rebuild.

## Future Enhancements

- Gzip compression (already enabled via Flask-Compress)
- Image optimization (if needed)
- CSS/JS bundling (if assets grow)
- Source maps for debugging (optional)

## References

- Script: `scripts/minify.py`
- Dockerfile: `Dockerfile` (dev/prod stages)
- Makefile: `Makefile` (minify targets)
- Requirements: `requirements.txt`, `requirements-dev.txt`

# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

# Radio Calico

Local prototype website. Flask + SQLite, native install (no Docker) in a Python virtualenv.

## Stack

- **Webserver**: Flask (app factory pattern in `app/__init__.py`)
- **Database**: SQLite via Flask-SQLAlchemy, file at `instance/radiocalico.db` (auto-created on first run, gitignored)
- **Env**: Python 3.12 virtualenv at `venv/` (gitignored)

## Development

**Setup:**
```bash
python3 -m venv venv
./venv/bin/python -m pip install -r requirements.txt
```

**Run dev server** (debug mode, port 5000):
```bash
./venv/bin/python run.py
```
Server: http://127.0.0.1:5000

## Architecture

**App structure (app factory pattern):**
- `app/__init__.py` — factory function `create_app()`, DB init, seeds default User on startup
- `app/models.py` — four ORM models: `User`, `Item`, `Song`, `Rating` (see Models section below)
- `app/routes.py` — Flask Blueprint with HTML routes and JSON API endpoints
- `app/templates/` — Jinja2 templates for HTML pages

**Models:**
- `User` — name, email (unique); seeded default: Pankaj Jha (pankaj.psu@gmail.com)
- `Item` — name, created_at (app structure allows extensibility; no form to create yet)
- `Song` — title, artist, album, date; created dynamically from player metadata queries
- `Rating` — song_id, session_id, is_thumbs_up (one rating per song per session, enforced by unique constraint)

**Session management:** Flask session stores `session_id` (per-browser); used to track one rating per song per unique visitor. No database cleanup needed—stale ratings accumulate but don't affect queries (filtered by current session_id).

**Routes:**
- GET `/` → homepage (lists users, items, add-user form)
- GET `/player` → HLS radio player page
- POST `/users` → add user (duplicate email rejected)
- GET `/api/health`, `/api/items`, `/api/users` → JSON responses
- GET `/api/song/current` → song metadata + user's rating for that song (creates Song if new)
- POST `/api/song/rate` → thumbs up/down (creates or updates Rating)

## Radio Player

- **Route**: `/player` → http://127.0.0.1:5000/player
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

## Current state

- Homepage features hero section with "Listen Now" CTA, user list + add-user form (duplicate email validation), items list, link to player. Full brand styling applied.
- Radio player at `/player` streams lossless HLS with teal header/logo, two-column layout, dynamic album art, track info, and session-based song ratings (thumbs up/down with aggregate counts).
- `Item` model exists but no form to create items yet.

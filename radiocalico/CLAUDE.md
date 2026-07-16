# Radio Calico

Local prototype website. Flask + SQLite, native install (no Docker) in a Python virtualenv.

## Stack

- **Webserver**: Flask (app factory pattern in `app/__init__.py`)
- **Database**: SQLite via Flask-SQLAlchemy, file at `instance/radiocalico.db` (auto-created by Flask, gitignored)
- **Env**: Python 3.12 virtualenv at `venv/` (gitignored)

## Setup & run

```bash
python3 -m venv venv
./venv/bin/python -m pip install -r requirements.txt
./venv/bin/python run.py
```

Server: http://127.0.0.1:5000

## Project structure

- `app/__init__.py` — app factory, DB init, seeds a default `User` on first run if none exists
- `app/models.py` — `User` (name, email) and `Item` (name, created_at) models
- `app/routes.py` — routes for `/`, `/player`, `POST /users`, `/api/items`, `/api/users`, `/api/health`
- `app/templates/index.html` — homepage: lists users, has an add-user form, lists items, link to player
- `app/templates/player.html` — HLS radio player page with Play/Pause/Stop controls
- `run.py` — dev server entrypoint (debug mode on, port 5000)
- `stream_URL.txt` — CloudFront HLS stream endpoint URL

## Radio Player

- **Route**: `/player` → http://127.0.0.1:5000/player
- **Stream**: Lossless HLS from CloudFront CDN (m3u8 playlist)
- **Library**: HLS.js (loaded from CDN) for cross-browser playback
- **Fallback**: Native HLS support on Safari/iOS
- **Features**: Play, Pause, Stop buttons; status indicator; responsive design

## Environment (this machine)

- OS: Ubuntu 24.04.4 LTS (Noble), user `pkjha`, hostname `pkjha-xps`, kernel `6.8.0-124-generic`
- Repo lives on an NTFS-mounted drive at `/media/pkjha/Win_D/...` (see exec-bit gotcha below)

## Environment gotchas (this machine)

- `python3-venv` is not installed by default on this system — needed `sudo apt install python3.12-venv` before `python3 -m venv` would work. **User prefers to run any sudo commands themselves in a separate terminal** rather than have Claude run them.
- `pip install --user` is blocked by PEP 668 (externally-managed-environment) on this system — always use a venv, not `--user` or `--break-system-packages`.
- The repo lives on an NTFS-mounted drive (`/media/.../Win_D/...`). Executable bits on files created inside `venv/bin/` (e.g. `pip`) aren't reliably set, so `./venv/bin/pip` may fail with "Permission denied". Use `./venv/bin/python -m pip ...` instead — it always works.
- The actual git repository root is **one directory above** `radiocalico/` (i.e. `Udemy_ClaudeCode_SundogEdu/`), not `radiocalico/` itself. Run git commands from there, or be aware `git status`/`git log` at the repo root will show `radiocalico/` as a subpath.

## Current state

- Homepage at `/` lists all users, has an add-user form (with duplicate email validation), lists items, and links to the radio player.
- A default user (Pankaj Jha, pankaj.psu@gmail.com) is seeded on first run.
- Radio player at `/player` streams lossless audio via HLS.js with Play/Pause/Stop controls.
- `Item` model exists but no form to create items yet.

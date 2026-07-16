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
- `app/routes.py` — `/` (homepage), `POST /users` (add user via form), `/api/items`, `/api/users`, `/api/health`
- `app/templates/index.html` — homepage: lists users, has an add-user form, lists items
- `run.py` — dev server entrypoint (debug mode on, port 5000)

## Environment (this machine)

- OS: Ubuntu 24.04.4 LTS (Noble), user `pkjha`, hostname `pkjha-xps`, kernel `6.8.0-124-generic`
- Repo lives on an NTFS-mounted drive at `/media/pkjha/Win_D/...` (see exec-bit gotcha below)

## Environment gotchas (this machine)

- `python3-venv` is not installed by default on this system — needed `sudo apt install python3.12-venv` before `python3 -m venv` would work. **User prefers to run any sudo commands themselves in a separate terminal** rather than have Claude run them.
- `pip install --user` is blocked by PEP 668 (externally-managed-environment) on this system — always use a venv, not `--user` or `--break-system-packages`.
- The repo lives on an NTFS-mounted drive (`/media/.../Win_D/...`). Executable bits on files created inside `venv/bin/` (e.g. `pip`) aren't reliably set, so `./venv/bin/pip` may fail with "Permission denied". Use `./venv/bin/python -m pip ...` instead — it always works.
- The actual git repository root is **one directory above** `radiocalico/` (i.e. `Udemy_ClaudeCode_SundogEdu/`), not `radiocalico/` itself. Run git commands from there, or be aware `git status`/`git log` at the repo root will show `radiocalico/` as a subpath.

## Current state

- A default user (seeded from git config / user email) shows on the homepage.
- Users can be added via the on-page form (POSTs to `/users`); duplicate emails and empty fields are silently ignored.
- `Item` model exists but nothing currently creates items (no form yet).

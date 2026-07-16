# Radio Calico (local prototype)

Flask webserver + SQLite database for local prototyping.

## Setup

```bash
python3 -m venv venv
./venv/bin/python -m pip install -r requirements.txt
```

## Run

```bash
./venv/bin/python run.py
```

Server runs at http://127.0.0.1:5000

- `/` — homepage
- `/api/health` — health check
- `/api/items` — JSON list of items

The SQLite database is created automatically at `instance/radiocalico.db` on first run.

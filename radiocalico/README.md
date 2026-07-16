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

## Features

- `/` — homepage with user management and items list
- `/player` — **HLS radio player** for lossless audio streaming
- `/api/health` — health check
- `/api/items` — JSON list of items
- `/api/users` — JSON list of users

## Radio Player

Access the HLS radio player at: **http://127.0.0.1:5000/player**

- Plays lossless HLS stream from CloudFront CDN
- Play/Pause/Stop controls
- Browser compatibility: Chrome, Firefox, Safari, Edge (iOS 10+, Android 6+)
- Uses HLS.js library for cross-browser support

The SQLite database is created automatically at `instance/radiocalico.db` on first run.

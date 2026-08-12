# Radio Calico REST API

Complete REST API documentation for Radio Calico backend services.

## Base URL

- **Development:** `http://127.0.0.1:5000`
- **Production:** `http://localhost` (via Nginx reverse proxy)

## Authentication

Currently uses Flask session-based identification. No API keys required. Session IDs are automatically generated and stored in browser cookies.

## CSRF Protection

- **Form endpoints** (`/users` POST) require CSRF tokens
- **JSON API endpoints** (`/api/*`) are CSRF-exempt (stateless operations)
- No additional token headers needed for API calls

---

## Endpoints

### Health Check

#### GET `/api/health`

Check application health status.

**Response:**
```json
{
  "status": "ok"
}
```

**Status Code:** `200 OK`

**Use Case:** Load balancer health checks, monitoring

---

### Users

#### GET `/api/users`

List all users.

**Response:**
```json
[
  {
    "id": 1,
    "name": "Pankaj Jha",
    "email": "pankaj.psu@gmail.com"
  }
]
```

**Status Code:** `200 OK`

---

#### POST `/users` (Form)

Add a new user. Requires CSRF token (form-based).

**Request:**
```html
<form method="POST" action="/users">
  <input type="hidden" name="csrf_token" value="{{ csrf_token() }}">
  <input type="text" name="name" placeholder="Name" required>
  <input type="email" name="email" placeholder="Email" required>
  <button type="submit">Add User</button>
</form>
```

**Parameters:**
- `name` (string, required): User's full name
- `email` (string, required): Email address (must be unique)

**Response:** Redirects to homepage on success

**Status Codes:**
- `302 Found` - Success, redirect to `/`
- Invalid input: silently ignored (no error feedback)

**Validation:**
- Email must be unique across users
- Both name and email required
- Whitespace trimmed automatically

---

### Items

#### GET `/api/items`

List all items.

**Response:**
```json
[
  {
    "id": 1,
    "name": "Sample Item",
    "created_at": "2026-08-12T04:53:00"
  }
]
```

**Status Code:** `200 OK`

**Note:** Item creation via API not yet implemented. Use database seed or admin interface.

---

### Songs & Ratings

#### GET `/api/song/current`

Get current song metadata and user's rating.

**Query Parameters:**
- `title` (string): Song title
- `artist` (string): Artist name
- `album` (string, optional): Album name
- `date` (string, optional): Release date (YYYY-MM-DD)

**Response:**
```json
{
  "id": 42,
  "title": "Song Title",
  "artist": "Artist Name",
  "album": "Album Name",
  "date": "2026-08-12",
  "thumbs_up": 15,
  "thumbs_down": 3,
  "user_rating": "up"
}
```

**Status Code:** `200 OK`

**Behavior:**
- Creates song record if it doesn't exist
- Returns user's rating for this song in current session
- `user_rating` values: `"up"`, `"down"`, or `null`

**Example:**
```bash
curl "http://localhost:5000/api/song/current?title=Song%20Name&artist=Artist%20Name&album=Album"
```

---

#### POST `/api/song/rate`

Submit a rating (thumbs up or down) for a song.

**Request:**
```json
{
  "song_id": 42,
  "is_thumbs_up": true
}
```

**Parameters:**
- `song_id` (integer, required): Song ID from `/api/song/current`
- `is_thumbs_up` (boolean, required): `true` for thumbs up, `false` for thumbs down

**Response:**
```json
{
  "id": 42,
  "title": "Song Title",
  "artist": "Artist Name",
  "album": "Album Name",
  "date": "2026-08-12",
  "thumbs_up": 16,
  "thumbs_down": 3,
  "user_rating": "up"
}
```

**Status Codes:**
- `200 OK` - Rating updated (existing rating changed)
- `201 Created` - New rating created
- `400 Bad Request` - Missing or invalid parameters
- `404 Not Found` - Song ID doesn't exist
- `415 Unsupported Media Type` - Invalid Content-Type (must be `application/json`)

**Validation:**
- `song_id` must reference existing song
- `is_thumbs_up` must be boolean
- One rating per user per song (updates existing)

**Example:**
```bash
curl -X POST http://localhost:5000/api/song/rate \
  -H "Content-Type: application/json" \
  -d '{"song_id": 42, "is_thumbs_up": true}'
```

---

## Session Management

### Session ID

- Auto-generated on first API call (uses `secrets.token_hex(16)`)
- Stored in Flask session (browser cookie)
- Persists across page refreshes
- Isolates ratings per user/browser

### User Identification

No login required. Sessions are per-browser:
- User A's browser gets Session X
- User B's browser gets Session Y
- Ratings are tied to session, not account

---

## Error Handling

### HTTP Status Codes

| Code | Meaning | Common Cause |
|------|---------|--------------|
| 200 | Success | Valid request processed |
| 201 | Created | New resource created |
| 302 | Redirect | Form submission successful |
| 400 | Bad Request | Missing/invalid parameters |
| 404 | Not Found | Song/resource doesn't exist |
| 415 | Unsupported Media Type | Wrong Content-Type header |

### Error Response Example

```json
HTTP/1.1 400 Bad Request
Content-Type: application/json

{
  "error": "Missing required parameter: song_id"
}
```

---

## Rate Limiting

**Development:** No rate limiting

**Production (via Nginx):**
- General API: 10 requests/second per IP
- `/api/song/rate`: 100 requests/second per IP

See `nginx.conf` for configuration.

---

## Testing

Run the test suite to validate API behavior:

```bash
make test                    # Run all tests (164 tests)
make test-specific TEST=tests/test_api.py  # API tests only
```

Test files:
- `tests/test_api.py` - API endpoint tests
- `tests/test_integration.py` - Full workflow tests
- `tests/test_session_management.py` - Session isolation tests

---

## Examples

### Get current song and rate it

```bash
# Step 1: Fetch current song
RESPONSE=$(curl -s "http://localhost:5000/api/song/current?title=Example&artist=Artist")
SONG_ID=$(echo $RESPONSE | jq '.id')

# Step 2: Rate it
curl -X POST http://localhost:5000/api/song/rate \
  -H "Content-Type: application/json" \
  -d "{\"song_id\": $SONG_ID, \"is_thumbs_up\": true}"
```

### Get all users and items

```bash
# Fetch users
curl http://localhost:5000/api/users | jq .

# Fetch items
curl http://localhost:5000/api/items | jq .
```

### Health check for monitoring

```bash
# Simple health check
curl http://localhost:5000/api/health

# With verbose output
curl -v http://localhost:5000/api/health
```

---

## Database Schema

See [CLAUDE.md](CLAUDE.md#models) for detailed schema documentation.

**Key Tables:**
- `user` - User profiles
- `song` - Track metadata (auto-created from player metadata)
- `rating` - Thumbs up/down votes (unique: song_id + session_id)
- `item` - Generic items list

---

## See Also

- [CLAUDE.md](CLAUDE.md) - Architecture & development guide
- [DOCKER.md](DOCKER.md) - Containerization & deployment
- [SECURITY.md](../SECURITY.md) - Security policies & vulnerability reporting

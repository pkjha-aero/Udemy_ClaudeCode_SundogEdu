# Features & Roadmap

Overview of Radio Calico's current capabilities and planned enhancements.

---

## ✅ Current Features

### Radio Player
- **HLS Audio Streaming** - Lossless audio via CloudFront CDN
- **Play/Pause Controls** - Full playback control
- **Volume Control** - Adjustable volume with default 100%
- **Time Display** - Current time and duration
- **Dynamic Quality** - Stream quality adapts to bandwidth and metadata
- **Browser Support** - Chrome, Firefox, Safari, Edge (iOS 10+, Android 6+)
- **Cross-browser Playback** - HLS.js library with native HLS fallback

### User Management
- **Add Users** - Form-based user creation
- **Unique Emails** - Email deduplication across users
- **User List** - Display all users on homepage
- **JSON API** - Get users via `/api/users`

### Track Rating System
- **Thumbs Up/Down** - Rate individual tracks
- **Vote Counts** - Aggregate votes per song
- **Session Tracking** - One vote per user per song (per session/browser)
- **Real-time Updates** - Vote counts update instantly
- **Rating Persistence** - Ratings persist across page refreshes

### Items Catalog
- **Items Display** - View items on homepage
- **JSON API** - Get items via `/api/items`
- **Extensible** - Database structure ready for item creation UI

### API & Integration
- **RESTful Endpoints** - `/api/health`, `/api/items`, `/api/users`, `/api/song/*`
- **JSON Responses** - Machine-readable API
- **CORS Ready** - Can be extended for cross-origin requests
- **Session Management** - Per-browser session tracking
- **Error Handling** - Comprehensive HTTP status codes

### Security
- **CSRF Protection** - Form submission protection
- **Session Isolation** - Per-browser vote isolation
- **Input Validation** - Email, name, and parameter validation
- **SQL Injection Prevention** - SQLAlchemy ORM
- **XSS Prevention** - Jinja2 auto-escaping

### Development & Operations
- **Docker Containerization** - Dev/prod separated builds
- **PostgreSQL Support** - Production-grade database
- **Nginx Reverse Proxy** - Production web server
- **Health Checks** - Automated container restart on failure
- **Comprehensive Testing** - 164 unit tests, 88% coverage
- **Security Scanning** - 7-tool automated analysis (Bandit, Safety, Trivy, etc.)
- **CI/CD Pipeline** - Automated testing, code review, builds
- **Asset Minification** - Automatic CSS/HTML compression (20% reduction, 2.7 KB saved)
- **Makefile Targets** - One-command dev/test/prod operations

### Documentation
- **API Reference** - Complete endpoint documentation (API.md)
- **Development Guide** - Architecture and setup (CLAUDE.md)
- **Docker Guide** - Containerization details (DOCKER.md)
- **Security Policy** - Vulnerability disclosure (SECURITY.md)
- **Style Guide** - Brand and design guidelines
- **Changelog** - Project evolution tracking

---

## 🚀 Planned Features

### High Priority (Next Sprint)

#### Item Creation UI
- **Web Form** - Create items via homepage
- **Validation** - Name/description validation
- **Database Sync** - Store in `item` table
- **API Support** - POST `/api/items`

#### Enhanced Player
- **Playlist Support** - Queue multiple songs
- **Shuffle/Repeat** - Playback modes
- **Skip Forward/Back** - Navigate through tracks
- **Now Playing** - Display current track info

#### User Authentication
- **Login/Logout** - Basic authentication
- **User Sessions** - Persistent login across browsers
- **Password Security** - Hashed passwords
- **Session Timeout** - Auto-logout after inactivity

### Medium Priority (2-3 Sprints)

#### Advanced Rating Features
- **User Profiles** - View user's rating history
- **Rating Distribution** - Show like/dislike ratio per song
- **Trending Songs** - Most-rated tracks
- **User Recommendations** - Suggested songs based on ratings

#### Search & Discovery
- **Song Search** - Find songs by title/artist
- **Advanced Filters** - Filter by album, date, rating
- **Sort Options** - Sort by rating, date, popularity

#### Notifications
- **New Song Alerts** - Notify when new tracks added
- **Comment Notifications** - Notify on shared ratings
- **System Alerts** - Important updates to users

### Lower Priority (Future Consideration)

#### Social Features
- **Comments** - Per-song discussion
- **Sharing** - Share ratings/playlists
- **Following** - Follow other users
- **Private Playlists** - Saved collections

#### Analytics & Insights
- **Play Statistics** - Track listening patterns
- **User Analytics** - Active users, engagement metrics
- **Charts** - Most-played songs, trending ratings
- **Export Reports** - CSV/JSON data exports

#### Music Library Management
- **Upload Tracks** - Self-hosted audio
- **Metadata Editing** - Update song info
- **Cover Art** - Custom album artwork
- **Audio Formats** - Support various codecs

#### Mobile App
- **Native iOS** - Swift/SwiftUI app
- **Native Android** - Kotlin/Jetpack app
- **Offline Mode** - Cache tracks locally
- **Push Notifications** - Mobile alerts

---

## 📊 Feature Status Legend

| Status | Meaning |
|--------|---------|
| ✅ | Implemented and tested |
| 🚀 | Planned for next release |
| 📋 | On roadmap, not scheduled |
| ⚠️ | Partially implemented |
| ❌ | Considered but rejected |

---

## Known Limitations

### Current Constraints

1. **Single Radio Stream**
   - Only one HLS stream URL supported
   - Cannot switch between stations
   - Stream metadata auto-fetched, not configurable

2. **Session-based Only**
   - No persistent user login
   - Votes per session (per browser), not per account
   - Rating isolation per browser

3. **Manual Database Management**
   - No UI for adding songs/items
   - Requires direct database access for initial data
   - No bulk import tools

4. **No Real-time Sync**
   - Page refresh needed for vote updates from other users
   - No WebSocket support yet
   - Polling-based updates only

5. **Rate Limiting**
   - Development: No rate limiting
   - Production: 10 req/s general, 100 req/s API (configurable in Nginx)

6. **Storage**
   - SQLite in development (single-connection limit)
   - PostgreSQL in production (requires setup)
   - No external file storage (all in-database)

---

## Performance Targets

- **Page Load:** < 2 seconds
- **API Response:** < 100ms
- **Audio Buffering:** < 3 seconds
- **Concurrent Users:** 1,000+ (in production)
- **Database:** Support millions of ratings
- **Uptime:** 99.9% (production SLA)

---

## Browser Compatibility

| Browser | Desktop | Mobile |
|---------|---------|--------|
| Chrome | ✅ Latest 2 versions | ✅ Latest 2 versions |
| Firefox | ✅ Latest 2 versions | ✅ Latest 2 versions |
| Safari | ✅ Latest 2 versions | ✅ iOS 10+ |
| Edge | ✅ Latest 2 versions | ✅ Chromium-based |
| Internet Explorer | ❌ Not supported | N/A |

---

## Contributing to Features

Want to help implement a feature?

1. **Report a Bug** - Open a GitHub issue with reproduction steps
2. **Suggest a Feature** - Discuss in GitHub issues
3. **Submit a PR** - Fork, branch, make changes, and create a pull request
4. **Code Review** - All changes require review before merging

See [SECURITY.md](../SECURITY.md) for security reporting guidelines.

---

## Feedback

Have ideas for Radio Calico?

- **GitHub Issues** - Report bugs or request features
- **Discussions** - Share ideas and get feedback
- **Pull Requests** - Contribute code directly

We welcome all feedback and contributions!

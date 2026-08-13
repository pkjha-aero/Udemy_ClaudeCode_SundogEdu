# Radio Calico - System Architecture

Comprehensive system design for the Radio Calico application, showing data flow, component interactions, and deployment topology.

## 📖 Viewing the Diagrams

**No installation needed!** All diagrams render automatically in:
- ✅ **GitHub** — Rendered in the repository
- ✅ **VS Code** — Install "Markdown Preview Mermaid Support" extension
- ✅ **GitLab** — Native Mermaid support
- ✅ **Notion, Confluence** — Paste markdown content
- ✅ **Mermaid Live Editor** — https://mermaid.live/ (copy/paste diagrams)

**Optional:** Export diagrams to PNG/SVG:
- Install `mermaid-cli`: `npm install -g @mermaid-js/mermaid-cli`
- Run: `make arch-html` or `mmdc -i ARCHITECTURE.md -o ARCHITECTURE.html`
- This is **NOT required** for viewing or building the application

## High-Level Architecture

```mermaid
graph TB
    subgraph "External Services"
        CDN["CloudFront CDN<br/>(HLS Stream)"]
    end

    subgraph "Client Layer"
        Browser["🌐 Web Browser<br/>(Chrome, Firefox, Safari)"]
        JS["HLS.js Library<br/>(Audio Playback)"]
    end

    subgraph "Development Stack"
        DevServer["Flask Dev Server<br/>(Port 5000)<br/>Debug Mode"]
        DevDB["SQLite<br/>(instance/radiocalico.db)"]
    end

    subgraph "Production Stack"
        Nginx["Nginx Reverse Proxy<br/>(Port 80/443)<br/>Rate Limiting<br/>Security Headers"]
        Gunicorn["Gunicorn Workers<br/>(4 workers)<br/>Port 5000 internal"]
        ProdDB["PostgreSQL 16<br/>(Port 5432)<br/>Alpine"]
    end

    subgraph "Application Layer"
        Routes["Flask Routes<br/>GET / /player<br/>POST /users"]
        API["JSON API<br/>GET /api/*<br/>POST /api/song/rate"]
        Models["ORM Models<br/>User, Item<br/>Song, Rating"]
        Helpers["Template Helpers<br/>Context Preparation<br/>URL Generation"]
        Templates["Jinja2 Templates<br/>index.html<br/>player.html"]
        Assets["Static Assets<br/>CSS (Minified)<br/>Images, Fonts"]
    end

    subgraph "Features"
        Player["🎵 Radio Player<br/>HLS Streaming<br/>Play/Pause/Volume"]
        Rating["👍 Rating System<br/>Thumbs Up/Down<br/>Vote Counts"]
        UserMgmt["👤 User Management<br/>Add Users<br/>Email Validation"]
    end

    CDN -->|Stream URL| JS
    Browser -->|HTTP/S| Nginx
    Browser -->|HTTP/S| DevServer
    JS -->|Audio Stream| CDN

    DevServer --> Routes
    Nginx --> Gunicorn

    Routes --> API
    Routes --> Templates
    API --> Models
    Templates --> Helpers
    Helpers --> Models

    Models --> DevDB
    Models --> ProdDB

    Templates --> Assets
    Browser -->|Request| Routes
    Browser -->|Request| API

    Routes --> Player
    API --> Rating
    Routes --> UserMgmt
    Models --> Player
    Models --> Rating
    Models --> UserMgmt
```

## Component Architecture

```mermaid
graph LR
    subgraph "Presentation Layer"
        HTML["HTML Templates<br/>- index.html<br/>- player.html"]
        CSS["CSS (Minified)<br/>- index.css<br/>- player.css"]
        JS_Client["Client JS<br/>- HLS.js (CDN)<br/>- Event handlers"]
    end

    subgraph "Application Layer"
        Factory["App Factory<br/>app/__init__.py<br/>- create_app()<br/>- DB init<br/>- Seeds data"]
        
        Routes["Route Handlers<br/>app/routes.py<br/>- GET /\n- GET /player<br/>- POST /users<br/>- GET/POST /api/*"]
        
        Helpers["Template Helpers<br/>app/template_helpers.py<br/>- prepare_index_context<br/>- prepare_player_context<br/>- URL generation"]
    end

    subgraph "Data Layer"
        ORM["SQLAlchemy ORM<br/>app/models.py<br/>- User<br/>- Item<br/>- Song<br/>- Rating"]
        
        DB_Dev["SQLite<br/>Development<br/>Single file"]
        
        DB_Prod["PostgreSQL<br/>Production<br/>Multi-connection"]
    end

    subgraph "Infrastructure"
        Session["Flask Session<br/>- session_id<br/>- Per-browser<br/>- Rating tracking"]
        
        Compress["Compression<br/>- Flask-Compress<br/>- Gzip (60-70%)"]
        
        Minify["Asset Minification<br/>- rcssmin (20% reduction)<br/>- htmlmin2 (5-22%)<br/>- Automatic in builds"]
    end

    HTML --> CSS
    CSS --> JS_Client
    
    Factory --> Routes
    Routes --> Helpers
    Helpers --> ORM
    
    Routes --> Session
    Routes --> Compress
    Routes --> Minify
    
    ORM --> DB_Dev
    ORM --> DB_Prod
```

## Data Flow - User Rating Workflow

```mermaid
sequenceDiagram
    participant Browser
    participant Flask as Flask Server
    participant Session as Flask Session
    participant Models as ORM Models
    participant DB as Database

    Browser->>Flask: POST /api/song/rate<br/>(song_id, is_thumbs_up)
    Flask->>Session: Get session_id
    Flask->>Models: Create/Update Rating<br/>(song_id, session_id, is_thumbs_up)
    Models->>DB: INSERT or UPDATE
    DB-->>Models: Confirm
    Models-->>Flask: Rating object
    Flask->>Models: Get aggregate votes<br/>for song_id
    Models->>DB: COUNT(*) GROUP BY is_thumbs_up
    DB-->>Models: Vote counts
    Models-->>Flask: {thumbs_up: N, thumbs_down: M}
    Flask-->>Browser: 200 OK<br/>{thumbs_up: N, thumbs_down: M}
    Browser->>Browser: Update DOM<br/>Show vote counts
```

## Docker Deployment Architecture

```mermaid
graph TB
    subgraph "Development (docker compose)"
        DevVol["Volume: app/"]
        DevImg["Image: radiocalico:dev<br/>Python 3.12 slim<br/>Flask dev server<br/>Hot reload"]
        DevCont["Container: radiocalico-dev<br/>Port: 5000<br/>Mount: /app (host)<br/>Env: DEBUG=True"]
    end

    subgraph "Production (docker-compose.prod.yml)"
        subgraph "Reverse Proxy"
            NginxImg["Image: nginx:alpine<br/>Reverse proxy<br/>Rate limiting<br/>Security headers"]
            NginxCont["Container: nginx<br/>Port: 80/443<br/>Config: nginx.conf"]
        end
        
        subgraph "Application"
            GunicornImg["Image: radiocalico:prod<br/>Python 3.12 slim<br/>Gunicorn WSGI<br/>4 workers"]
            GunicornCont["Container: radiocalico-prod<br/>Port: 5000 (internal)<br/>Env: PRODUCTION=true"]
        end
        
        subgraph "Database"
            PgImg["Image: postgres:16-alpine<br/>Official PostgreSQL"]
            PgCont["Container: postgres<br/>Port: 5432 (internal)<br/>Vol: radiocalico-db<br/>Env: DB_PASSWORD"]
        end
    end

    DevCont -->|Reads/Writes| DevVol
    DevImg -->|Container| DevCont
    
    NginxImg -->|Container| NginxCont
    GunicornImg -->|Container| GunicornCont
    PgImg -->|Container| PgCont
    
    NginxCont -->|Port 80| GunicornCont
    GunicornCont -->|TCP 5432| PgCont
```

## API Endpoints Architecture

```mermaid
graph LR
    Client["Browser Client"]
    
    subgraph "HTML Routes"
        Root["GET /"]
        Player["GET /player"]
        AddUser["POST /users"]
    end
    
    subgraph "JSON API"
        Health["GET /api/health"]
        Items["GET /api/items"]
        Users["GET /api/users"]
        CurrentSong["GET /api/song/current"]
        RateSong["POST /api/song/rate"]
    end
    
    subgraph "Response Data"
        HTML_Root["Homepage<br/>- Users list<br/>- Items list<br/>- Add user form"]
        HTML_Player["Player Page<br/>- Player UI<br/>- Album art<br/>- Vote counts"]
        JSON_Health["{status: ok}"]
        JSON_Items["[{id, name, created_at}]"]
        JSON_Users["[{id, name, email}]"]
        JSON_Song["{title, artist, album,<br/>date, is_thumbs_up}"]
        JSON_Vote["{thumbs_up, thumbs_down}"]
    end
    
    Client --> Root
    Client --> Player
    Client --> AddUser
    Client --> Health
    Client --> Items
    Client --> Users
    Client --> CurrentSong
    Client --> RateSong
    
    Root --> HTML_Root
    Player --> HTML_Player
    Health --> JSON_Health
    Items --> JSON_Items
    Users --> JSON_Users
    CurrentSong --> JSON_Song
    RateSong --> JSON_Vote
```

## Database Schema

```mermaid
erDiagram
    USER ||--o{ ITEM : "has"
    USER ||--o{ RATING : "creates"
    SONG ||--o{ RATING : "rated_by"
    
    USER {
        int id PK
        string name
        string email UK "unique"
        datetime created_at
    }
    
    ITEM {
        int id PK
        int user_id FK
        string name
        datetime created_at
    }
    
    SONG {
        int id PK
        string title
        string artist
        string album
        datetime date
        datetime created_at
    }
    
    RATING {
        int id PK
        int song_id FK
        string session_id
        boolean is_thumbs_up
        datetime created_at
        unique "song_id, session_id"
    }
```

## Performance Optimization Layers

```mermaid
graph TB
    subgraph "Frontend Optimization"
        FontPreconnect["Font Preconnect<br/>~80ms saved"]
        AssetMinify["Asset Minification<br/>CSS: 20% reduction<br/>HTML: 5-22% reduction"]
        CSSCodeSplit["CSS Code Split<br/>27KB → 4KB + 9.4KB"]
    end
    
    subgraph "API Optimization"
        MetadataCache["Metadata Caching<br/>localStorage<br/>70% fewer API calls"]
        ConditionalPolling["Conditional Polling<br/>Only when playing"]
    end
    
    subgraph "Database Optimization"
        SQLOptimization["Query Optimization<br/>func.count() aggregation<br/>~100ms saved"]
        IndexOptimization["Database Indexes<br/>On foreign keys<br/>On session_id"]
    end
    
    subgraph "Transport Optimization"
        GzipCompression["Gzip Compression<br/>60-70% size reduction<br/>100-200ms saved"]
        HTTPCacheHeaders["HTTP Cache Headers<br/>200-400ms on repeat visits"]
    end
    
    subgraph "Results"
        Total["~550ms Total Improvement<br/>Faster loads & better UX"]
    end
    
    FontPreconnect --> Total
    AssetMinify --> Total
    CSSCodeSplit --> Total
    MetadataCache --> Total
    ConditionalPolling --> Total
    SQLOptimization --> Total
    GzipCompression --> Total
    HTTPCacheHeaders --> Total
```

## Deployment Environments

```mermaid
graph TB
    subgraph "Local Development"
        Dev["make dev<br/>- Flask debug mode<br/>- SQLite database<br/>- Hot reload<br/>- Port 5000"]
    end
    
    subgraph "Local Docker Dev"
        DockerDev["make dev (Docker)<br/>- docker compose up<br/>- Flask in container<br/>- SQLite in volume<br/>- Port 5000"]
    end
    
    subgraph "Local Docker Production"
        DockerProd["make prod<br/>- PostgreSQL in container<br/>- Gunicorn + Nginx<br/>- Health checks<br/>- Port 80"]
    end
    
    subgraph "CI/CD Pipeline"
        GitHub["GitHub Actions<br/>- Unit tests (88% coverage)<br/>- Security scanning<br/>- AI code review<br/>- Docker build & push"]
    end
    
    subgraph "Production Deployment"
        Prod["Production Server<br/>- PostgreSQL (managed)<br/>- Gunicorn load balancer<br/>- Nginx reverse proxy<br/>- SSL/TLS termination<br/>- Rate limiting"]
    end
    
    Dev -.->|Test locally| DockerDev
    DockerDev -.->|Validate stack| DockerProd
    DockerProd -->|Push branch| GitHub
    GitHub -->|Pass CI| Prod
```

## Security Architecture

```mermaid
graph TB
    subgraph "Input Layer"
        CSRF["CSRF Protection<br/>Flask-WTF<br/>Token validation"]
        InputVal["Input Validation<br/>Email format<br/>Name length<br/>Parameter checks"]
    end
    
    subgraph "Application Layer"
        SQLInject["SQL Injection Prevention<br/>SQLAlchemy ORM<br/>Parameterized queries"]
        XSSPrev["XSS Prevention<br/>Jinja2 auto-escaping<br/>Template safety"]
        SessionIso["Session Isolation<br/>Per-browser session_id<br/>Vote per session"]
    end
    
    subgraph "Transport Layer"
        HTTPS["HTTPS/TLS<br/>SSL certificate<br/>Encrypted traffic"]
        Headers["Security Headers<br/>X-Frame-Options<br/>X-XSS-Protection<br/>Content-Security-Policy"]
    end
    
    subgraph "Infrastructure Layer"
        RateLimit["Rate Limiting<br/>10 req/s general<br/>100 req/s API<br/>Nginx rules"]
        NonRoot["Non-root User<br/>Container UID 1000<br/>Reduced attack surface"]
    end
    
    subgraph "Scanning"
        SAST["SAST Analysis<br/>Bandit (Python)"]
        DepScan["Dependency Scan<br/>Safety check<br/>Dependabot"]
        ImageScan["Image Scanning<br/>Trivy<br/>CVE detection"]
        SecScan["Secrets Scanning<br/>TruffleHog<br/>Credential detection"]
    end
    
    CSRF --> InputVal
    InputVal --> SQLInject
    SQLInject --> XSSPrev
    XSSPrev --> SessionIso
    SessionIso --> HTTPS
    HTTPS --> Headers
    Headers --> RateLimit
    RateLimit --> NonRoot
    NonRoot --> SAST
    SAST --> DepScan
    DepScan --> ImageScan
    ImageScan --> SecScan
```

## Technology Stack Summary

| Layer | Technology | Purpose |
|-------|-----------|---------|
| **Frontend** | HTML5, Jinja2, CSS3 | User interface |
| **Audio** | HLS.js, CloudFront CDN | Streaming playback |
| **Backend** | Flask, Python 3.12 | Web server & API |
| **Database** | SQLite (dev), PostgreSQL (prod) | Data persistence |
| **ORM** | SQLAlchemy | Database abstraction |
| **Templating** | Jinja2 | Dynamic HTML generation |
| **WSGI** | Gunicorn (prod only) | Application server |
| **Reverse Proxy** | Nginx (prod only) | Load balancing, security |
| **Containerization** | Docker, Docker Compose | Reproducible deployments |
| **Compression** | gzip, rcssmin, htmlmin2 | Asset optimization |
| **Testing** | pytest, pytest-flask, pytest-cov | Quality assurance |
| **Security** | Bandit, Safety, Trivy, TruffleHog | Vulnerability scanning |
| **CI/CD** | GitHub Actions | Automated workflows |

## Key Architectural Principles

1. **Separation of Concerns** — Templates focus on display, helpers prepare data, routes handle logic
2. **App Factory Pattern** — Flexible configuration for dev/prod/test environments
3. **Layered Architecture** — Clear boundaries between presentation, application, and data layers
4. **Security by Default** — CSRF protection, SQL injection prevention, XSS escaping, CORS ready
5. **Performance First** — Minification, caching, optimized queries, compression
6. **Infrastructure as Code** — Docker, docker-compose, Makefiles for reproducible environments
7. **Automated Quality** — Tests (164), security scanning (7 tools), AI code review

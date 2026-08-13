# Database Management Guide

Complete reference for managing Radio Calico databases in development and production environments.

---

## Quick Reference

### Database Overview

| Environment | Database | Location | Cleanup | When to Clean |
|-------------|----------|----------|---------|---------------|
| **Dev** | SQLite | `instance/radiocalico.db` | `make db-clean-dev` | Start fresh, test data reset |
| **Prod** | PostgreSQL | Docker volume `radiocalico-db` | `make db-clean-prod` | Full reset, data migration |

### Quick Commands

```bash
# Development (SQLite)
make db-init-dev       # Initialize dev database (automatic on first run)
make db-clean-dev      # Remove dev database (hard reset)
make db-reset-dev      # Clean + reinitialize dev database

# Production (PostgreSQL)
make db-init-prod      # Initialize prod database (automatic on first start)
make db-clean-prod     # Remove prod database (hard reset)
make db-reset-prod     # Clean + reinitialize prod database

# Universal
make db-status         # Show database status (both dev and prod)
make db-backup         # Backup dev database
```

---

## Development Database (SQLite)

### Overview

- **Type**: SQLite 3 (file-based)
- **Location**: `instance/radiocalico.db` (gitignored)
- **Auto-created**: Yes, on first `make dev` run
- **Data seeded**: Yes, default User created automatically
- **Multi-connection**: Single connection (development only)
- **Lifecycle**: Recreated when needed, temporary data

### Initialization

**Automatic (Recommended):**
```bash
make dev  # ← Auto-creates database on first run
# Database initialized with default User (Pankaj Jha)
```

**Manual:**
```bash
make db-init-dev  # Create database manually (if needed)
```

### When to Clean Up Dev Database

✅ **CLEAN when:**
1. **Testing** — Start fresh with clean data
   ```bash
   make db-reset-dev  # Clean + reinitialize
   make test
   ```

2. **Data Corruption** — Database corrupted or invalid state
   ```bash
   make db-clean-dev
   make dev  # ← Recreate with fresh schema
   ```

3. **Schema Changes** — After modifying models.py
   ```bash
   make db-reset-dev  # Rebuild schema
   make dev
   ```

4. **Testing User Workflows** — Need predictable starting state
   ```bash
   make db-reset-dev
   # Now run manual tests with known initial state
   ```

5. **Debugging** — Remove test data that interferes with debugging
   ```bash
   make db-clean-dev
   make dev
   ```

❌ **DO NOT CLEAN when:**
- Just making code changes (no schema changes)
- Running normal development iteration
- Preserving test data for ongoing development
- Running integration tests (test fixture handles it)

### Development Database Commands

**View database:**
```bash
sqlite3 instance/radiocalico.db ".tables"
sqlite3 instance/radiocalico.db "SELECT * FROM user;"
```

**Backup dev database (before cleaning):**
```bash
make db-backup-dev  # Copies to backup.db
```

**Restore dev database:**
```bash
cp instance/radiocalico.db-backup instance/radiocalico.db
make dev
```

---

## Production Database (PostgreSQL)

### Overview

- **Type**: PostgreSQL 16 (Alpine Linux)
- **Location**: Docker volume `radiocalico-db` (persistent)
- **Auto-created**: Yes, on first `make prod` start
- **Data seeded**: Yes, default User created automatically
- **Multi-connection**: Yes (production-ready)
- **Lifecycle**: Persists across container restarts, requires explicit cleanup
- **Connection**: `postgresql://radiocalico:$DB_PASSWORD@postgres:5432/radiocalico`

### Initialization

**Automatic (Recommended):**
```bash
export DB_PASSWORD=$(openssl rand -base64 32)
make prod  # ← Auto-creates PostgreSQL container + database
# Database initialized with default User (Pankaj Jha)
```

**Manual:**
```bash
make db-init-prod  # Initialize database (container must be running)
```

### When to Clean Up Prod Database

✅ **CLEAN when:**

1. **Full Reset** — Start with completely fresh data
   ```bash
   make db-clean-prod
   export DB_PASSWORD=$(openssl rand -base64 32)
   make prod  # ← Fresh PostgreSQL with clean data
   ```

2. **Data Migration** — Migrating to new schema or production environment
   ```bash
   make db-clean-prod  # Old data removed
   make db-init-prod   # New schema created
   ```

3. **Testing Production Behavior** — Verify production setup works end-to-end
   ```bash
   make db-clean-prod
   make prod
   make health  # Verify everything initializes correctly
   ```

4. **Security Incident** — Data breach or compromise
   ```bash
   make db-clean-prod  # Remove compromised data
   make db-init-prod   # Fresh database
   ```

5. **Storage Cleanup** — Reduce Docker volume size
   ```bash
   make db-clean-prod  # Frees disk space
   # Remove old backups: rm -f backups/*.sql
   ```

❌ **DO NOT CLEAN when:**
- Just testing application features
- Running integration tests (use separate test database)
- Preserving production data
- In active production (use backup-restore instead)
- Debugging application logic (don't need data reset)

### Production Database Commands

**Check database connection:**
```bash
docker exec radiocalico-postgres pg_isready -U radiocalico
```

**Connect to database:**
```bash
docker exec -it radiocalico-postgres psql -U radiocalico radiocalico
# Then: SELECT * FROM "user";
```

**Backup prod database (before cleaning):**
```bash
make db-backup-prod  # Dumps to backups/prod-$(date).sql
```

**Restore prod database:**
```bash
# Stop database first
make prod-stop
# Remove volume
docker volume rm radiocalico_radiocalico-db
# Restore from backup
make db-restore-prod BACKUP=backups/prod-2026-08-12.sql
# Start production
make prod
```

---

## Database Lifecycle

### Development Workflow

```
1. make dev
   ↓
   [Check if instance/radiocalico.db exists]
   ├─ NO → [Create schema, seed User] → [Start Flask]
   └─ YES → [Start Flask with existing data]

2. [Develop and test]
   ├─ Just code changes? → No cleanup needed
   ├─ Schema changes? → make db-reset-dev
   └─ Want fresh data? → make db-clean-dev

3. make test
   ↓
   [Use test fixtures, separate test database]
   ↓
   [Cleanup automatic, no production data affected]
```

### Production Workflow

```
1. make prod
   ↓
   [Check if radiocalico-db volume exists]
   ├─ NO → [Create PostgreSQL container, init schema, seed User]
   └─ YES → [Start PostgreSQL with existing data]

2. [Run application]
   ├─ Data accumulates in volume
   ├─ Persistent across restarts
   └─ Require explicit cleanup to remove

3. Maintenance
   ├─ Backup regularly → make db-backup-prod
   ├─ Monitor size → docker volume ls
   └─ Clean only when needed → make db-clean-prod
```

---

## Common Workflows

### Workflow 1: Fresh Development Start

```bash
# Clone repo
git clone <repo>
cd radiocalico

# First run (auto-creates everything)
make dev
# Database created at instance/radiocalico.db
# User table seeded with default user
# Ready for testing

# Later, want completely fresh data?
make db-reset-dev
# Database removed and recreated
```

### Workflow 2: Test Integration After Schema Change

```bash
# Modified models.py (added new field)
vim app/models.py

# Reset database with new schema
make db-reset-dev
make test
# Tests run with correct schema
```

### Workflow 3: Production Deployment Verification

```bash
# Test production setup in local environment
export DB_PASSWORD=$(openssl rand -base64 32)
make prod

# Verify it initializes correctly
make health
docker exec radiocalico-postgres psql -U radiocalico radiocalico
# SELECT * FROM "user";  ← Should show default user

# Before actual deployment
make db-backup-prod
# Keep backup safe, then deploy
```

### Workflow 4: Backup and Restore (Production)

```bash
# Backup before risky operation
make db-backup-prod  # → backups/prod-2026-08-12.sql

# Something goes wrong?
make prod-stop
docker volume rm radiocalico_radiocalico-db
make db-restore-prod BACKUP=backups/prod-2026-08-12.sql
make prod
# Back to previous state
```

### Workflow 5: CI/CD Testing

```bash
# GitHub Actions runs:
make test
# Uses separate test database (fixtures)
# Production data never affected
# Automatic cleanup after tests
```

---

## Database Status and Inspection

### View Database Status

**Development:**
```bash
make db-status-dev
# Shows:
# - SQLite version
# - File location
# - File size
# - Last modified
# - Number of tables
# - Number of records
```

**Production:**
```bash
make db-status-prod
# Shows:
# - PostgreSQL version
# - Volume name
# - Volume size
# - Container status
# - Number of tables
# - Number of records
```

### Inspect Database Structure

**Development:**
```bash
sqlite3 instance/radiocalico.db
sqlite> .schema
sqlite> .tables
sqlite> SELECT COUNT(*) FROM rating;
```

**Production:**
```bash
docker exec -it radiocalico-postgres psql -U radiocalico radiocalico
postgres=# \dt  -- List tables
postgres=# SELECT COUNT(*) FROM rating;
```

---

## Backup and Restore

### Backup Strategy

**Development (Optional but Recommended):**
```bash
make db-backup-dev
# Creates: instance/radiocalico.db-backup
```

**Production (Strongly Recommended):**
```bash
# Before any risky operation
make db-backup-prod
# Creates: backups/prod-YYYY-MM-DD-HH-MM-SS.sql

# Manual backup
docker exec radiocalico-postgres pg_dump -U radiocalico radiocalico > backup.sql
```

### Restore Strategy

**Development:**
```bash
# If database corrupted:
rm instance/radiocalico.db
cp instance/radiocalico.db-backup instance/radiocalico.db
make dev
```

**Production:**
```bash
# If something goes wrong:
make prod-stop
docker volume rm radiocalico_radiocalico-db
docker volume create radiocalico_radiocalico-db
docker exec -i radiocalico-postgres psql -U radiocalico radiocalico < backup.sql
make prod
```

---

## Makefile Database Targets

### Development Database Targets

```makefile
make db-init-dev    # Initialize SQLite database (manual)
make db-clean-dev   # Remove SQLite database (hard delete)
make db-reset-dev   # Clean + reinitialize (fresh start)
make db-backup-dev  # Backup SQLite database
make db-status-dev  # Show database status
```

### Production Database Targets

```makefile
make db-init-prod    # Initialize PostgreSQL database (manual)
make db-clean-prod   # Remove PostgreSQL database (hard delete)
make db-reset-prod   # Clean + reinitialize (fresh start)
make db-backup-prod  # Backup PostgreSQL database
make db-status-prod  # Show database status
make db-restore-prod # Restore from backup (BACKUP=file.sql)
```

### Universal Database Targets

```makefile
make db-status       # Show status of both dev and prod
make db-backup       # Backup both dev and prod
make db-help         # Show all database commands
```

---

## Decision Tree: When to Clean Database?

```
Is the database causing issues?
├─ YES (corrupted, wrong schema, etc.)
│  └─ Run: make db-reset-dev (or db-reset-prod)
└─ NO ↓

Am I testing something that needs fresh data?
├─ YES (testing user workflows, new features)
│  └─ Run: make db-reset-dev
└─ NO ↓

Did I change the database schema (models.py)?
├─ YES (added/removed fields)
│  └─ Run: make db-reset-dev
└─ NO ↓

Is the database getting too large?
├─ YES (production data accumulated)
│  └─ Backup: make db-backup-prod
│  └─ Clean: make db-clean-prod (only if sure)
└─ NO ↓

KEEP EXISTING DATABASE
(No cleanup needed, just keep developing/running)
```

---

## Troubleshooting

### Problem: "Table already exists" error

**Cause**: Schema mismatch between models.py and database

**Solution**:
```bash
make db-reset-dev  # Clean and recreate schema
make dev
```

### Problem: "Database locked" error

**Cause**: Multiple connections to SQLite or stale connection

**Solution**:
```bash
make dev-stop
make clean-db
make dev
```

### Problem: "Connection refused" on production

**Cause**: PostgreSQL container not running or not ready

**Solution**:
```bash
make prod-stop
make prod
sleep 5  # Wait for PostgreSQL to start
make health
```

### Problem: PostgreSQL volume is too large

**Cause**: Data accumulation over time

**Solution**:
```bash
# Backup first!
make db-backup-prod

# Clean data (if okay to lose)
make db-clean-prod

# Or just remove old backups
rm -f backups/prod-old-*.sql
```

### Problem: Want to verify data before cleaning

**Solution**:
```bash
# Dev
sqlite3 instance/radiocalico.db "SELECT COUNT(*) FROM rating;"

# Prod
docker exec radiocalico-postgres psql -U radiocalico radiocalico \
  -c "SELECT COUNT(*) FROM rating;"

# If data looks okay, proceed with confidence
```

---

## Best Practices

### ✅ Development Best Practices

1. **Let database auto-create on first run**
   ```bash
   make dev  # ← Auto-creates if missing
   ```

2. **Backup before manual cleanup**
   ```bash
   make db-backup-dev
   make db-clean-dev  # Now safe to delete
   ```

3. **Use make targets, not manual deletion**
   ```bash
   make db-reset-dev  # ← Use this
   # NOT: rm instance/radiocalico.db manually
   ```

4. **Check schema after model changes**
   ```bash
   make db-reset-dev
   make test  # Verify new schema works
   ```

### ✅ Production Best Practices

1. **Always backup before cleanup**
   ```bash
   make db-backup-prod  # First
   make db-clean-prod   # Then
   ```

2. **Monitor volume size**
   ```bash
   docker volume ls
   docker volume inspect radiocalico_radiocalico-db
   ```

3. **Never clean production without plan**
   ```bash
   # Know exactly what you're doing
   # Have backup ready
   # Have restore plan tested
   ```

4. **Use separate test database**
   ```bash
   # Don't clean production for testing
   make test  # Uses test fixtures, separate database
   ```

5. **Archive old backups**
   ```bash
   mkdir -p backups/archive
   mv backups/prod-*.sql backups/archive/
   # Keep recent backups in backups/ for quick restore
   ```

### ✅ CI/CD Best Practices

1. **Use test fixtures, not production database**
   ```bash
   # Tests automatically use fixtures
   make test  # Safe, no production data touched
   ```

2. **Create fresh database per test run**
   ```bash
   pytest  # Creates in-memory SQLite for each test
   # Automatic cleanup, zero impact
   ```

3. **Archive test databases**
   ```bash
   # Don't keep test artifacts in git
   # .gitignore handles this automatically
   ```

---

## Summary Table

| Scenario | Command | Dev/Prod | Notes |
|----------|---------|----------|-------|
| First time setup | `make dev` | Dev | Auto-creates everything |
| Just run app | `make dev` | Dev | Reuses existing database |
| Want fresh data | `make db-reset-dev` | Dev | Clean + recreate |
| Test after schema change | `make db-reset-dev` | Dev | New schema needed |
| Running tests | `make test` | Both | Uses fixtures, safe |
| Before cleanup | `make db-backup-dev` | Dev | Always backup first |
| Backup production | `make db-backup-prod` | Prod | Before risky operation |
| Hard reset production | `make db-clean-prod` | Prod | Completely remove data |
| Check database state | `make db-status` | Both | See what exists |
| Restore from backup | `make db-restore-prod` | Prod | Recovery operation |
| Deploy to production | `make prod` | Prod | Auto-init, creates volume |

---

## Key Takeaways

✅ **Databases auto-create** — No manual initialization needed on first run

✅ **Clean only when necessary** — Most development doesn't need cleanup

✅ **Always backup first** — Before any destructive operation

✅ **Tests are safe** — Never affect production data

✅ **Make targets exist** — Use them, don't delete files manually

✅ **Decision tree included** — Know exactly when to clean

✅ **Troubleshooting guide** — Solutions for common problems

✅ **Production checklist** — Best practices for safety

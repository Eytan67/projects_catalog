# Database Setup and Bug Fixes

This document outlines the changes made to set up database creation and fix various import/configuration issues.

## Database Creation
**File: `app/main.py`**
- Added imports: `from db.database import engine, Base`
- Added: `Base.metadata.create_all(bind=engine, checkfirst=True)` to create tables on startup

## Fixed Import/Query Errors
**File: `app/services/project_service.py`**
- Changed from `Project as ProjectSchema` to just `Project` (database model)
- Fixed all function return types and queries to use `Project` model instead of schema
- Fixed all `db.query(ProjectSchema)` to `db.query(Project)`

**File: `app/api/deps.py`**
- Changed import from `db.schemas import Admin` to `db.models import Admin`
- Fixed query from `Admin.id` to `Admin.sso_id` (correct column name)

## Database Configuration
**File: `.env`**
- Fixed DATABASE_URL from `user:password@localhost:5432/projects_catalog` to match Docker credentials
- Added environment variables: `POSTGRES_USER`, `POSTGRES_PASSWORD`, `POSTGRES_DB`, etc.

**File: `docker-compose.yml`**
- Replaced hardcoded values with environment variables and defaults
- Changed from `my_db` to `projects_catalog` database name

## Summary
The main issue was mixing up **database models** (for queries) with **Pydantic schemas** (for API validation). The fixes ensure:

1. Database tables are created automatically on application startup
2. Queries use the correct SQLAlchemy models
3. Database credentials match between Docker and application configuration
4. Configuration is externalized using environment variables
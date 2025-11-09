# Database Analysis Report

## Overview
This application uses **PostgreSQL** as the primary database (configured in docker-compose) and **SQLite** for the v1 version. The database is managed through SQLAlchemy ORM.

## Database Configuration

### Main Application (backend/)
- **Database**: PostgreSQL 15
- **Connection**: `postgresql+psycopg://app:app@localhost:5432/recipe`
- **Pool**: Connection pooling enabled with `pool_pre_ping=True`
- **Session Management**: SQLAlchemy sessionmaker with autoflush/autocommit disabled

### V1 Application (v1/backend/)
- **Database**: SQLite
- **Connection**: `sqlite:///recipes.db`
- **ORM**: SQLModel (built on SQLAlchemy)

## Database Schema

### Tables in Main Application

#### 1. **users**
```sql
- id: INTEGER (PRIMARY KEY)
- email: VARCHAR(255) (UNIQUE, INDEXED)
- password_hash: VARCHAR(255)
```

**Purpose**: User authentication and management
**Usage**: Used in `auth.py` for JWT token validation

#### 2. **evaluations**
```sql
- id: INTEGER (PRIMARY KEY)
- user_id: INTEGER (NOT NULL)
- snapshot: JSON
- locked: BOOLEAN (DEFAULT: true)
- created_at: DATETIME (DEFAULT: utcnow)
```

**Purpose**: Stores user evaluation snapshots from diagnosis flow
**Usage**: Created in `routes/diagnosis.py` when evaluation is locked
**Issues**: 
- Hardcoded `user_id=1` in route handlers
- No foreign key constraint to `users` table
- No index on `user_id` for query performance

#### 3. **flavors**
```sql
- id: INTEGER (PRIMARY KEY)
- user_id: INTEGER (NOT NULL)
- template: JSON
- locked: BOOLEAN (DEFAULT: true)
- created_at: DATETIME (DEFAULT: utcnow)
```

**Purpose**: Stores flavor preference templates
**Usage**: Created in `routes/flavor.py` when flavor is locked
**Issues**: 
- Hardcoded `user_id=1` in route handlers
- No foreign key constraint to `users` table
- No index on `user_id` for query performance

#### 4. **analyses**
```sql
- id: INTEGER (PRIMARY KEY)
- user_id: INTEGER (NOT NULL)
- content: JSON
- created_at: DATETIME (DEFAULT: utcnow)
```

**Purpose**: Stores culinary analysis results
**Usage**: Created in `routes/analysis.py` after compiling evaluation and flavor data
**Issues**: 
- Hardcoded `user_id=1` in route handlers
- No foreign key constraint to `users` table
- Missing import for `get_db` in `analysis.py` (uses walrus operator `...:=get_db`)
- No index on `user_id` for query performance

#### 5. **recipe_runs**
```sql
- id: INTEGER (PRIMARY KEY)
- user_id: INTEGER (NOT NULL)
- request_payload: JSON
- result: JSON
- created_at: DATETIME (DEFAULT: utcnow)
```

**Purpose**: Stores recipe generation requests and results
**Usage**: Created in `routes/recipes.py` when recipes are generated
**Issues**: 
- Hardcoded `user_id=1` in route handlers
- No foreign key constraint to `users` table
- No index on `user_id` for query performance

### Tables in V1 Application

#### 1. **recipe**
```sql
- id: INTEGER (PRIMARY KEY, AUTOINCREMENT)
- name: VARCHAR
- type: VARCHAR (breakfast, lunch, etc.)
- cuisine: VARCHAR
- ingredients: VARCHAR (JSON serialized list)
- instructions: VARCHAR (JSON serialized list)
- calories: FLOAT
- macros: VARCHAR (JSON serialized dict)
- micros: VARCHAR (JSON serialized dict)
- user_info: VARCHAR (JSON serialized dict)
- rating: INTEGER (DEFAULT: 0)
```

**Purpose**: Stores generated recipes
**Issues**: 
- Uses VARCHAR for JSON data instead of native JSON type
- No user_id field to associate recipes with users
- No timestamps for tracking creation/modification

## Critical Issues

### 1. **Missing Foreign Key Relationships**
- All tables reference `user_id` but have no foreign key constraints
- This allows orphaned records and data integrity issues
- **Recommendation**: Add foreign key constraints:
  ```python
  user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), nullable=False, index=True)
  ```

### 2. **Hardcoded User ID**
- All route handlers use `user_id=1` instead of authenticated user
- Found in:
  - `routes/diagnosis.py:40`
  - `routes/flavor.py:36`
  - `routes/analysis.py:24`
  - `routes/recipes.py:39`
- **Impact**: All data is associated with a single user, breaking multi-user support
- **Recommendation**: Use authentication middleware to get current user ID

### 3. **Missing Database Indexes**
- No indexes on `user_id` columns in any table
- This will cause performance issues as data grows
- **Recommendation**: Add indexes on all `user_id` columns

### 4. **Syntax Errors in Multiple Route Files** 🔴 CRITICAL
- **Files affected**: `analysis.py`, `flavor.py`, `recipes.py`
- **Issue**: Invalid syntax using walrus operator `Depends(...:=get_db)`
- The walrus operator cannot be used in function parameter defaults
- `get_db` is not imported in these files
- **Current broken code**: 
  ```python
  def compile_analysis(req: Request, db: OrmSession = Depends(...:=get_db)):
  ```
- **Fix for all affected files**: 
  ```python
  from backend.db import get_db
  def compile_analysis(req: Request, db: OrmSession = Depends(get_db)):
  ```
- **Impact**: These routes cannot be imported, breaking the application

### 5. **No Database Migrations**
- No Alembic or migration system in place
- Schema changes require manual database updates
- **Recommendation**: Set up Alembic for version control

### 6. **Session Management**
- Sessions are created per request but not always properly closed
- Some routes use `db.commit()` without error handling
- **Recommendation**: Use context managers or ensure proper error handling

### 7. **Data Type Inconsistencies**
- V1 uses VARCHAR for JSON data instead of native JSON types
- Main app correctly uses JSON type
- **Recommendation**: Migrate V1 to use JSON columns

## Data Flow

1. **User Diagnosis Flow**:
   - User answers stored in Redis session
   - Evaluation snapshot created and saved to `evaluations` table
   - Locked flag prevents re-evaluation

2. **Flavor Flow**:
   - User flavor preferences stored in Redis session
   - Flavor template created and saved to `flavors` table
   - Locked flag prevents re-generation

3. **Analysis Flow**:
   - Combines evaluation and flavor data
   - LLM generates analysis
   - Saved to `analyses` table

4. **Recipe Generation Flow**:
   - Uses evaluation, flavor, and analysis data
   - LLM generates recipes
   - Request and result saved to `recipe_runs` table

## Recommendations

### Immediate Fixes

1. **Fix Import in analysis.py**:
   ```python
   from backend.db import get_db
   ```

2. **Add Foreign Keys**:
   ```python
   from sqlalchemy import ForeignKey
   user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), nullable=False, index=True)
   ```

3. **Implement Proper Authentication**:
   - Use `get_current_user` from `auth.py` in route handlers
   - Replace hardcoded `user_id=1` with `current_user.id`

### Short-term Improvements

1. **Add Database Indexes**:
   - Index on all `user_id` columns
   - Consider indexes on `created_at` for time-based queries

2. **Set up Alembic Migrations**:
   - Initialize Alembic
   - Create initial migration
   - Set up migration workflow

3. **Add Error Handling**:
   - Wrap database operations in try-except blocks
   - Implement proper rollback on errors
   - Add logging for database operations

### Long-term Improvements

1. **Database Relationships**:
   - Add proper ORM relationships (e.g., `user.evaluations`)
   - Enable cascade delete options

2. **Query Optimization**:
   - Add query methods to models
   - Implement pagination for large datasets
   - Add database query logging in development

3. **Data Archival**:
   - Implement soft deletes
   - Add archival strategy for old data
   - Consider partitioning for large tables

4. **Monitoring**:
   - Add database performance monitoring
   - Track slow queries
   - Monitor connection pool usage

## Database Initialization

### Current State
- `init_db.py` exists but imports from wrong path (`db.database` instead of `backend.db`)
- No automatic table creation on startup
- Tables must be created manually or through separate script

### Recommended Approach
1. Fix `init_db.py` import paths
2. Add table creation on application startup
3. Or use Alembic migrations for schema management

## Security Considerations

1. **SQL Injection**: Protected by SQLAlchemy ORM (parameterized queries)
2. **Password Storage**: Uses bcrypt hashing (good)
3. **Session Management**: Uses Redis for session storage (good)
4. **Data Access**: No row-level security; all users can potentially access all data if authentication is bypassed

## Summary

The database structure is functional but has several critical issues:
- ✅ Good: Proper use of JSON columns, connection pooling, session management
- ⚠️ Issues: Missing foreign keys, hardcoded user IDs, missing indexes, no migrations
- 🔴 Critical: Authentication not properly integrated, data integrity at risk

**Priority Actions**:
1. 🔴 **CRITICAL**: Fix syntax errors in `analysis.py`, `flavor.py`, `recipes.py` (add `get_db` imports)
2. Fix hardcoded user IDs (use authentication)
3. Add foreign key constraints
4. Add database indexes
5. Set up migration system


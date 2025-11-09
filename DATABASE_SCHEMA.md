# Database Schema Quick Reference

## Entity Relationship Diagram

```
┌─────────────┐
│    users    │
├─────────────┤
│ id (PK)     │
│ email       │◄───┐
│ password    │    │
└─────────────┘    │
                   │ (No FK constraint)
┌─────────────┐    │
│ evaluations │    │
├─────────────┤    │
│ id (PK)     │    │
│ user_id     │────┘ (should reference users.id)
│ snapshot    │
│ locked      │
│ created_at  │
└─────────────┘

┌─────────────┐    │
│   flavors   │    │
├─────────────┤    │
│ id (PK)     │    │
│ user_id     │────┘ (should reference users.id)
│ template    │
│ locked      │
│ created_at  │
└─────────────┘

┌─────────────┐    │
│  analyses   │    │
├─────────────┤    │
│ id (PK)     │    │
│ user_id     │────┘ (should reference users.id)
│ content     │
│ created_at  │
└─────────────┘

┌─────────────┐    │
│ recipe_runs │    │
├─────────────┤    │
│ id (PK)     │    │
│ user_id     │────┘ (should reference users.id)
│ request     │
│ result      │
│ created_at  │
└─────────────┘
```

## Table Details

### users
| Column | Type | Constraints | Index |
|--------|------|-------------|-------|
| id | INTEGER | PRIMARY KEY | ✅ |
| email | VARCHAR(255) | UNIQUE, NOT NULL | ✅ |
| password_hash | VARCHAR(255) | NOT NULL | ❌ |

### evaluations
| Column | Type | Constraints | Index | Notes |
|--------|------|-------------|-------|-------|
| id | INTEGER | PRIMARY KEY | ✅ | |
| user_id | INTEGER | NOT NULL | ❌ | **Missing FK to users.id** |
| snapshot | JSON | | ❌ | Stores evaluation data |
| locked | BOOLEAN | DEFAULT true | ❌ | |
| created_at | DATETIME | DEFAULT utcnow | ❌ | |

### flavors
| Column | Type | Constraints | Index | Notes |
|--------|------|-------------|-------|-------|
| id | INTEGER | PRIMARY KEY | ✅ | |
| user_id | INTEGER | NOT NULL | ❌ | **Missing FK to users.id** |
| template | JSON | | ❌ | Stores flavor preferences |
| locked | BOOLEAN | DEFAULT true | ❌ | |
| created_at | DATETIME | DEFAULT utcnow | ❌ | |

### analyses
| Column | Type | Constraints | Index | Notes |
|--------|------|-------------|-------|-------|
| id | INTEGER | PRIMARY KEY | ✅ | |
| user_id | INTEGER | NOT NULL | ❌ | **Missing FK to users.id** |
| content | JSON | | ❌ | Stores analysis results |
| created_at | DATETIME | DEFAULT utcnow | ❌ | |

### recipe_runs
| Column | Type | Constraints | Index | Notes |
|--------|------|-------------|-------|-------|
| id | INTEGER | PRIMARY KEY | ✅ | |
| user_id | INTEGER | NOT NULL | ❌ | **Missing FK to users.id** |
| request_payload | JSON | | ❌ | Request sent to LLM |
| result | JSON | | ❌ | Recipes returned |
| created_at | DATETIME | DEFAULT utcnow | ❌ | |

## Data Flow

```
User Session (Redis)
    │
    ├─► Answers ──────────┐
    │                      │
    │                      ▼
    │              ┌───────────────┐
    │              │  Evaluation   │
    │              │  (diagnosis)  │
    │              └───────────────┘
    │                      │
    │                      ▼
    │              ┌───────────────┐
    │              │  evaluations  │
    │              │     table     │
    │              └───────────────┘
    │
    ├─► Flavor Preferences ──┐
    │                         │
    │                         ▼
    │                 ┌───────────────┐
    │                 │    Flavor     │
    │                 │   (flavor)    │
    │                 └───────────────┘
    │                         │
    │                         ▼
    │                 ┌───────────────┐
    │                 │   flavors     │
    │                 │    table      │
    │                 └───────────────┘
    │
    └─► Combined ──► Analysis ──► analyses table
                            │
                            ▼
                    ┌───────────────┐
                    │ Recipe Gen    │
                    │  (recipes)    │
                    └───────────────┘
                            │
                            ▼
                    ┌───────────────┐
                    │ recipe_runs   │
                    │    table      │
                    └───────────────┘
```

## Code Locations

| Table | Created In | Model Location |
|-------|-----------|----------------|
| users | (via auth.py) | `backend/models.py:User` |
| evaluations | `routes/diagnosis.py:40` | `backend/models.py:Evaluation` |
| flavors | `routes/flavor.py:36` | `backend/models.py:Flavor` |
| analyses | `routes/analysis.py:24` | `backend/models.py:Analysis` |
| recipe_runs | `routes/recipes.py:39` | `backend/models.py:RecipeRun` |

## Current Issues Summary

| Issue | Severity | Files Affected |
|-------|----------|----------------|
| Syntax errors (missing imports) | 🔴 Critical | analysis.py, flavor.py, recipes.py |
| Hardcoded user_id=1 | 🔴 Critical | diagnosis.py, flavor.py, analysis.py, recipes.py |
| Missing foreign keys | 🟡 High | All models |
| Missing indexes on user_id | 🟡 High | All models |
| No migrations | 🟡 Medium | Entire project |
| No error handling | 🟡 Medium | All route files |

## Recommended Indexes

```sql
CREATE INDEX idx_evaluations_user_id ON evaluations(user_id);
CREATE INDEX idx_evaluations_created_at ON evaluations(created_at);

CREATE INDEX idx_flavors_user_id ON flavors(user_id);
CREATE INDEX idx_flavors_created_at ON flavors(created_at);

CREATE INDEX idx_analyses_user_id ON analyses(user_id);
CREATE INDEX idx_analyses_created_at ON analyses(created_at);

CREATE INDEX idx_recipe_runs_user_id ON recipe_runs(user_id);
CREATE INDEX idx_recipe_runs_created_at ON recipe_runs(created_at);
```

## Recommended Foreign Keys

```sql
ALTER TABLE evaluations 
  ADD CONSTRAINT fk_evaluations_user_id 
  FOREIGN KEY (user_id) REFERENCES users(id) 
  ON DELETE CASCADE;

ALTER TABLE flavors 
  ADD CONSTRAINT fk_flavors_user_id 
  FOREIGN KEY (user_id) REFERENCES users(id) 
  ON DELETE CASCADE;

ALTER TABLE analyses 
  ADD CONSTRAINT fk_analyses_user_id 
  FOREIGN KEY (user_id) REFERENCES users(id) 
  ON DELETE CASCADE;

ALTER TABLE recipe_runs 
  ADD CONSTRAINT fk_recipe_runs_user_id 
  FOREIGN KEY (user_id) REFERENCES users(id) 
  ON DELETE CASCADE;
```


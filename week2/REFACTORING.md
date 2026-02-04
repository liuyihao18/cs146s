# Week2 Backend Refactoring

## Overview

This refactoring improves the week2 backend with well-defined API contracts, robust error handling, database layer cleanup, and proper app configuration management.

## Key Improvements

### 1. **Schemas & API Contracts** (`schemas.py`)

- **Pydantic models** for all request/response types providing:
  - Type validation and documentation
  - Automatic OpenAPI schema generation
  - Request/response consistency

- **Key schemas:**
  - `ExtractRequest` / `ExtractResponse`: Action item extraction contract
  - `NoteCreate` / `Note`: Note management contracts
  - `ActionItemCreate` / `ActionItem` / `ActionItemUpdate`: Action item contracts
  - `ErrorResponse`: Standardized error format

### 2. **Configuration Management** (`config.py`)

- **Centralized settings** via `pydantic-settings`:
  - Database path
  - LLM model and host
  - App metadata (title, version)
  - Logging configuration
  - Environment variable support via `.env` file

- **Benefits:**
  - Single source of truth for configuration
  - Type-safe settings with defaults
  - Easy to override via environment variables

### 3. **Custom Exceptions** (`exceptions.py`)

- **Structured exception hierarchy:**
  - `AppException`: Base exception with error code
  - `ValidationError`: Request validation failures
  - `NotFoundError`: Resource not found
  - `DatabaseError`: Database operation failures
  - `LLMError`: LLM operation failures

- **Benefits:**
  - Consistent error reporting
  - Machine-readable error codes
  - Proper exception translation to HTTP responses

### 4. **Database Layer Cleanup** (`db.py`)

- **Context manager pattern** (`_get_connection()`):
  - Automatic connection cleanup
  - Proper transaction handling (commit/rollback)
  - Consistent error handling

- **Enhanced operations:**
  - Input validation (empty checks, ID validation)
  - Error handling with descriptive messages
  - New `get_action_item()` operation
  - Improved row validation in `mark_action_item_done()`

- **Key functions:**
  - `init_db()`: Initialize schema with error handling
  - `insert_note()`, `list_notes()`, `get_note()`: Note CRUD
  - `insert_action_items()`, `list_action_items()`, `get_action_item()`, `mark_action_item_done()`: Action items CRUD

### 5. **Service Layer Improvements** (`services/extract.py`)

- **Better error handling:**
  - Raises `ValidationError` for empty input (vs silently returning empty list)
  - Raises `LLMError` for LLM failures (vs silent fallback)
  - Caller decides fallback behavior

- **Comprehensive docstrings:**
  - Clear parameter and return documentation
  - Exception documentation
  - Usage guidance

- **Configuration integration:**
  - Uses centralized settings for model and host
  - No hardcoded paths or models

### 6. **Main Application** (`main.py`)

- **Structured exception handlers:**
  - `ValidationError` → 400 Bad Request
  - `NotFoundError` → 404 Not Found
  - `DatabaseError` → 500 Internal Server Error
  - `AppException` → 500 Internal Server Error with logging

- **Logging:**
  - Configured logging with configurable level
  - Error logging for debugging
  - Warning messages for missing resources

- **Lifecycle management:**
  - Graceful database initialization
  - Error handling during app startup
  - Health check endpoint (`/health`)

- **Static files:**
  - Conditional mounting (checks if directory exists)
  - Proper warnings for missing frontend

### 7. **Router Improvements**

#### `routers/notes.py`

- **Strong typing** with Pydantic schemas
- **Proper validation:**
  - Empty content checks with `ValidationError`
  - ID validation
  - 404 responses for missing notes
- **All CRUD operations:**
  - `POST /notes`: Create note
  - `GET /notes/{id}`: Get single note
  - `GET /notes`: List all notes

#### `routers/action_items.py`

- **Extraction endpoint improvements:**
  - Uses new `ExtractRequest`/`ExtractResponse` schemas
  - Configurable LLM vs heuristic extraction
  - LLM fallback to heuristic on failure
  - Clear error handling

- **Enhanced action item operations:**
  - `POST /action-items/extract`: Extract with saving
  - `GET /action-items`: List all or by note
  - `POST /action-items/{id}/done`: Mark done with validation
  - Proper 404 handling

### 8. **Testing** (`tests/test_extract.py`)

- **Comprehensive test coverage:**
  - Heuristic extraction (bullets, checkboxes)
  - LLM extraction with keyword prefixes
  - Empty input validation
  - Invalid JSON error handling
  - Exception propagation (not silent failures)

- **Uses mocking:**
  - Mocks Ollama client for predictable testing
  - No external dependencies
  - Fast test execution

## Migration Guide

### For Existing Code

If you have existing code using the old patterns, update as follows:

**Old:**

```python
from . import db
db.init_db()
items = extract_action_items_llm(text)  # Silently falls back on error
```

**New:**

```python
from .config import settings
from .exceptions import LLMError
from .services.extract import extract_action_items_llm

try:
    items = extract_action_items_llm(text)
except LLMError:
    # Handle LLM failure explicitly
    items = extract_action_items(text)
```

### Using the New Configuration

```python
from week2.app.config import settings

# Access settings
model = settings.ollama_model
db_path = settings.db_path
log_level = settings.log_level

# Override via environment
# APP_OLLAMA_MODEL=llama3.2 poetry run uvicorn ...
```

### Using Schemas in Routers

```python
from fastapi import APIRouter
from ..schemas import ExtractRequest, ExtractResponse

router = APIRouter()

@router.post("/extract", response_model=ExtractResponse)
def extract(payload: ExtractRequest) -> dict:
    # Payload is automatically validated
    # Response is automatically serialized
    pass
```

## Dependency Changes

Added to `pyproject.toml`:

- `pydantic-settings>=2.0.0`: Configuration management

## Breaking Changes

- `extract_action_items_llm()` now raises exceptions instead of silently falling back
- Routes return structured responses with `created_at` timestamps
- Database operations validate inputs and raise `DatabaseError` on failures

## Benefits Summary

| Aspect | Before | After |
|--------|--------|-------|
| **Type Safety** | Loose `Dict[str, Any]` | Strong Pydantic schemas |
| **API Documentation** | Manual effort | Auto-generated from schemas |
| **Error Handling** | Loose HTTPExceptions | Structured custom exceptions |
| **Database Safety** | Manual commit/rollback | Context manager pattern |
| **Configuration** | Hardcoded/env vars | Centralized settings |
| **Testability** | Harder to mock | Easy with structured services |
| **Maintainability** | Scattered logic | Clear separation of concerns |

## Files Modified/Created

### Created

- `app/schemas.py`: Pydantic models
- `app/config.py`: Settings management
- `app/exceptions.py`: Custom exceptions

### Modified

- `app/main.py`: Exception handlers, logging, lifecycle
- `app/db.py`: Context managers, error handling, validation
- `app/routers/notes.py`: Schema usage, improved validation
- `app/routers/action_items.py`: Schema usage, better extraction logic
- `app/services/extract.py`: Error handling, docstrings
- `tests/test_extract.py`: Updated tests for new behavior
- `pyproject.toml`: Added pydantic-settings dependency

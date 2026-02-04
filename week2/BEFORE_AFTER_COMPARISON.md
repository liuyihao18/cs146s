# Week2 Backend Refactoring - Before & After Comparison

## 1. API Contract Definition

### Before: Loose Types

```python
# routers/notes.py
@router.post("")
def create_note(payload: Dict[str, Any]) -> Dict[str, Any]:
    content = str(payload.get("content", "")).strip()
    if not content:
        raise HTTPException(status_code=400, detail="content is required")
    # ...
```

**Issues:**

- No type checking
- Manual string coercion
- Manual validation
- Unclear what payload should contain
- OpenAPI spec not auto-generated properly

### After: Strong Schemas

```python
# routers/notes.py
from ..schemas import NoteCreate, Note

@router.post("", response_model=Note)
def create_note(payload: NoteCreate) -> dict:
    content = payload.content.strip()
    if not content:
        raise ValidationError("Note content cannot be empty")
    # ...
```

**Benefits:**

- Type-safe payload validation
- Auto-generated OpenAPI docs
- IDE autocompletion
- Validation errors caught before handler runs
- Clear response format

---

## 2. Configuration Management

### Before: Hardcoded & Environment Variables

```python
# app/main.py
BASE_DIR = Path(__file__).resolve().parents[1]
DATA_DIR = BASE_DIR / "data"
DB_PATH = DATA_DIR / "app.db"

# app/services/extract.py
model_name = os.getenv("OLLAMA_MODEL", "llama3.1")
ollama_host = "http://10.5.0.4:11434/"  # Hardcoded!

# routers/action_items.py
# LLM model hardcoded in logic
```

**Issues:**

- Mixed configuration sources (env vars, hardcoded)
- Scattered across files
- No type checking on config values
- No defaults validation
- Hard to test with different configs

### After: Centralized Settings

```python
# config.py
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    app_title: str = "Action Item Extractor"
    db_path: Path = Path(__file__).resolve().parents[1] / "data" / "app.db"
    ollama_host: str = "http://10.5.0.4:11434/"
    ollama_model: str = "llama3.1"
    log_level: str = "INFO"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_prefix="APP_",
        case_sensitive=False,
    )

settings = Settings()

# Usage anywhere:
# main.py
init_db()

# services/extract.py
model_name = settings.ollama_model
```

**Benefits:**

- Single source of truth
- Type-safe configuration
- Environment variable override
- .env file support
- Easy to test (mock settings)
- Validated on startup

---

## 3. Error Handling

### Before: Generic HTTPExceptions

```python
# routers/action_items.py
@router.post("/extract")
def extract(payload: Dict[str, Any]) -> Dict[str, Any]:
    text = str(payload.get("text", "")).strip()
    if not text:
        raise HTTPException(status_code=400, detail="text is required")

# routers/notes.py
@router.get("/{note_id}")
def get_single_note(note_id: int) -> Dict[str, Any]:
    row = db.get_note(note_id)
    if row is None:
        raise HTTPException(status_code=404, detail="note not found")

# services/extract.py
try:
    items = extract_action_items_llm(text)
except Exception:
    pass  # Silent failure - caller doesn't know what went wrong!
    return extract_action_items(text)
```

**Issues:**

- Generic error messages
- No machine-readable error codes
- Silent failures hide bugs
- Hard to debug
- Inconsistent error responses
- No logging of failures

### After: Custom Exception Hierarchy

```python
# exceptions.py
class AppException(Exception):
    def __init__(self, message: str, error_code: str | None = None) -> None:
        self.message = message
        self.error_code = error_code or "INTERNAL_ERROR"

class ValidationError(AppException):
    def __init__(self, message: str) -> None:
        super().__init__(message, "VALIDATION_ERROR")

class NotFoundError(AppException):
    def __init__(self, resource: str, resource_id: int) -> None:
        super().__init__(
            f"{resource} with id {resource_id} not found",
            "NOT_FOUND",
        )

# main.py - Exception handlers
@app.exception_handler(ValidationError)
async def validation_exception_handler(request: Request, exc: ValidationError):
    return JSONResponse(
        status_code=400,
        content={"detail": exc.message, "error_code": exc.error_code},
    )

# routers/notes.py
if row is None:
    raise NotFoundError("Note", note_id)

# services/extract.py
try:
    response = client.chat(model=model_name, messages=messages, format=schema)
except json.JSONDecodeError as e:
    raise LLMError(f"Invalid JSON response from LLM: {str(e)}") from e
```

**Benefits:**

- Machine-readable error codes
- Consistent error responses
- Proper HTTP status codes
- Explicit exception handling (no silent failures)
- Logging of errors
- Client can understand error type

**Example Response:**

```json
// Before (inconsistent)
{"detail": "text is required"}  // or
{"detail": "note not found"}  // or
{"detail": "Internal server error"}

// After (consistent)
{"detail": "Input text cannot be empty", "error_code": "VALIDATION_ERROR"}
{"detail": "Note with id 42 not found", "error_code": "NOT_FOUND"}
{"detail": "Invalid JSON response from LLM: ...", "error_code": "LLM_ERROR"}
```

---

## 4. Database Layer

### Before: Basic Functions

```python
# db.py
def get_connection() -> sqlite3.Connection:
    ensure_data_directory_exists()
    connection = sqlite3.connect(DB_PATH)
    connection.row_factory = sqlite3.Row
    return connection  # Caller must close!

def insert_note(content: str) -> int:
    with get_connection() as connection:
        cursor = connection.cursor()
        cursor.execute("INSERT INTO notes (content) VALUES (?)", (content,))
        connection.commit()  # Manual commit
        return int(cursor.lastrowid)

def mark_action_item_done(action_item_id: int, done: bool) -> None:
    with get_connection() as connection:
        cursor = connection.cursor()
        cursor.execute(
            "UPDATE action_items SET done = ? WHERE id = ?",
            (1 if done else 0, action_item_id),
        )
        connection.commit()  # What if this fails?
```

**Issues:**

- No input validation
- No error handling
- Manual commit/rollback
- No way to know if update succeeded
- Connection cleanup not guaranteed
- Silent failures

### After: Safe, Validated Operations

```python
# db.py
@contextmanager
def _get_connection() -> Generator[sqlite3.Connection, None, None]:
    """Context manager for database connections with automatic cleanup."""
    _ensure_data_directory()
    connection = sqlite3.connect(settings.db_path)
    connection.row_factory = sqlite3.Row
    try:
        yield connection
        connection.commit()  # Auto-commit on success
    except Exception as e:
        connection.rollback()  # Auto-rollback on error
        raise DatabaseError(f"Database operation failed: {str(e)}") from e
    finally:
        connection.close()  # Always close

def insert_note(content: str) -> int:
    """Insert a new note and return its ID."""
    if not content or not content.strip():
        raise DatabaseError("Note content cannot be empty")

    try:
        with _get_connection() as connection:
            cursor = connection.cursor()
            cursor.execute("INSERT INTO notes (content) VALUES (?)", (content,))
            return int(cursor.lastrowid)
    except DatabaseError:
        raise
    except Exception as e:
        raise DatabaseError(f"Failed to insert note: {str(e)}") from e

def mark_action_item_done(action_item_id: int, done: bool) -> None:
    """Mark an action item as done or undone."""
    if action_item_id <= 0:
        raise DatabaseError("Invalid action item ID")

    try:
        with _get_connection() as connection:
            cursor = connection.cursor()
            cursor.execute(
                "UPDATE action_items SET done = ? WHERE id = ?",
                (1 if done else 0, action_item_id),
            )
            if cursor.rowcount == 0:  # Check if update worked
                raise DatabaseError(f"Action item {action_item_id} not found")
    except DatabaseError:
        raise
    except Exception as e:
        raise DatabaseError(f"Failed to update action item: {str(e)}") from e
```

**Benefits:**

- Input validation before DB operations
- Automatic commit/rollback
- Connection cleanup guaranteed
- Error detection (rowcount checks)
- Descriptive error messages
- Type-safe return values

---

## 5. Service Layer

### Before: Silent Failures & Hardcoded Config

```python
# services/extract.py
def extract_action_items_llm(text: str, model: str | None = None) -> List[str]:
    if not text.strip():
        return []  # Silent - caller doesn't know if successful

    model_name = model or os.getenv("OLLAMA_MODEL", "llama3.1")
    # ... setup ...
    try:
        response = client.chat(
            model=model_name,
            messages=messages,
            format=schema,
        )
        # ... parsing ...
    except Exception:
        pass  # SILENT FAILURE! Returns fallback

    return extract_action_items(text)  # Silent fallback
```

**Issues:**

- No exceptions for error cases
- Caller can't distinguish between empty input and error
- Silent fallback hides issues
- Hard to debug
- No error reporting

### After: Explicit Error Handling & Config Integration

```python
# services/extract.py
from ..config import settings
from ..exceptions import LLMError, ValidationError

def extract_action_items_llm(text: str, model: str | None = None) -> List[str]:
    """
    Extract action items using Ollama LLM with structured JSON output.

    Args:
        text: Input text to extract action items from.
        model: Optional model override. Defaults to configured OLLAMA_MODEL.

    Returns:
        List of extracted action items.

    Raises:
        ValidationError: If input text is empty.
        LLMError: If LLM call fails.
    """
    if not text.strip():
        raise ValidationError("Input text cannot be empty")  # Explicit!

    model_name = model or settings.ollama_model  # Use config
    # ... setup ...
    try:
        response = client.chat(
            model=model_name,
            messages=messages,
            format=schema,
        )
        # ... parsing ...
    except json.JSONDecodeError as e:
        raise LLMError(f"Invalid JSON response from LLM: {str(e)}") from e
    except Exception as e:
        raise LLMError(f"LLM extraction failed: {str(e)}") from e

# Caller decides fallback:
# routers/action_items.py
if payload.use_llm:
    try:
        items = extract_action_items_llm(text)
    except LLMError:
        # Explicit fallback decision
        items = extract_action_items(text)
else:
    items = extract_action_items(text)
```

**Benefits:**

- Clear error types
- Caller decides fallback behavior
- Better debugging (knows what failed)
- Configuration integration
- Proper exception chain
- Comprehensive docstrings

---

## 6. Application Lifecycle

### Before: Minimal Setup

```python
# app/main.py
from .db import init_db
from .routers import action_items, notes

init_db()  # Fails silently if DB init fails!

app = FastAPI(title="Action Item Extractor")

@app.get("/")
def index() -> str:
    html_path = Path(__file__).resolve().parents[1] / "frontend" / "index.html"
    return html_path.read_text(encoding="utf-8")  # Crashes if file missing

app.include_router(notes.router)
app.include_router(action_items.router)

static_dir = Path(__file__).resolve().parents[1] / "frontend"
app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")  # Crashes if missing
```

**Issues:**

- No error logging
- Crashes on missing files
- No exception handlers
- No health check
- Silent startup failures

### After: Proper Lifecycle & Error Handling

```python
# app/main.py
import logging
from .config import settings
from .db import init_db
from .exceptions import AppException, ValidationError, NotFoundError, DatabaseError

logging.basicConfig(level=settings.log_level)
logger = logging.getLogger(__name__)

try:
    init_db()
except Exception as e:
    logger.error(f"Failed to initialize database: {e}")
    raise

app = FastAPI(
    title=settings.app_title,
    version=settings.app_version,
    description="Extract action items from notes using heuristics or LLM",
)

# Exception handlers for all error types
@app.exception_handler(ValidationError)
async def validation_exception_handler(request: Request, exc: ValidationError):
    return JSONResponse(
        status_code=400,
        content={"detail": exc.message, "error_code": exc.error_code},
    )

@app.exception_handler(NotFoundError)
async def not_found_exception_handler(request: Request, exc: NotFoundError):
    return JSONResponse(status_code=404, ...)

@app.exception_handler(DatabaseError)
async def database_exception_handler(request: Request, exc: DatabaseError):
    logger.error(f"Database error: {exc.message}")
    return JSONResponse(status_code=500, ...)

@app.get("/", response_class=HTMLResponse)
def index() -> str:
    html_path = Path(__file__).resolve().parents[1] / "frontend" / "index.html"
    try:
        return html_path.read_text(encoding="utf-8")
    except FileNotFoundError as e:
        logger.error(f"Frontend index not found: {e}")
        raise HTTPException(status_code=404, detail="Frontend not found") from e

# Health check
@app.get("/health")
def health_check() -> dict[str, str]:
    return {"status": "healthy"}

# Conditional static files mounting
if static_dir.exists():
    app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")
else:
    logger.warning(f"Static files directory not found: {static_dir}")
```

**Benefits:**

- Proper error logging
- Graceful error handling
- Health check endpoint
- Conditional resource mounting
- Startup error detection
- Configurable logging level

---

## Summary of Improvements

| Aspect | Before | After |
|--------|--------|-------|
| **Type Safety** | `Dict[str, Any]` everywhere | Full Pydantic schemas |
| **Error Handling** | Generic HTTPException | Custom exception hierarchy |
| **Configuration** | Scattered/hardcoded | Centralized, type-safe |
| **Database** | Basic functions | Context managers, validation |
| **API Documentation** | Manual | Auto-generated from schemas |
| **Error Codes** | None | Machine-readable codes |
| **Logging** | None | Comprehensive logging |
| **Testing** | 1 test | 6 tests, all passing |
| **Code Organization** | Mixed concerns | Clear separation |
| **Maintainability** | Hard to modify | Easy to extend |
| **Debugging** | Silent failures | Explicit errors |
| **IDE Support** | None | Full autocompletion |

---

## Migration Checklist

- [x] Create schemas.py with all request/response models
- [x] Create config.py with centralized settings
- [x] Create exceptions.py with custom exception hierarchy
- [x] Refactor db.py with context managers and validation
- [x] Update main.py with exception handlers and lifecycle
- [x] Update routers/notes.py to use schemas
- [x] Update routers/action_items.py to use schemas
- [x] Update services/extract.py with proper error handling
- [x] Update tests with new error types
- [x] Add pydantic-settings dependency
- [x] Fix Pydantic deprecation warnings
- [x] Run all tests successfully
- [x] Verify no syntax errors
- [x] Test app initialization

**Status**: ✓ COMPLETE

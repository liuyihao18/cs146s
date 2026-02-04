# Action Item Extractor

A FastAPI application that extracts actionable items from free-form notes using either rule-based heuristics or LLM-powered extraction with Ollama.

## Overview

This application helps convert unstructured meeting notes, task lists, and free-form text into structured, actionable items. It supports two extraction methods:

- **Heuristic Extraction**: Fast, rule-based pattern matching for bullet points, checkboxes, and keyword prefixes
- **LLM Extraction**: AI-powered extraction using Ollama for intelligent, context-aware action item identification

All extracted items can be saved to a SQLite database, linked to the original notes, and managed through a simple web interface.

## Features

- ✅ **Dual Extraction Methods**: Choose between heuristic or LLM-based extraction
- ✅ **Note Management**: Save and retrieve original notes
- ✅ **Action Item Tracking**: Mark items as done/undone
- ✅ **Type-Safe API**: Pydantic schemas for request/response validation
- ✅ **Error Handling**: Comprehensive exception hierarchy with error codes
- ✅ **Web Interface**: Clean, minimal HTML frontend
- ✅ **Database Persistence**: SQLite with automatic schema initialization
- ✅ **Configuration Management**: Environment-based settings

## Architecture

```
week2/
├── app/
│   ├── main.py              # FastAPI app with exception handlers
│   ├── config.py            # Centralized configuration
│   ├── schemas.py           # Pydantic models for validation
│   ├── exceptions.py        # Custom exception hierarchy
│   ├── db.py                # Database layer with context managers
│   ├── client.py            # Ollama client configuration
│   ├── routers/
│   │   ├── notes.py         # Note CRUD endpoints
│   │   └── action_items.py  # Extraction and item management
│   └── services/
│       └── extract.py       # Extraction logic (heuristic & LLM)
├── frontend/
│   └── index.html           # Web interface
├── tests/
│   └── test_extract.py      # Unit tests for extraction
└── data/
    └── app.db               # SQLite database (auto-created)
```

## Prerequisites

- Python 3.10 or higher
- Poetry (for dependency management)
- Ollama (optional, for LLM extraction)

## Setup

### 1. Install Dependencies

```bash
# Activate your conda environment (if using conda)
conda activate cs146s

# Install dependencies with Poetry
poetry install
```

### 2. Configure Ollama (Optional)

If you want to use LLM-powered extraction:

```bash
# Install Ollama: https://ollama.com/download

# Pull the default model
ollama pull llama3.1

# Start Ollama server (usually runs automatically)
ollama serve
```

### 3. Configure Environment (Optional)

Create a `.env` file in the `week2` directory to override default settings:

```env
# LLM Configuration
APP_OLLAMA_HOST=http://localhost:11434/
APP_OLLAMA_MODEL=llama3.1

# Database
APP_DB_PATH=./data/app.db

# Logging
APP_LOG_LEVEL=INFO
```

## Running the Application

### Start the Server

```bash
# From the project root directory
poetry run uvicorn week2.app.main:app --reload
```

The application will be available at:

- **Web Interface**: <http://localhost:8000>
- **API Documentation**: <http://localhost:8000/docs>
- **Alternative Docs**: <http://localhost:8000/redoc>

### Using the Web Interface

1. Open <http://localhost:8000> in your browser
2. Paste your notes into the textarea
3. Choose an extraction method:
   - **Extract (Heuristic)**: Fast, rule-based extraction
   - **Extract (LLM)**: AI-powered extraction (requires Ollama)
4. Check "Save as note" to store the original text
5. View extracted items with checkboxes to mark them done
6. Click **List Notes** to view all saved notes

## API Endpoints

### Action Items

#### Extract Action Items

```http
POST /action-items/extract
Content-Type: application/json

{
  "text": "- [ ] Set up database\n- Implement API\n- Write tests",
  "save_note": true,
  "use_llm": false
}
```

**Response:**

```json
{
  "note_id": 1,
  "items": [
    {
      "id": 1,
      "text": "Set up database",
      "note_id": 1,
      "done": false,
      "created_at": "2026-02-04T10:30:00"
    }
  ]
}
```

#### List Action Items

```http
GET /action-items
GET /action-items?note_id=1
```

#### Mark Item as Done

```http
POST /action-items/{item_id}/done
Content-Type: application/json

{
  "done": true
}
```

### Notes

#### Create Note

```http
POST /notes
Content-Type: application/json

{
  "content": "Meeting notes from today..."
}
```

#### Get Single Note

```http
GET /notes/{note_id}
```

#### List All Notes

```http
GET /notes
```

### Health Check

```http
GET /health
```

**Response:**

```json
{
  "status": "healthy"
}
```

## Extraction Methods

### Heuristic Extraction

The heuristic method uses pattern matching to identify action items:

- **Bullet points**: Lines starting with `-`, `*`, `•`, or numbered lists
- **Checkboxes**: Lines containing `[ ]` or `[todo]`
- **Keywords**: Lines starting with `todo:`, `action:`, or `next:`
- **Imperative verbs**: Sentences starting with action verbs (add, create, implement, etc.)

**Example:**

```
Input:
- [ ] Set up database
* Implement API
1. Write tests
TODO: Deploy to production

Output:
["Set up database", "Implement API", "Write tests", "Deploy to production"]
```

### LLM Extraction

The LLM method uses Ollama to understand context and extract tasks intelligently:

- Understands natural language descriptions
- Identifies implicit action items
- Handles complex sentence structures
- Provides context-aware extraction

**Example:**

```
Input:
We need to set up the database before implementing the API.
Also, remember to write comprehensive tests.

Output:
["Set up the database", "Implement the API", "Write comprehensive tests"]
```

## Testing

### Run All Tests

```bash
poetry run pytest week2/tests/ -v
```

### Run Specific Tests

```bash
# Test extraction logic
poetry run pytest week2/tests/test_extract.py -v

# Run with coverage
poetry run pytest week2/tests/ --cov=week2.app
```

### Integration Testing

```bash
# Start the server first
poetry run uvicorn week2.app.main:app --reload

# In another terminal, run integration tests
poetry run python week2/test_integration.py
```

### Expected Test Output

```
========================================== test session starts ==========================================
collected 6 items

week2/tests/test_extract.py::test_extract_bullets_and_checkboxes PASSED              [ 16%]
week2/tests/test_extract.py::test_extract_action_items_llm_bullets PASSED            [ 33%]
week2/tests/test_extract.py::test_extract_action_items_llm_keywords PASSED           [ 50%]
week2/tests/test_extract.py::test_extract_action_items_llm_empty_input PASSED        [ 66%]
week2/tests/test_extract.py::test_extract_action_items_llm_invalid_json PASSED       [ 83%]
week2/tests/test_extract.py::test_extract_action_items_llm_fallback_to_heuristic PASSED [100%]

=========================================== 6 passed in 2.60s ===========================================
```

## Error Handling

The API returns structured error responses with machine-readable codes:

| HTTP Code | Error Code | Description |
|-----------|------------|-------------|
| 400 | `VALIDATION_ERROR` | Invalid input (empty text, invalid IDs) |
| 404 | `NOT_FOUND` | Resource doesn't exist |
| 500 | `DATABASE_ERROR` | Database operation failed |
| 500 | `LLM_ERROR` | LLM extraction failed |

**Example Error Response:**

```json
{
  "detail": "Input text cannot be empty",
  "error_code": "VALIDATION_ERROR"
}
```

## Configuration

All settings can be configured via environment variables with the `APP_` prefix:

| Variable | Default | Description |
|----------|---------|-------------|
| `APP_OLLAMA_HOST` | `http://10.5.0.4:11434/` | Ollama server URL |
| `APP_OLLAMA_MODEL` | `llama3.1` | LLM model to use |
| `APP_DB_PATH` | `./data/app.db` | SQLite database path |
| `APP_LOG_LEVEL` | `INFO` | Logging level |

## Database Schema

### Notes Table

```sql
CREATE TABLE notes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    content TEXT NOT NULL,
    created_at TEXT DEFAULT (datetime('now'))
);
```

### Action Items Table

```sql
CREATE TABLE action_items (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    note_id INTEGER,
    text TEXT NOT NULL,
    done INTEGER DEFAULT 0,
    created_at TEXT DEFAULT (datetime('now')),
    FOREIGN KEY (note_id) REFERENCES notes(id)
);
```

## Development

### Code Quality

```bash
# Format code
poetry run black week2/

# Lint code
poetry run ruff check week2/

# Type checking (requires mypy)
pip install mypy
mypy week2/app
```

### Project Structure Principles

- **Separation of Concerns**: Clear boundaries between API, services, and data layers
- **Type Safety**: Pydantic schemas for all API contracts
- **Error Handling**: Custom exceptions with proper HTTP status codes
- **Testability**: Dependency injection and mocked external services
- **Configuration**: Centralized settings with environment override

## Troubleshooting

### LLM Extraction Fails

**Problem**: LLM extraction returns errors or falls back to heuristics

**Solutions**:

1. Verify Ollama is running: `ollama list`
2. Check the configured host: `echo $APP_OLLAMA_HOST`
3. Pull the model: `ollama pull llama3.1`
4. Check logs for detailed error messages

### Database Errors

**Problem**: Database operation fails

**Solutions**:

1. Ensure `data/` directory has write permissions
2. Delete `data/app.db` to reset the database
3. Check disk space availability

### Import Errors

**Problem**: Module not found errors

**Solutions**:

1. Ensure you're in the correct conda environment
2. Run `poetry install` to install dependencies
3. Check Python version: `python --version` (should be 3.10+)

## Documentation

Additional documentation is available in the following files:

- **[REFACTORING.md](REFACTORING.md)**: Detailed refactoring documentation
- **[REFACTORING_SUMMARY.md](REFACTORING_SUMMARY.md)**: Quick reference guide
- **[BEFORE_AFTER_COMPARISON.md](BEFORE_AFTER_COMPARISON.md)**: Code comparison examples
- **[FRONTEND_INTEGRATION.md](FRONTEND_INTEGRATION.md)**: Frontend features and API usage
- **[VERIFICATION_CHECKLIST.md](VERIFICATION_CHECKLIST.md)**: Complete verification checklist
- **[INDEX.md](INDEX.md)**: Comprehensive project index

## License

This project is part of the CS146S Modern Software Development course assignments.

## Contributing

This is a course assignment project. Please follow the course guidelines for contributions and submissions.

## Support

For issues or questions:

1. Check the documentation files listed above
2. Review the API documentation at `/docs`
3. Consult the course staff or TA

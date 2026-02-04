from __future__ import annotations

import logging
from pathlib import Path

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles

from .config import settings
from .db import init_db
from .exceptions import AppException, DatabaseError, NotFoundError, ValidationError
from .routers import action_items, notes

# Configure logging
logging.basicConfig(level=settings.log_level)
logger = logging.getLogger(__name__)

# Initialize database
try:
    init_db()
except Exception as e:
    logger.error(f"Failed to initialize database: {e}")
    raise

# Create FastAPI app
app = FastAPI(
    title=settings.app_title,
    version=settings.app_version,
    description="Extract action items from notes using heuristics or LLM",
)


# Exception handlers
@app.exception_handler(ValidationError)
async def validation_exception_handler(request: Request, exc: ValidationError):
    """Handle validation errors."""
    return JSONResponse(
        status_code=400,
        content={"detail": exc.message, "error_code": exc.error_code},
    )


@app.exception_handler(NotFoundError)
async def not_found_exception_handler(request: Request, exc: NotFoundError):
    """Handle not found errors."""
    return JSONResponse(
        status_code=404,
        content={"detail": exc.message, "error_code": exc.error_code},
    )


@app.exception_handler(DatabaseError)
async def database_exception_handler(request: Request, exc: DatabaseError):
    """Handle database errors."""
    logger.error(f"Database error: {exc.message}")
    return JSONResponse(
        status_code=500,
        content={"detail": "Database operation failed", "error_code": exc.error_code},
    )


@app.exception_handler(AppException)
async def app_exception_handler(request: Request, exc: AppException):
    """Handle application errors."""
    logger.error(f"Application error: {exc.message}")
    return JSONResponse(
        status_code=500,
        content={"detail": exc.message, "error_code": exc.error_code},
    )


# Routes
@app.get("/", response_class=HTMLResponse)
def index() -> str:
    """Serve the main HTML page."""
    html_path = Path(__file__).resolve().parents[1] / "frontend" / "index.html"
    try:
        return html_path.read_text(encoding="utf-8")
    except FileNotFoundError as e:
        logger.error(f"Frontend index not found: {e}")
        raise HTTPException(status_code=404, detail="Frontend not found") from e


# Include routers
app.include_router(notes.router)
app.include_router(action_items.router)

# Static files
static_dir = Path(__file__).resolve().parents[1] / "frontend"
if static_dir.exists():
    app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")
else:
    logger.warning(f"Static files directory not found: {static_dir}")


@app.get("/health")
def health_check() -> dict[str, str]:
    """Health check endpoint."""
    return {"status": "healthy"}

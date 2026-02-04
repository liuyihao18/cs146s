from __future__ import annotations

import sqlite3
from contextlib import contextmanager
from typing import Generator, Optional

from .config import settings
from .exceptions import DatabaseError


def _ensure_data_directory() -> None:
    """Ensure the data directory exists."""
    settings.db_path.parent.mkdir(parents=True, exist_ok=True)


@contextmanager
def _get_connection() -> Generator[sqlite3.Connection, None, None]:
    """Context manager for database connections with automatic cleanup."""
    _ensure_data_directory()
    connection = sqlite3.connect(settings.db_path)
    connection.row_factory = sqlite3.Row
    try:
        yield connection
        connection.commit()
    except Exception as e:
        connection.rollback()
        raise DatabaseError(f"Database operation failed: {str(e)}") from e
    finally:
        connection.close()


def init_db() -> None:
    """Initialize the database schema."""
    _ensure_data_directory()
    try:
        with _get_connection() as connection:
            cursor = connection.cursor()
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS notes (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    content TEXT NOT NULL,
                    created_at TEXT DEFAULT (datetime('now'))
                );
                """
            )
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS action_items (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    note_id INTEGER,
                    text TEXT NOT NULL,
                    done INTEGER DEFAULT 0,
                    created_at TEXT DEFAULT (datetime('now')),
                    FOREIGN KEY (note_id) REFERENCES notes(id)
                );
                """
            )
    except Exception as e:
        raise DatabaseError(f"Failed to initialize database: {str(e)}") from e


# Note operations


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


def list_notes() -> list[sqlite3.Row]:
    """List all notes ordered by creation date (newest first)."""
    try:
        with _get_connection() as connection:
            cursor = connection.cursor()
            cursor.execute(
                "SELECT id, content, created_at FROM notes ORDER BY id DESC"
            )
            return list(cursor.fetchall())
    except Exception as e:
        raise DatabaseError(f"Failed to list notes: {str(e)}") from e


def get_note(note_id: int) -> Optional[sqlite3.Row]:
    """Get a single note by ID."""
    if note_id <= 0:
        raise DatabaseError("Invalid note ID")

    try:
        with _get_connection() as connection:
            cursor = connection.cursor()
            cursor.execute(
                "SELECT id, content, created_at FROM notes WHERE id = ?",
                (note_id,),
            )
            return cursor.fetchone()
    except Exception as e:
        raise DatabaseError(f"Failed to retrieve note: {str(e)}") from e


# Action items operations


def insert_action_items(items: list[str], note_id: Optional[int] = None) -> list[int]:
    """Insert multiple action items and return their IDs."""
    if not items:
        return []

    try:
        with _get_connection() as connection:
            cursor = connection.cursor()
            ids: list[int] = []
            for item in items:
                if item and item.strip():
                    cursor.execute(
                        "INSERT INTO action_items (note_id, text) VALUES (?, ?)",
                        (note_id, item.strip()),
                    )
                    ids.append(int(cursor.lastrowid))
            return ids
    except Exception as e:
        raise DatabaseError(f"Failed to insert action items: {str(e)}") from e


def list_action_items(note_id: Optional[int] = None) -> list[sqlite3.Row]:
    """List action items, optionally filtered by note_id."""
    try:
        with _get_connection() as connection:
            cursor = connection.cursor()
            if note_id is None:
                cursor.execute(
                    "SELECT id, note_id, text, done, created_at FROM action_items ORDER BY id DESC"
                )
            else:
                if note_id <= 0:
                    raise DatabaseError("Invalid note ID")
                cursor.execute(
                    "SELECT id, note_id, text, done, created_at FROM action_items WHERE note_id = ? ORDER BY id DESC",
                    (note_id,),
                )
            return list(cursor.fetchall())
    except DatabaseError:
        raise
    except Exception as e:
        raise DatabaseError(f"Failed to list action items: {str(e)}") from e


def get_action_item(action_item_id: int) -> Optional[sqlite3.Row]:
    """Get a single action item by ID."""
    if action_item_id <= 0:
        raise DatabaseError("Invalid action item ID")

    try:
        with _get_connection() as connection:
            cursor = connection.cursor()
            cursor.execute(
                "SELECT id, note_id, text, done, created_at FROM action_items WHERE id = ?",
                (action_item_id,),
            )
            return cursor.fetchone()
    except Exception as e:
        raise DatabaseError(f"Failed to retrieve action item: {str(e)}") from e


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
            if cursor.rowcount == 0:
                raise DatabaseError(f"Action item {action_item_id} not found")
    except DatabaseError:
        raise
    except Exception as e:
        raise DatabaseError(f"Failed to update action item: {str(e)}") from e

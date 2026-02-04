from __future__ import annotations

from fastapi import APIRouter

from .. import db
from ..exceptions import NotFoundError, ValidationError
from ..schemas import Note, NoteCreate


router = APIRouter(prefix="/notes", tags=["notes"])


@router.post("", response_model=Note)
def create_note(payload: NoteCreate) -> dict:
    """Create a new note."""
    content = payload.content.strip()
    if not content:
        raise ValidationError("Note content cannot be empty")

    note_id = db.insert_note(content)
    row = db.get_note(note_id)
    if row is None:
        raise NotFoundError("Note", note_id)

    return {
        "id": row["id"],
        "content": row["content"],
        "created_at": row["created_at"],
    }


@router.get("/{note_id}", response_model=Note)
def get_note(note_id: int) -> dict:
    """Get a single note by ID."""
    if note_id <= 0:
        raise ValidationError("Invalid note ID")

    row = db.get_note(note_id)
    if row is None:
        raise NotFoundError("Note", note_id)

    return {
        "id": row["id"],
        "content": row["content"],
        "created_at": row["created_at"],
    }


@router.get("", response_model=list[Note])
def list_notes() -> list[dict]:
    """List all notes."""
    rows = db.list_notes()
    return [
        {
            "id": r["id"],
            "content": r["content"],
            "created_at": r["created_at"],
        }
        for r in rows
    ]




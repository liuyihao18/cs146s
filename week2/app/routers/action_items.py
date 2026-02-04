from __future__ import annotations

from fastapi import APIRouter

from .. import db
from ..exceptions import LLMError, NotFoundError, ValidationError
from ..schemas import ActionItem, ActionItemUpdate, ExtractRequest, ExtractResponse
from ..services.extract import extract_action_items, extract_action_items_llm


router = APIRouter(prefix="/action-items", tags=["action-items"])


@router.post("/extract", response_model=ExtractResponse)
def extract(payload: ExtractRequest) -> dict:
    """
    Extract action items from text using heuristics or LLM.

    If save_note is True, the original text is saved as a note and linked to the extracted items.
    """
    text = payload.text.strip()
    if not text:
        raise ValidationError("Text content cannot be empty")

    note_id: int | None = None
    if payload.save_note:
        note_id = db.insert_note(text)

    # Choose extraction method
    if payload.use_llm:
        try:
            items = extract_action_items_llm(text)
        except LLMError:
            # Fallback to heuristic if LLM fails
            items = extract_action_items(text)
    else:
        items = extract_action_items(text)

    ids = db.insert_action_items(items, note_id=note_id)
    return {
        "note_id": note_id,
        "items": [
            {
                "id": i,
                "text": t,
                "note_id": note_id,
                "done": False,
                "created_at": "",  # Will be set by DB
            }
            for i, t in zip(ids, items)
        ],
    }


@router.get("", response_model=list[ActionItem])
def list_action_items(note_id: int | None = None) -> list[dict]:
    """List action items, optionally filtered by note_id."""
    rows = db.list_action_items(note_id=note_id)
    return [
        {
            "id": r["id"],
            "note_id": r["note_id"],
            "text": r["text"],
            "done": bool(r["done"]),
            "created_at": r["created_at"],
        }
        for r in rows
    ]


@router.post("/{action_item_id}/done", response_model=ActionItem)
def mark_done(action_item_id: int, payload: ActionItemUpdate) -> dict:
    """Mark an action item as done or undone."""
    if action_item_id <= 0:
        raise ValidationError("Invalid action item ID")

    db.mark_action_item_done(action_item_id, payload.done)
    row = db.get_action_item(action_item_id)
    if row is None:
        raise NotFoundError("Action item", action_item_id)

    return {
        "id": row["id"],
        "note_id": row["note_id"],
        "text": row["text"],
        "done": bool(row["done"]),
        "created_at": row["created_at"],
    }




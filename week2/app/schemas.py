"""
Pydantic schemas for request/response validation and documentation.
"""

from __future__ import annotations

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class ActionItemBase(BaseModel):
    """Base schema for action items."""

    text: str = Field(..., min_length=1, max_length=500, description="Action item text")


class ActionItemCreate(ActionItemBase):
    """Schema for creating an action item."""

    pass


class ActionItemUpdate(BaseModel):
    """Schema for updating an action item."""

    done: bool = Field(..., description="Whether the action item is complete")


class ActionItem(ActionItemBase):
    """Complete action item schema."""

    id: int = Field(..., description="Unique identifier")
    note_id: Optional[int] = Field(None, description="Associated note ID")
    done: bool = Field(False, description="Completion status")
    created_at: str = Field(..., description="Creation timestamp")

    model_config = ConfigDict(from_attributes=True)


class NoteBase(BaseModel):
    """Base schema for notes."""

    content: str = Field(..., min_length=1, description="Note content")


class NoteCreate(NoteBase):
    """Schema for creating a note."""

    pass


class Note(NoteBase):
    """Complete note schema."""

    id: int = Field(..., description="Unique identifier")
    created_at: str = Field(..., description="Creation timestamp")

    model_config = ConfigDict(from_attributes=True)


class ExtractRequest(BaseModel):
    """Schema for action item extraction request."""

    text: str = Field(..., min_length=1, description="Text to extract action items from")
    save_note: bool = Field(
        False, description="Whether to save the original text as a note"
    )
    use_llm: bool = Field(
        True, description="Whether to use LLM-based extraction (vs heuristic)"
    )


class ExtractResponse(BaseModel):
    """Schema for action item extraction response."""

    note_id: Optional[int] = Field(None, description="ID of saved note, if applicable")
    items: list[ActionItem] = Field(..., description="Extracted action items")


class ErrorResponse(BaseModel):
    """Standard error response schema."""

    detail: str = Field(..., description="Error message")
    error_code: Optional[str] = Field(None, description="Machine-readable error code")

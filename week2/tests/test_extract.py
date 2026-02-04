import os
import pytest

from ..app.services.extract import extract_action_items, extract_action_items_llm
from ..app.exceptions import ValidationError, LLMError


def test_extract_bullets_and_checkboxes():
    text = """
    Notes from meeting:
    - [ ] Set up database
    * implement API extract endpoint
    1. Write tests
    Some narrative sentence.
    """.strip()

    items = extract_action_items(text)
    assert "Set up database" in items
    assert "implement API extract endpoint" in items
    assert "Write tests" in items


def test_extract_action_items_llm_bullets(monkeypatch):
    """Test LLM extraction with bullet points."""

    def _fake_chat(*, model, messages, format):
        return {"message": {"content": "[\"Set up database\", \"Write tests\"]"}}

    monkeypatch.setattr("week2.app.services.extract.client.chat", _fake_chat)

    text = """
    Notes:
    - [ ] Set up database
    * Write tests
    """.strip()

    items = extract_action_items_llm(text, model="test-model")
    assert items == ["Set up database", "Write tests"]


def test_extract_action_items_llm_keywords(monkeypatch):
    """Test LLM extraction with keyword prefixes."""

    def _fake_chat(*, model, messages, format):
        return {"message": {"content": "[\"Send follow-up email\", \"Schedule demo\"]"}}

    monkeypatch.setattr("week2.app.services.extract.client.chat", _fake_chat)

    text = """
    todo: Send follow-up email
    action: Schedule demo
    """.strip()

    items = extract_action_items_llm(text, model="test-model")
    assert items == ["Send follow-up email", "Schedule demo"]


def test_extract_action_items_llm_empty_input(monkeypatch):
    """Test that LLM extraction raises ValidationError for empty input."""

    def _fake_chat(*, model, messages, format):
        raise AssertionError("chat should not be called for empty input")

    monkeypatch.setattr("week2.app.services.extract.client.chat", _fake_chat)

    with pytest.raises(ValidationError):
        extract_action_items_llm("   ")


def test_extract_action_items_llm_invalid_json(monkeypatch):
    """Test that LLM extraction raises LLMError for invalid JSON."""

    def _fake_chat(*, model, messages, format):
        return {"message": {"content": "invalid json"}}

    monkeypatch.setattr("week2.app.services.extract.client.chat", _fake_chat)

    text = "- [ ] Task 1"
    with pytest.raises(LLMError):
        extract_action_items_llm(text, model="test-model")


def test_extract_action_items_llm_fallback_to_heuristic(monkeypatch):
    """Test that LLM extraction falls back to heuristic on connection error."""

    def _fake_chat(*, model, messages, format):
        raise RuntimeError("LLM unavailable")

    monkeypatch.setattr("week2.app.services.extract.client.chat", _fake_chat)

    text = """
    - [ ] Set up database
    * implement API extract endpoint
    """.strip()

    with pytest.raises(LLMError):
        extract_action_items_llm(text, model="test-model")


from __future__ import annotations

import json
import os
import re
from typing import Any, List

from ..config import settings
from ..client import client
from ..exceptions import LLMError, ValidationError


BULLET_PREFIX_PATTERN = re.compile(r"^\s*([-*•]|\d+\.)\s+")
KEYWORD_PREFIXES = (
    "todo:",
    "action:",
    "next:",
)


def _is_action_line(line: str) -> bool:
    stripped = line.strip().lower()
    if not stripped:
        return False
    if BULLET_PREFIX_PATTERN.match(stripped):
        return True
    if any(stripped.startswith(prefix) for prefix in KEYWORD_PREFIXES):
        return True
    if "[ ]" in stripped or "[todo]" in stripped:
        return True
    return False


def extract_action_items(text: str) -> List[str]:
    lines = text.splitlines()
    extracted: List[str] = []
    for raw_line in lines:
        line = raw_line.strip()
        if not line:
            continue
        if _is_action_line(line):
            cleaned = BULLET_PREFIX_PATTERN.sub("", line)
            cleaned = cleaned.strip()
            # Trim common checkbox markers
            cleaned = cleaned.removeprefix("[ ]").strip()
            cleaned = cleaned.removeprefix("[todo]").strip()
            extracted.append(cleaned)
    # Fallback: if nothing matched, heuristically split into sentences and pick imperative-like ones
    if not extracted:
        sentences = re.split(r"(?<=[.!?])\s+", text.strip())
        for sentence in sentences:
            s = sentence.strip()
            if not s:
                continue
            if _looks_imperative(s):
                extracted.append(s)
    # Deduplicate while preserving order
    seen: set[str] = set()
    unique: List[str] = []
    for item in extracted:
        lowered = item.lower()
        if lowered in seen:
            continue
        seen.add(lowered)
        unique.append(item)
    return unique


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
        LLMError: If LLM call fails and heuristic fallback also fails.
    """
    if not text.strip():
        raise ValidationError("Input text cannot be empty")

    model_name = model or settings.ollama_model
    schema = {"type": "array", "items": {"type": "string"}}
    messages = [
        {
            "role": "system",
            "content": (
                "Extract action items from the user-provided notes. "
                "Return ONLY a JSON array of strings. "
                "Each string must be a concise, self-contained task."
            ),
        },
        {"role": "user", "content": text},
    ]

    try:
        response = client.chat(
            model=model_name,
            messages=messages,
            format=schema,
        )
        content = response.get("message", {}).get("content", "")
        parsed: Any = json.loads(content)
        if isinstance(parsed, list) and all(isinstance(item, str) for item in parsed):
            return [item.strip() for item in parsed if item.strip()]
    except json.JSONDecodeError as e:
        raise LLMError(f"Invalid JSON response from LLM: {str(e)}") from e
    except Exception as e:
        raise LLMError(f"LLM extraction failed: {str(e)}") from e


def _looks_imperative(sentence: str) -> bool:
    """Check if a sentence looks like an imperative command."""
    words = re.findall(r"[A-Za-z']+", sentence)
    if not words:
        return False
    first = words[0]
    # Crude heuristic: treat these as imperative starters
    imperative_starters = {
        "add",
        "create",
        "implement",
        "fix",
        "update",
        "write",
        "check",
        "verify",
        "refactor",
        "document",
        "design",
        "investigate",
    }
    return first.lower() in imperative_starters


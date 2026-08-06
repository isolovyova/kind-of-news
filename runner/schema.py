sed: --: No such file or directory
"""JSON schemas used for Responses API structured output."""

from __future__ import annotations

from typing import Any, Dict


SOURCE_SCHEMA: Dict[str, Any] = {
    "type": "object",
    "additionalProperties": False,
    "properties": {
        "block": {"type": "string", "enum": ["good_thing", "current_or_history", "tiny_fact"]},
        "name": {"type": "string"},
        "descriptor": {"type": "string"},
        "url": {"type": "string"},
    },
    "required": ["block", "name", "descriptor", "url"],
}


ISSUE_SCHEMA: Dict[str, Any] = {
    "type": "object",
    "additionalProperties": False,
    "properties": {
        "issue_id": {"type": "string"},
        "good_thing": {"type": "string"},
        "current_header": {"type": "string", "enum": ["on_this_day", "happening_now"]},
        "current_or_history": {"type": "string"},
        "tiny_fact": {"type": "string"},
        "thought": {"type": "string"},
        "sources": {"type": "array", "items": SOURCE_SCHEMA},
    },
    "required": [
        "issue_id",
        "good_thing",
        "current_header",
        "current_or_history",
        "tiny_fact",
        "thought",
        "sources",
    ],
}


RESEARCH_ITEM_SCHEMA: Dict[str, Any] = {
    "type": "object",
    "additionalProperties": False,
    "properties": {
        "notes": {"type": "string"},
        "sources": {"type": "array", "items": SOURCE_SCHEMA},
    },
    "required": ["notes", "sources"],
}


RESEARCH_SCHEMA: Dict[str, Any] = {
    "type": "object",
    "additionalProperties": False,
    "properties": {
        "good_thing": RESEARCH_ITEM_SCHEMA,
        "current_or_history": RESEARCH_ITEM_SCHEMA,
        "tiny_fact": RESEARCH_ITEM_SCHEMA,
    },
    "required": ["good_thing", "current_or_history", "tiny_fact"],
}

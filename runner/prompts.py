sed: --: No such file or directory
"""Prompts and evidence schemas for the two-stage generation flow."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict

from .schema import ISSUE_SCHEMA, RESEARCH_SCHEMA


def load_skill_text(skill_path: str) -> str:
    content = Path(skill_path).read_text(encoding="utf-8")
    if content.startswith("---"):
        end = content.find("\n---", 3)
        if end != -1:
            content = content[end + len("\n---") :]
    return content.strip()


def research_prompt(skill_text: str, issue_date: str, weekday: str) -> str:
    return """
You are the research stage of Kind of News. Use the web_search tool before
answering. The requested publication date is {issue_date} ({weekday}).

Find evidence for exactly three blocks:
1. A recent, specific, non-political good-news story.
2. Either a strong date-specific historical detail for {issue_date}, or a
   genuinely striking non-political event from the last 24–48 hours.
3. One curious, verifiable tiny fact.

Search more than once when needed. Prefer primary and reputable sources. Do not
use listicles, content farms, or unsupported claims. Return research notes and
the exact HTTPS source URLs that support the notes. Do not draft the final post.

The following skill is the governing editorial policy:

{skill}
""".format(issue_date=issue_date, weekday=weekday, skill=skill_text)


def compose_prompt(
    skill_text: str,
    issue_date: str,
    weekday: str,
    research: Dict[str, Any],
) -> str:
    return """
You are the composition stage of Kind of News. Create one final issue for
{issue_date} ({weekday}) from the source-backed research below.

Return only JSON matching the supplied schema. Keep every factual claim within
the evidence. Map each factual block to the exact source URL(s) used in the
research. Use `on_this_day` unless the evidence clearly supports a qualified
`happening_now` item. Keep the output concise and follow the editorial policy.

Research evidence:
{research}

Editorial policy:
{skill}
""".format(
        issue_date=issue_date,
        weekday=weekday,
        research=json.dumps(research, ensure_ascii=False, indent=2),
        skill=skill_text,
    )


def schema_format(name: str, schema: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "type": "json_schema",
        "name": name,
        "description": "Strict structured output for Kind of News.",
        "schema": schema,
        "strict": True,
    }


def research_format() -> Dict[str, Any]:
    return schema_format("kind_of_news_research", RESEARCH_SCHEMA)


def issue_format() -> Dict[str, Any]:
    return schema_format("kind_of_news_issue", ISSUE_SCHEMA)

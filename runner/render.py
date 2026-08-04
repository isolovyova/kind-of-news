"""Render a validated issue for supported delivery channels."""

from __future__ import annotations

from typing import Any, Dict, List

from .models import BLOCK_ORDER, NewsIssue


def intro(issue_id: str) -> str:
    return (
        "Kind of News #%s\n"
        "The world is noisy. This is a small, warm window into the parts that don't scream."
        % issue_id
    )


def render_markdown(issue: NewsIssue) -> str:
    header = "📅 On this day" if issue.current_header == "on_this_day" else "⚡ Happening now"
    source_lines = []
    link_lines = []
    ordered_sources = []
    for block in BLOCK_ORDER:
        ordered_sources.extend(source for source in issue.sources if source.block == block)
    for index, source in enumerate(ordered_sources, start=1):
        source_lines.append("[%d] %s — %s" % (index, source.name, source.descriptor))
        link_lines.append("[%d] %s" % (index, source.url))

    return "\n\n".join(
        [
            intro(issue.issue_id),
            "☀️ Good thing\n" + issue.good_thing,
            header + "\n" + issue.current_or_history,
            "🧠 Tiny fact\n" + issue.tiny_fact,
            "🌱 Thought for the day\n" + issue.thought,
            "—\nSources:\n"
            + "\n".join(source_lines)
            + "\n\nFull links (for verification, remove before publishing):\n"
            + "\n".join(link_lines),
            "Kind of News — sent with love and verified links.",
        ]
    )


def webhook_payload(issue: NewsIssue, provider: str) -> Dict[str, Any]:
    text = render_markdown(issue)
    title = "Kind of News #%s" % issue.issue_id
    if provider == "slack":
        return {"text": text}
    if provider == "discord":
        return {"content": text}
    if provider == "ntfy":
        return {"text": text, "title": title}
    return {
        "title": title,
        "issue_id": issue.issue_id,
        "text": text,
        "sources": [source.to_dict() for source in issue.sources],
    }


def split_text(text: str, limit: int = 4096) -> List[str]:
    """Split long Telegram content without cutting a line where possible."""

    if len(text) <= limit:
        return [text]
    chunks: List[str] = []
    remaining = text
    while len(remaining) > limit:
        boundary = remaining.rfind("\n", 0, limit + 1)
        if boundary < limit // 2:
            boundary = limit
        chunks.append(remaining[:boundary].rstrip())
        remaining = remaining[boundary:].lstrip()
    if remaining:
        chunks.append(remaining)
    return chunks

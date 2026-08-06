"""Render a validated issue for supported delivery channels."""

from __future__ import annotations

from html import escape
from typing import Any, Dict, List
from urllib.parse import urlparse

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
    ordered_sources = []
    for block in BLOCK_ORDER:
        ordered_sources.extend(source for source in issue.sources if source.block == block)
    for index, source in enumerate(ordered_sources, start=1):
        source_lines.append("[%d] [%s](%s) — %s" % (index, source.name, source.url, source.descriptor))

    return "\n\n".join(
        [
            intro(issue.issue_id),
            "☀️ Good thing\n" + issue.good_thing,
            header + "\n" + issue.current_or_history,
            "🧠 Tiny fact\n" + issue.tiny_fact,
            "🌱 Thought for the day\n" + issue.thought,
            "Sources:\n"
            + "\n".join(source_lines),
            "Kind of News — sent with love and verified links.",
        ]
    )


def _html_text(value: str) -> str:
    return escape(value).replace("\n", "<br>\n")


def render_html(
    issue: NewsIssue,
    *,
    include_issue_title: bool = True,
    footer: str = "Kind of News — sent with love and verified links.",
) -> str:
    """Render safe HTML with clickable validated source links."""

    header = "📅 On this day" if issue.current_header == "on_this_day" else "⚡ Happening now"
    source_items = []
    ordered_sources = []
    for block in BLOCK_ORDER:
        ordered_sources.extend(source for source in issue.sources if source.block == block)
    for source in ordered_sources:
        parsed = urlparse(source.url)
        source_name = escape(source.name)
        if parsed.scheme == "https" and parsed.netloc:
            source_name = '<a href="%s">%s</a>' % (
                escape(source.url, quote=True),
                source_name,
            )
        source_items.append(
            "<li>%s &mdash; %s</li>" % (source_name, _html_text(source.descriptor))
        )

    lines = [
        "<!doctype html>",
        "<html><body>",
    ]
    if include_issue_title:
        lines.append("<h1>Kind of News #%s</h1>" % escape(issue.issue_id))
    lines.extend(
        [
            "<p>The world is noisy. This is a small, warm window into the parts that don't scream.</p>",
            "<h2>☀️ Good thing</h2>",
            "<p>%s</p>" % _html_text(issue.good_thing),
            "<h2>%s</h2>" % escape(header),
            "<p>%s</p>" % _html_text(issue.current_or_history),
            "<h2>🧠 Tiny fact</h2>",
            "<p>%s</p>" % _html_text(issue.tiny_fact),
            "<h2>🌱 Thought for the day</h2>",
            "<p>%s</p>" % _html_text(issue.thought),
            "<h2>Sources</h2>",
            "<ol>\n%s\n</ol>" % "\n".join(source_items),
            "<p>%s</p>" % _html_text(footer),
            "</body></html>",
        ]
    )
    return "\n".join(lines)


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

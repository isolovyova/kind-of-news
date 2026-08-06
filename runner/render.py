"""Render a validated issue for supported delivery channels."""

from __future__ import annotations

from html import escape
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
    include_issue_title: bool = False,
    footer: str = "Sent with love and verified links.",
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
sed: --: No such file or directory

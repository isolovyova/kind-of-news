"""Fail-closed validation for generated issues."""

from __future__ import annotations

import re
from datetime import date
from typing import Iterable, Optional, Sequence
from urllib.parse import urlparse

from .models import BLOCK_ORDER, CURRENT_HEADERS, NewsIssue


ISSUE_ID_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")


class IssueValidationError(ValueError):
    """Raised when an issue is not safe to deliver."""

    def __init__(self, errors: Sequence[str]):
        self.errors = list(errors)
        super().__init__("; ".join(self.errors))


def validate_issue(
    issue: NewsIssue,
    expected_date: Optional[str] = None,
    citation_urls: Optional[Iterable[str]] = None,
) -> None:
    errors = []
    if not ISSUE_ID_RE.match(issue.issue_id):
        errors.append("issue_id must use YYYY-MM-DD")
    else:
        try:
            date.fromisoformat(issue.issue_id)
        except ValueError:
            errors.append("issue_id is not a real calendar date")
    if expected_date and issue.issue_id != expected_date:
        errors.append("issue_id does not match the requested publication date")
    if issue.current_header not in CURRENT_HEADERS:
        errors.append("current_header must be on_this_day or happening_now")

    narrative = {
        "good_thing": issue.good_thing,
        "current_or_history": issue.current_or_history,
        "tiny_fact": issue.tiny_fact,
        "thought": issue.thought,
    }
    for field, value in narrative.items():
        if not value.strip():
            errors.append("%s cannot be empty" % field)
        if "—" in value:
            errors.append("%s contains an em dash" % field)

    source_blocks = {source.block for source in issue.sources}
    for block in BLOCK_ORDER:
        if block not in source_blocks:
            errors.append("missing source for %s" % block)
    if len(issue.sources) < 3:
        errors.append("at least three sources are required")

    urls = set()
    for source in issue.sources:
        if source.block not in BLOCK_ORDER:
            errors.append("source has unsupported block %s" % source.block)
        parsed = urlparse(source.url)
        if parsed.scheme != "https" or not parsed.netloc:
            errors.append("source URL must be an absolute HTTPS URL: %s" % source.url)
        if "..." in source.url:
            errors.append("source URL is incomplete: %s" % source.url)
        urls.add(source.url)

    if citation_urls is not None:
        cited = {url for url in citation_urls if isinstance(url, str)}
        missing_citations = sorted(urls - cited)
        if missing_citations:
            errors.append("source URL was not present in research evidence: %s" % ", ".join(missing_citations))

    if errors:
        raise IssueValidationError(errors)

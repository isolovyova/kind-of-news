"""Static site delivery for the Kind of News public page.

The adapter writes one validated issue into the published docs directory so
GitHub Pages can serve it.  It deliberately does not touch git: committing the
result belongs to the workflow, which keeps this adapter pure and testable.
"""

from __future__ import annotations

import json
from pathlib import Path

from ..models import NewsIssue
from ..validate import IssueValidationError, validate_issue
from .base import DeliveryError, DeliveryResult


ISSUES_DIRNAME = "issues"
LATEST_FILENAME = "latest.json"


class SiteDelivery:
    """Publish validated issues as JSON for the static Kind of News site."""

    def __init__(self, docs_root: str = "docs"):
        self._issues_dir = Path(docs_root) / ISSUES_DIRNAME

    @property
    def issues_dir(self) -> Path:
        return self._issues_dir

    def send(self, issue: NewsIssue) -> DeliveryResult:
        """Validate one issue and write it as the dated and latest payloads."""

        try:
            validate_issue(issue)
        except IssueValidationError as exc:
            raise DeliveryError("Site publish blocked because the issue failed validation") from exc

        payload = json.dumps(issue.to_dict(), ensure_ascii=False, indent=2) + "\n"
        try:
            self._issues_dir.mkdir(parents=True, exist_ok=True)
            # The dated file is the archive. latest.json remains a compatibility
            # pointer for older readers, while the public page requests today's
            # dated file explicitly.
            (self._issues_dir / ("%s.json" % issue.issue_id)).write_text(payload, encoding="utf-8")
            (self._issues_dir / LATEST_FILENAME).write_text(payload, encoding="utf-8")
        except OSError as exc:
            raise DeliveryError("Site publish failed to write the issue files") from exc

        return DeliveryResult(
            channel="site",
            delivered=True,
            detail="written to %s" % self._issues_dir,
        )

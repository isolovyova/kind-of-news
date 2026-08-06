"""Small per-issue state store used with the GitHub Actions cache."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Optional, Set

from .models import NewsIssue


class StateStore:
    def __init__(self, root: str, issue_id: str):
        self.root = Path(root) / issue_id

    @property
    def issue_path(self) -> Path:
        return self.root / "issue.json"

    def load_issue(self) -> Optional[NewsIssue]:
        if not self.issue_path.exists():
            return None
        raw = json.loads(self.issue_path.read_text(encoding="utf-8"))
        return NewsIssue.from_mapping(raw)

    def save_issue(self, issue: NewsIssue) -> None:
        self.root.mkdir(parents=True, exist_ok=True)
        self.issue_path.write_text(
            json.dumps(issue.to_dict(), ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )

    def sent_channels(self) -> Set[str]:
        if not self.root.exists():
            return set()
        return {
            marker.stem
            for marker in self.root.glob("*.sent")
            if marker.is_file()
        }

    def mark_sent(self, channel: str) -> None:
        self.root.mkdir(parents=True, exist_ok=True)
        (self.root / (channel + ".sent")).write_text("ok\n", encoding="utf-8")

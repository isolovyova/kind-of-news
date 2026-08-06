#!/usr/bin/env python3
"""Repository-local skill validation for CI and local checks."""

from __future__ import annotations

import re
import sys
from pathlib import Path

try:
    import yaml
except ImportError as exc:  # pragma: no cover
    raise SystemExit("Install dependencies first: python -m pip install -r requirements.txt") from exc


def validate(path: str) -> None:
    skill_dir = Path(path)
    skill_file = skill_dir / "SKILL.md"
    if not skill_file.exists():
        raise ValueError("SKILL.md not found: %s" % skill_file)
    content = skill_file.read_text(encoding="utf-8")
    match = re.match(r"^---\n(.*?)\n---", content, re.DOTALL)
    if not match:
        raise ValueError("Invalid or missing YAML frontmatter")
    frontmatter = yaml.safe_load(match.group(1))
    if not isinstance(frontmatter, dict):
        raise ValueError("Frontmatter must be a mapping")
    allowed = {"name", "description", "license", "allowed-tools", "metadata"}
    unexpected = set(frontmatter) - allowed
    if unexpected:
        raise ValueError("Unexpected frontmatter keys: %s" % ", ".join(sorted(unexpected)))
    name = frontmatter.get("name")
    description = frontmatter.get("description")
    if not isinstance(name, str) or not re.match(r"^[a-z0-9-]{1,64}$", name):
        raise ValueError("name must be lowercase hyphen-case and no longer than 64 characters")
    if not isinstance(description, str) or not description.strip() or len(description) > 1024:
        raise ValueError("description must be a non-empty string under 1024 characters")
    print("Skill is valid: %s" % skill_file)


if __name__ == "__main__":
    if len(sys.argv) != 2:
        raise SystemExit("Usage: python scripts/validate_skill.py skills/kind-of-news")
    try:
        validate(sys.argv[1])
    except (OSError, ValueError) as exc:
        print("Skill validation failed: %s" % exc)
        raise SystemExit(1)

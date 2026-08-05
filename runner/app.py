"""Command-line application for generation, validation, and delivery."""

from __future__ import annotations

import argparse
import json
import os
from datetime import date, datetime
from pathlib import Path
from typing import Any, Dict, Mapping, Optional, Sequence
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

from .config import AppConfig, ConfigError, load_config
from .delivery import ButtondownDelivery, DeliveryError, GmailDelivery, TelegramDelivery, WebhookDelivery
from .models import NewsIssue
from .openai_client import OpenAIRuntimeError, ResponsesClient
from .prompts import load_skill_text
from .render import render_markdown
from .state import StateStore
from .validate import IssueValidationError, validate_issue


class RunnerError(RuntimeError):
    """Raised when a run cannot complete safely."""


def issue_date_for(config: AppConfig, requested: Optional[str] = None) -> str:
    if requested:
        try:
            return date.fromisoformat(requested).isoformat()
        except ValueError as exc:
            raise RunnerError("--date must use YYYY-MM-DD") from exc
    try:
        return datetime.now(ZoneInfo(config.timezone)).date().isoformat()
    except ZoneInfoNotFoundError as exc:
        raise RunnerError("Unknown timezone: %s" % config.timezone) from exc


def _make_delivery(channel: str, config: AppConfig, environ: Mapping[str, str]) -> Any:
    if channel == "buttondown":
        return ButtondownDelivery(environ.get("BUTTONDOWN_API_KEY", ""))
    if channel == "gmail":
        return GmailDelivery(
            environ.get("GMAIL_CLIENT_ID", ""),
            environ.get("GMAIL_CLIENT_SECRET", ""),
            environ.get("GMAIL_REFRESH_TOKEN", ""),
            environ.get("GMAIL_TO", ""),
            sender=environ.get("GMAIL_FROM", ""),
        )
    if channel == "telegram":
        return TelegramDelivery(
            environ.get("TELEGRAM_BOT_TOKEN", ""),
            environ.get("TELEGRAM_CHAT_ID", ""),
        )
    if channel == "webhook":
        return WebhookDelivery(
            environ.get("WEBHOOK_URL", ""),
            config.delivery.webhook_provider,
        )
    raise RunnerError("Unsupported delivery channel: %s" % channel)


def _load_fixture(path: str, expected_date: str) -> NewsIssue:
    raw = json.loads(Path(path).read_text(encoding="utf-8"))
    issue = NewsIssue.from_mapping(raw)
    validate_issue(issue, expected_date=expected_date)
    return issue


def run(
    config_path: Optional[str] = None,
    requested_date: Optional[str] = None,
    skill_path: str = "skills/kind-of-news/SKILL.md",
    state_dir: str = ".kind-of-news-state",
    dry_run: bool = False,
    fixture_path: Optional[str] = None,
    environ: Optional[Mapping[str, str]] = None,
) -> int:
    environment = environ if environ is not None else os.environ
    config = load_config(config_path)
    issue_id = issue_date_for(config, requested_date)
    weekday = date.fromisoformat(issue_id).strftime("%A")
    state = StateStore(state_dir, issue_id)
    sent = state.sent_channels()

    if not dry_run and set(config.delivery.channels).issubset(sent):
        print("Issue %s is already delivered to all configured channels." % issue_id)
        return 0

    issue = state.load_issue()
    if issue is None:
        if fixture_path:
            issue = _load_fixture(fixture_path, issue_id)
        else:
            skill_text = load_skill_text(skill_path)
            client = ResponsesClient(
                environment.get("OPENAI_API_KEY", ""),
                config.model,
            )
            try:
                issue, _ = client.generate_issue(skill_text, issue_id, weekday)
            except (OpenAIRuntimeError, IssueValidationError) as exc:
                raise RunnerError("Generation failed closed: %s" % exc) from exc
        validate_issue(issue, expected_date=issue_id)
        if not dry_run:
            state.save_issue(issue)

    rendered = render_markdown(issue)
    if dry_run:
        print(rendered)
        return 0

    failures = []
    for channel in config.delivery.channels:
        if channel in sent:
            print("Skipping already delivered channel: %s" % channel)
            continue
        try:
            delivery = _make_delivery(channel, config, environment)
            delivery.send(issue)
            state.mark_sent(channel)
            print("Delivered issue %s to %s" % (issue_id, channel))
        except (DeliveryError, RunnerError) as exc:
            failures.append("%s: %s" % (channel, exc))
            print("Delivery failed for %s: %s" % (channel, exc))

    if failures:
        raise RunnerError("One or more channels failed; rerun to retry failed channels")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Generate and deliver a Kind of News issue (advanced repo runner)"
    )
    parser.add_argument("--config", default=None, help="Path to config.yml")
    parser.add_argument("--date", default=None, help="Issue date in YYYY-MM-DD")
    parser.add_argument("--skill", default="skills/kind-of-news/SKILL.md")
    parser.add_argument("--state-dir", default=".kind-of-news-state")
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Advanced repo-runner preview; render without delivery or state writes",
    )
    parser.add_argument("--fixture", default=None, help="Render a validated issue JSON fixture without the API")
    return parser


def main(argv: Optional[Sequence[str]] = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        return run(
            config_path=args.config,
            requested_date=args.date,
            skill_path=args.skill,
            state_dir=args.state_dir,
            dry_run=args.dry_run,
            fixture_path=args.fixture,
        )
    except (ConfigError, RunnerError, IssueValidationError, OSError, ValueError) as exc:
        print("Kind of News failed: %s" % exc)
        return 1

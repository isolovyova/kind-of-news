#!/usr/bin/env python3
"""Create the non-secret Kind of News config and validate GitHub Secrets."""

from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path
from typing import List, Optional, Sequence

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

try:
    import yaml
except ImportError as exc:  # pragma: no cover - requirements install PyYAML.
    raise SystemExit("Install dependencies first: python -m pip install -r requirements.txt") from exc

from runner.config import (  # noqa: E402
    ALLOWED_CHANNELS,
    DEFAULT_TIMEZONE,
    load_config,
    missing_secret_names,
)


def _parse_channels(raw: str) -> List[str]:
    channels = [item.strip().lower() for item in raw.split(",") if item.strip()]
    unknown = set(channels) - ALLOWED_CHANNELS
    if unknown or not channels:
        raise ValueError("channels must contain one or more of: gmail, telegram, webhook")
    return list(dict.fromkeys(channels))


def build_config(channels: List[str], timezone: str, issue_time: str, provider: str) -> dict:
    return {
        "language": "en",
        "timezone": timezone,
        "model": "gpt-5.6-terra",
        "schedule": {
            "days": ["monday", "wednesday", "friday"],
            "time": issue_time,
        },
        "delivery": {
            "channels": channels,
            "webhook_provider": provider,
        },
    }


def interactive_values() -> tuple:
    channels = _parse_channels(input("Channels [gmail, telegram, webhook] (default: gmail): ").strip() or "gmail")
    timezone = input("Timezone (default: America/Vancouver): ").strip() or DEFAULT_TIMEZONE
    issue_time = input("Delivery time (default: 06:00): ").strip() or "06:00"
    provider = "generic"
    if "webhook" in channels:
        provider = input("Webhook provider [generic/slack/discord/ntfy] (default: generic): ").strip() or "generic"
    return channels, timezone, issue_time, provider


def write_config(output: str, channels: Optional[str], timezone: str, issue_time: str, provider: str) -> int:
    if channels:
        selected = _parse_channels(channels)
        selected_timezone = timezone
        selected_time = issue_time
        selected_provider = provider
    else:
        selected, selected_timezone, selected_time, selected_provider = interactive_values()
    payload = build_config(selected, selected_timezone, selected_time, selected_provider)
    Path(output).write_text(yaml.safe_dump(payload, sort_keys=False), encoding="utf-8")
    print("Wrote %s" % output)
    print("Add these names to GitHub Secrets; values are never written by this script:")
    config = load_config(output)
    for name in missing_secret_names(config, {}):
        print("- %s" % name)
    print("Then run the 'Kind of News Setup' workflow to verify the configuration.")
    return 0


def check_config(config_path: str) -> int:
    config = load_config(config_path)
    missing = missing_secret_names(config)
    if missing:
        print("Missing required environment variables / GitHub Secrets:")
        for name in missing:
            print("- %s" % name)
        return 1
    print("Configuration and required secret names are present.")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Set up Kind of News without handling secrets")
    parser.add_argument("--output", default="config.yml")
    parser.add_argument("--channels", help="Comma-separated: gmail,telegram,webhook")
    parser.add_argument("--timezone", default=DEFAULT_TIMEZONE)
    parser.add_argument("--time", dest="issue_time", default="06:00")
    parser.add_argument("--webhook-provider", default="generic")
    parser.add_argument("--check", action="store_true", help="Check config and required environment variables")
    parser.add_argument("--config", default="config.yml", help="Config path used by --check")
    return parser


def main(argv: Optional[Sequence[str]] = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        if args.check:
            return check_config(args.config)
        return write_config(args.output, args.channels, args.timezone, args.issue_time, args.webhook_provider)
    except (OSError, ValueError) as exc:
        print("Setup failed: %s" % exc)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())

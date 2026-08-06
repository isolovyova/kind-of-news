sed: --: No such file or directory
"""Configuration loading with safe defaults and no credential storage."""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, List, Mapping, Optional

try:
    import yaml
except ImportError:  # pragma: no cover - the runtime requirements install PyYAML.
    yaml = None


DEFAULT_TIMEZONE = "America/Vancouver"
DEFAULT_MODEL = "gpt-5.6-terra"
DEFAULT_CHANNELS = ["buttondown"]
ALLOWED_CHANNELS = {"buttondown"}


@dataclass(frozen=True)
class DeliveryConfig:
    channels: List[str] = field(default_factory=lambda: list(DEFAULT_CHANNELS))


@dataclass(frozen=True)
class AppConfig:
    timezone: str = DEFAULT_TIMEZONE
    time: str = "06:00"
    days: List[str] = field(default_factory=lambda: ["monday", "wednesday", "friday"])
    language: str = "en"
    model: str = DEFAULT_MODEL
    delivery: DeliveryConfig = field(default_factory=DeliveryConfig)


class ConfigError(ValueError):
    """Raised when user configuration is invalid."""


def _as_mapping(raw: Any) -> Mapping[str, Any]:
    return raw if isinstance(raw, Mapping) else {}


def load_config(path: Optional[str] = None) -> AppConfig:
    """Load config.yml when present, otherwise use public defaults."""

    raw: Mapping[str, Any] = {}
    if path:
        config_path = Path(path)
        if not config_path.exists():
            raise ConfigError("Configuration file not found: %s" % config_path)
        if yaml is None:
            raise ConfigError("PyYAML is required to read configuration files")
        loaded = yaml.safe_load(config_path.read_text(encoding="utf-8"))
        raw = _as_mapping(loaded)

    schedule = _as_mapping(raw.get("schedule"))
    delivery = _as_mapping(raw.get("delivery"))
    if "webhook_provider" in delivery:
        raise ConfigError("delivery.webhook_provider is no longer supported")
    channels = delivery.get("channels", DEFAULT_CHANNELS)
    if isinstance(channels, str):
        channels = [channels]
    if not isinstance(channels, list) or not all(isinstance(item, str) for item in channels):
        raise ConfigError("delivery.channels must be a list of channel names")
    normalized_channels = [item.strip().lower() for item in channels if item.strip()]
    unknown_channels = set(normalized_channels) - ALLOWED_CHANNELS
    if unknown_channels:
        raise ConfigError("Unsupported channel(s): %s" % ", ".join(sorted(unknown_channels)))
    if normalized_channels != ["buttondown"]:
        raise ConfigError("delivery.channels must contain only buttondown")

    timezone = str(raw.get("timezone", DEFAULT_TIMEZONE)).strip()
    issue_time = str(schedule.get("time", "06:00")).strip()
    days = schedule.get("days", ["monday", "wednesday", "friday"])
    if isinstance(days, str):
        days = [days]
    if not isinstance(days, list) or not all(isinstance(item, str) for item in days):
        raise ConfigError("schedule.days must be a list of weekday names")

    configured_model = str(raw.get("model", DEFAULT_MODEL)).strip()
    environment_model = os.environ.get("OPENAI_MODEL", "").strip()
    return AppConfig(
        timezone=timezone,
        time=issue_time,
        days=[item.strip().lower() for item in days],
        language=str(raw.get("language", "en")).strip().lower(),
        model=environment_model or configured_model or DEFAULT_MODEL,
        delivery=DeliveryConfig(
            channels=normalized_channels,
        ),
    )


def required_secret_names(config: AppConfig) -> List[str]:
    return ["OPENAI_API_KEY", "BUTTONDOWN_API_KEY"]


def missing_secret_names(config: AppConfig, environ: Optional[Mapping[str, str]] = None) -> List[str]:
    values = environ if environ is not None else os.environ
    return [name for name in required_secret_names(config) if not values.get(name)]

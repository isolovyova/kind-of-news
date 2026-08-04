"""Shared delivery result and error types."""

from __future__ import annotations

from dataclasses import dataclass


class DeliveryError(RuntimeError):
    """Raised for a delivery failure without exposing credentials."""


@dataclass(frozen=True)
class DeliveryResult:
    channel: str
    delivered: bool
    detail: str = ""

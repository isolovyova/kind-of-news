"""Delivery adapters for Kind of News output."""

from .base import DeliveryError, DeliveryResult
from .buttondown import ButtondownDelivery

__all__ = [
    "DeliveryError",
    "DeliveryResult",
    "ButtondownDelivery",
]

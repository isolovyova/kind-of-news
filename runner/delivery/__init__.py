"""Delivery adapters for Kind of News output."""

from .base import DeliveryError, DeliveryResult
from .buttondown import ButtondownDelivery
from .site import SiteDelivery

__all__ = [
    "DeliveryError",
    "DeliveryResult",
    "ButtondownDelivery",
    "SiteDelivery",
]

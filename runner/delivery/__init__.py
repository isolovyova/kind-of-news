"""Delivery adapters for Kind of News output."""

from .base import DeliveryError, DeliveryResult
from .buttondown import ButtondownDelivery
from .gmail import GmailDelivery
from .telegram import TelegramDelivery
from .webhook import WebhookDelivery

__all__ = [
    "DeliveryError",
    "DeliveryResult",
    "ButtondownDelivery",
    "GmailDelivery",
    "TelegramDelivery",
    "WebhookDelivery",
]

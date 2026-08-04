"""Generic, Slack, Discord, and ntfy webhook delivery."""

from __future__ import annotations

from typing import Any, Callable, Dict

from ..models import NewsIssue
from ..render import render_markdown, webhook_payload
from .base import DeliveryError, DeliveryResult
from .http import post_json, post_text


class WebhookDelivery:
    def __init__(
        self,
        url: str,
        provider: str = "generic",
        post_json_fn: Callable[..., Dict[str, Any]] = post_json,
        post_text_fn: Callable[..., None] = post_text,
    ):
        if not url:
            raise DeliveryError("WEBHOOK_URL is required")
        self.url = url
        self.provider = provider.lower()
        self.post_json = post_json_fn
        self.post_text = post_text_fn

    def send(self, issue: NewsIssue) -> DeliveryResult:
        if self.provider == "ntfy":
            self.post_text(
                self.url,
                render_markdown(issue),
                headers={"Title": "Kind of News #%s" % issue.issue_id},
            )
        else:
            payload = webhook_payload(issue, self.provider)
            result = self.post_json(self.url, payload)
            if isinstance(result, dict) and result.get("ok") is False:
                raise DeliveryError("webhook provider rejected the message")
        return DeliveryResult(channel="webhook", delivered=True)

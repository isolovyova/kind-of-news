"""Buttondown API delivery for the branded Kind of News newsletter."""

from __future__ import annotations

import json
from typing import Any, Callable, Dict
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from ..models import NewsIssue
from ..render import render_html
from ..validate import IssueValidationError, validate_issue
from .base import DeliveryError, DeliveryResult


EMAILS_URL = "https://api.buttondown.com/v1/emails"
QUEUED_STATUSES = frozenset({"about_to_send", "in_flight", "resending", "sent", "throttled"})


def _post_buttondown(url: str, api_key: str, payload: Dict[str, Any]) -> Dict[str, Any]:
    """Publish one email using an API key supplied by the secure host."""

    request = Request(
        url,
        data=json.dumps(payload, ensure_ascii=False).encode("utf-8"),
        headers={
            "Authorization": "Token " + api_key,
            "Content-Type": "application/json",
            "Accept": "application/json",
            # Buttondown requires this one-time acknowledgement before the
            # first API-initiated live send for an API key. This adapter is
            # called only by a non-dry live delivery path.
            "X-Buttondown-Live-Dangerously": "true",
        },
        method="POST",
    )
    try:
        with urlopen(request, timeout=30) as response:
            value = json.loads(response.read().decode("utf-8"))
    except (HTTPError, URLError, json.JSONDecodeError) as exc:
        raise DeliveryError("Buttondown email publish failed") from exc
    if not isinstance(value, dict):
        raise DeliveryError("Buttondown returned an invalid publish response")
    return value


class ButtondownDelivery:
    """Publish validated issues to the configured Buttondown newsletter."""

    def __init__(
        self,
        api_key: str,
        publish_request: Callable[[str, str, Dict[str, Any]], Dict[str, Any]] = _post_buttondown,
    ):
        if not api_key:
            raise DeliveryError("BUTTONDOWN_API_KEY is required")
        self._api_key = api_key
        self.publish_request = publish_request

    def send(self, issue: NewsIssue) -> DeliveryResult:
        """Validate, render, and queue one issue for Buttondown subscribers."""

        try:
            validate_issue(issue)
        except IssueValidationError as exc:
            raise DeliveryError("Buttondown publish blocked because the issue failed validation") from exc

        payload = {
            "subject": "Kind of News #%s" % issue.issue_id,
            "body": "<!-- buttondown-editor-mode: fancy -->\n" + render_html(issue),
            "slug": "kind-of-news-%s" % issue.issue_id,
            # Buttondown now safely defaults API-created emails to drafts. A
            # live Kind of News run is explicitly user-confirmed, so queue the
            # validated issue for sending instead.
            "status": "about_to_send",
        }
        try:
            response = self.publish_request(EMAILS_URL, self._api_key, payload)
        except DeliveryError:
            raise
        except Exception as exc:  # Injectable transports must fail closed too.
            raise DeliveryError("Buttondown email publish failed") from exc
        if not isinstance(response, dict) or not response.get("id"):
            raise DeliveryError("Buttondown did not return a published email id")
        if response.get("status") not in QUEUED_STATUSES:
            raise DeliveryError("Buttondown did not confirm that the email was queued for delivery")
        return DeliveryResult(channel="buttondown", delivered=True, detail="published to subscribers")

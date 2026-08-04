"""Gmail API OAuth refresh and direct message sending."""

from __future__ import annotations

import base64
import json
from email.message import EmailMessage
from typing import Any, Callable, Dict, Optional
from urllib.parse import urlencode
from urllib.request import Request, urlopen
from urllib.error import HTTPError, URLError

from ..models import NewsIssue
from ..render import render_markdown
from .base import DeliveryError, DeliveryResult


TOKEN_URL = "https://oauth2.googleapis.com/token"
SEND_URL = "https://gmail.googleapis.com/gmail/v1/users/me/messages/send"


def _post_form(url: str, values: Dict[str, str]) -> Dict[str, Any]:
    request = Request(
        url,
        data=urlencode(values).encode("utf-8"),
        headers={"Content-Type": "application/x-www-form-urlencoded"},
        method="POST",
    )
    try:
        with urlopen(request, timeout=30) as response:
            return json.loads(response.read().decode("utf-8"))
    except (HTTPError, URLError, json.JSONDecodeError) as exc:
        raise DeliveryError("Gmail OAuth token refresh failed") from exc


def _post_gmail(url: str, token: str, payload: Dict[str, Any]) -> Dict[str, Any]:
    request = Request(
        url,
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Authorization": "Bearer " + token,
            "Content-Type": "application/json",
            "Accept": "application/json",
        },
        method="POST",
    )
    try:
        with urlopen(request, timeout=30) as response:
            return json.loads(response.read().decode("utf-8"))
    except (HTTPError, URLError, json.JSONDecodeError) as exc:
        raise DeliveryError("Gmail message send failed") from exc


class GmailDelivery:
    def __init__(
        self,
        client_id: str,
        client_secret: str,
        refresh_token: str,
        recipient: str,
        token_exchange: Callable[[str, Dict[str, str]], Dict[str, Any]] = _post_form,
        send_request: Callable[[str, str, Dict[str, Any]], Dict[str, Any]] = _post_gmail,
    ):
        values = (client_id, client_secret, refresh_token, recipient)
        if not all(values):
            raise DeliveryError(
                "GMAIL_CLIENT_ID, GMAIL_CLIENT_SECRET, GMAIL_REFRESH_TOKEN, and GMAIL_TO are required"
            )
        self.client_id = client_id
        self.client_secret = client_secret
        self.refresh_token = refresh_token
        self.recipient = recipient
        self.token_exchange = token_exchange
        self.send_request = send_request

    def send(self, issue: NewsIssue) -> DeliveryResult:
        token_response = self.token_exchange(
            TOKEN_URL,
            {
                "client_id": self.client_id,
                "client_secret": self.client_secret,
                "refresh_token": self.refresh_token,
                "grant_type": "refresh_token",
            },
        )
        access_token = token_response.get("access_token")
        if not access_token:
            raise DeliveryError("Gmail OAuth response did not contain an access token")

        message = EmailMessage()
        message["To"] = self.recipient
        message["Subject"] = "Kind of News #%s" % issue.issue_id
        message.set_content(render_markdown(issue))
        encoded = base64.urlsafe_b64encode(message.as_bytes()).decode("ascii")
        response = self.send_request(SEND_URL, access_token, {"raw": encoded})
        if not isinstance(response, dict) or not response.get("id"):
            raise DeliveryError("Gmail did not return a message id")
        return DeliveryResult(channel="gmail", delivered=True)

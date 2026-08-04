"""Telegram Bot API delivery."""

from __future__ import annotations

from typing import Any, Callable, Dict, Optional

from ..models import NewsIssue
from ..render import render_markdown, split_text
from .base import DeliveryError, DeliveryResult
from .http import post_json


class TelegramDelivery:
    def __init__(
        self,
        bot_token: str,
        chat_id: str,
        post: Callable[..., Dict[str, Any]] = post_json,
    ):
        if not bot_token or not chat_id:
            raise DeliveryError("TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID are required")
        self.bot_token = bot_token
        self.chat_id = chat_id
        self.post = post

    def send(self, issue: NewsIssue) -> DeliveryResult:
        url = "https://api.telegram.org/bot%s/sendMessage" % self.bot_token
        for chunk in split_text(render_markdown(issue)):
            result = self.post(
                url,
                {
                    "chat_id": self.chat_id,
                    "text": chunk,
                    "disable_web_page_preview": True,
                },
            )
            if result.get("ok") is False:
                raise DeliveryError("Telegram rejected the message")
        return DeliveryResult(channel="telegram", delivered=True)

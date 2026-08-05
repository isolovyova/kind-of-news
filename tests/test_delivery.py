import base64
import json
import unittest
from email import policy
from email.parser import BytesParser
from pathlib import Path

from runner.delivery.base import DeliveryError
from runner.delivery.gmail import GmailDelivery
from runner.delivery.telegram import TelegramDelivery
from runner.delivery.webhook import WebhookDelivery
from runner.models import NewsIssue


FIXTURE = Path(__file__).parent / "fixtures" / "valid_issue.json"


class DeliveryTests(unittest.TestCase):
    def setUp(self):
        self.issue = NewsIssue.from_mapping(json.loads(FIXTURE.read_text(encoding="utf-8")))

    def test_telegram_posts_to_bot_endpoint_without_logging_secret(self):
        calls = []

        def fake_post(url, payload, **kwargs):
            calls.append((url, payload))
            return {"ok": True}

        TelegramDelivery("secret-token", "123", post=fake_post).send(self.issue)
        self.assertEqual(len(calls), 1)
        self.assertIn("secret-token", calls[0][0])
        self.assertEqual(calls[0][1]["chat_id"], "123")

    def test_webhook_uses_provider_shape(self):
        calls = []

        def fake_post(url, payload, **kwargs):
            calls.append(payload)
            return {}

        WebhookDelivery("https://example.com/hook", "discord", post_json_fn=fake_post).send(self.issue)
        self.assertEqual(len(calls), 1)
        self.assertIn("content", calls[0])

    def test_gmail_refreshes_and_sends_raw_message(self):
        exchange_calls = []
        send_calls = []

        def fake_exchange(url, values):
            exchange_calls.append((url, values))
            return {"access_token": "access"}

        def fake_send(url, token, payload):
            send_calls.append((url, token, payload))
            return {"id": "message-id"}

        GmailDelivery(
            "client",
            "secret",
            "refresh",
            "reader@example.com",
            token_exchange=fake_exchange,
            send_request=fake_send,
        ).send(self.issue)
        self.assertEqual(exchange_calls[0][1]["grant_type"], "refresh_token")
        self.assertEqual(send_calls[0][1], "access")
        self.assertIn("raw", send_calls[0][2])
        message = BytesParser(policy=policy.default).parsebytes(
            base64.urlsafe_b64decode(send_calls[0][2]["raw"])
        )
        self.assertEqual(message.get_content_type(), "multipart/alternative")
        self.assertEqual(
            [part.get_content_type() for part in message.iter_parts()],
            ["text/plain", "text/html"],
        )
        self.assertNotIn("text/markdown", message.as_string().lower())
        self.assertIsNone(message.get("Content-Disposition"))
        self.assertTrue(
            all(part.get("Content-Disposition") is None for part in message.iter_parts())
        )
        self.assertIsNone(message["From"])
        body = message.get_body(preferencelist=("plain",)).get_content()
        html_body = message.get_body(preferencelist=("html",)).get_content()
        self.assertIn(
            "[1] [Example source](https://example.com/kind-of-news/good-thing)",
            body,
        )
        self.assertIn(
            '<a href="https://example.com/kind-of-news/good-thing">Example source</a>',
            html_body,
        )
        self.assertIn("<h2>☀️ Good thing</h2>", html_body)
        self.assertIn("<h2>Sources</h2>", html_body)
        self.assertNotIn("Full links (for verification, remove before publishing)", body)
        self.assertNotIn("\n—\nSources:", body)

    def test_gmail_adds_configured_verified_alias_as_from_header(self):
        send_calls = []

        def fake_exchange(url, values):
            return {"access_token": "access"}

        def fake_send(url, token, payload):
            send_calls.append(payload)
            return {"id": "message-id"}

        GmailDelivery(
            "client",
            "secret",
            "refresh",
            "reader@example.com",
            token_exchange=fake_exchange,
            send_request=fake_send,
            sender="newsishletter@gmail.com",
        ).send(self.issue)

        message = BytesParser(policy=policy.default).parsebytes(
            base64.urlsafe_b64decode(send_calls[0]["raw"])
        )
        self.assertEqual(message["From"], "newsishletter@gmail.com")
        self.assertEqual(message["To"], "reader@example.com")

    def test_gmail_rejects_unvalidated_sender_address_before_send(self):
        with self.assertRaises(DeliveryError):
            GmailDelivery(
                "client",
                "secret",
                "refresh",
                "reader@example.com",
                sender="Newsishletter <newsishletter@gmail.com>",
            )


if __name__ == "__main__":
    unittest.main()

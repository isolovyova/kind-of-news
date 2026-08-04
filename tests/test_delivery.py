import json
import unittest
from pathlib import Path

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


if __name__ == "__main__":
    unittest.main()

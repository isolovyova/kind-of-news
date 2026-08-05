import base64
import json
import unittest
from email import policy
from email.parser import BytesParser
from pathlib import Path
from unittest.mock import patch

from runner.delivery.base import DeliveryError
from runner.delivery.buttondown import ButtondownDelivery, EMAILS_URL, _post_buttondown
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

    def test_buttondown_publishes_safe_html_with_source_links(self):
        calls = []

        def fake_publish(url, api_key, payload):
            calls.append((url, api_key, payload))
            return {"id": "em_test", "status": "about_to_send"}

        result = ButtondownDelivery("buttondown-secret", publish_request=fake_publish).send(self.issue)

        self.assertEqual(result.channel, "buttondown")
        self.assertTrue(result.delivered)
        self.assertEqual(calls[0][0], EMAILS_URL)
        self.assertEqual(calls[0][1], "buttondown-secret")
        self.assertEqual(calls[0][2]["subject"], "Kind of News #2026-08-03")
        self.assertTrue(calls[0][2]["body"].startswith("<!-- buttondown-editor-mode: fancy -->"))
        for heading in ("☀️ Good thing", "📅 On this day", "🧠 Tiny fact", "🌱 Thought for the day"):
            self.assertIn(heading, calls[0][2]["body"])
        self.assertIn(
            '<a href="https://example.com/kind-of-news/good-thing">Example source</a>',
            calls[0][2]["body"],
        )
        self.assertNotIn("buttondown-secret", json.dumps(calls[0][2]))
        self.assertEqual(calls[0][2]["status"], "about_to_send")

    def test_buttondown_rejects_a_draft_response_as_false_success(self):
        calls = []

        def fake_publish(url, api_key, payload):
            calls.append(payload)
            return {"id": "em_draft", "status": "draft"}

        with self.assertRaises(DeliveryError):
            ButtondownDelivery("buttondown-secret", publish_request=fake_publish).send(self.issue)

        self.assertEqual(len(calls), 1)

    def test_buttondown_transport_failure_is_not_reported_as_success(self):
        def fake_publish(url, api_key, payload):
            raise TimeoutError("simulated network failure")

        with self.assertRaises(DeliveryError):
            ButtondownDelivery("buttondown-secret", publish_request=fake_publish).send(self.issue)

    def test_buttondown_does_not_publish_an_invalid_issue(self):
        raw = self.issue.to_dict()
        raw["sources"] = raw["sources"][:2]
        invalid_issue = NewsIssue.from_mapping(raw)
        calls = []

        def fake_publish(url, api_key, payload):
            calls.append(payload)
            return {"id": "should-not-exist", "status": "about_to_send"}

        with self.assertRaises(DeliveryError):
            ButtondownDelivery("buttondown-secret", publish_request=fake_publish).send(invalid_issue)

        self.assertEqual(calls, [])

    def test_buttondown_requires_secret_without_exposing_it_in_config(self):
        with self.assertRaises(DeliveryError):
            ButtondownDelivery("")

    def test_buttondown_http_request_uses_token_header_and_json_body(self):
        response = type("Response", (), {"read": lambda self: b'{"id":"em_test","status":"sent"}'})()
        with patch("runner.delivery.buttondown.urlopen") as urlopen:
            urlopen.return_value.__enter__.return_value = response
            result = _post_buttondown(EMAILS_URL, "buttondown-secret", {"subject": "test"})

        request = urlopen.call_args.args[0]
        self.assertEqual(request.get_header("Authorization"), "Token buttondown-secret")
        self.assertEqual(request.get_header("Content-type"), "application/json")
        self.assertEqual(request.get_header("X-buttondown-live-dangerously"), "true")
        self.assertEqual(json.loads(request.data.decode("utf-8")), {"subject": "test"})
        self.assertEqual(result["status"], "sent")

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

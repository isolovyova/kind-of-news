import json
import unittest
from pathlib import Path
from unittest.mock import patch

from runner.delivery.base import DeliveryError
from runner.delivery.buttondown import ButtondownDelivery, EMAILS_URL, _post_buttondown
from runner.models import NewsIssue


FIXTURE = Path(__file__).parent / "fixtures" / "valid_issue.json"


class DeliveryTests(unittest.TestCase):
    def setUp(self):
        self.issue = NewsIssue.from_mapping(json.loads(FIXTURE.read_text(encoding="utf-8")))

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
        body = calls[0][2]["body"]
        self.assertTrue(body.startswith("<!-- buttondown-editor-mode: fancy -->"))
        for heading in ("☀️ Good thing", "📅 On this day", "🧠 Tiny fact", "🌱 Thought for the day"):
            self.assertIn(heading, body)
        self.assertNotIn("<h1>Kind of News #2026-08-03</h1>", body)
        self.assertNotIn("Kind of News — sent with love and verified links.", body)
        self.assertIn("<p>Sent with love and verified links.</p>", body)
        self.assertIn(
            '<a href="https://example.com/kind-of-news/good-thing">Example source</a>',
            body,
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


if __name__ == "__main__":
    unittest.main()

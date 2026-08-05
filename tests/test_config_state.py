import json
import tempfile
import unittest
from pathlib import Path

from runner.app import _make_delivery
from runner.config import DEFAULT_MODEL, DeliveryConfig, AppConfig, load_config, missing_secret_names
from runner.models import NewsIssue
from runner.state import StateStore


class ConfigAndStateTests(unittest.TestCase):
    def test_empty_model_environment_falls_back_to_config(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "config.yml"
            path.write_text(
                "model: custom-model\ndelivery:\n  channels: [telegram]\n",
                encoding="utf-8",
            )
            config = load_config(str(path))
            self.assertEqual(config.model, "custom-model")

    def test_default_model_is_available(self):
        self.assertTrue(DEFAULT_MODEL)

    def test_secret_names_follow_selected_channels(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "config.yml"
            path.write_text("delivery:\n  channels: [webhook]\n", encoding="utf-8")
            config = load_config(str(path))
            self.assertEqual(missing_secret_names(config, {}), ["OPENAI_API_KEY", "WEBHOOK_URL"])

    def test_buttondown_secret_is_required_only_from_secure_environment(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "config.yml"
            path.write_text("delivery:\n  channels: [buttondown]\n", encoding="utf-8")
            config = load_config(str(path))
            self.assertEqual(
                missing_secret_names(config, {}),
                ["OPENAI_API_KEY", "BUTTONDOWN_API_KEY"],
            )
            self.assertEqual(
                missing_secret_names(
                    config,
                    {"OPENAI_API_KEY": "openai", "BUTTONDOWN_API_KEY": "buttondown"},
                ),
                [],
            )

    def test_buttondown_delivery_reads_api_key_from_environment(self):
        config = AppConfig(delivery=DeliveryConfig(channels=["buttondown"]))
        delivery = _make_delivery("buttondown", config, {"BUTTONDOWN_API_KEY": "buttondown-secret"})
        self.assertEqual(delivery._api_key, "buttondown-secret")

    def test_optional_gmail_from_is_passed_as_non_secret_delivery_setting(self):
        config = AppConfig(delivery=DeliveryConfig(channels=["gmail"]))
        delivery = _make_delivery(
            "gmail",
            config,
            {
                "GMAIL_CLIENT_ID": "client",
                "GMAIL_CLIENT_SECRET": "secret",
                "GMAIL_REFRESH_TOKEN": "refresh",
                "GMAIL_TO": "reader@example.com",
                "GMAIL_FROM": "newsishletter@gmail.com",
            },
        )
        self.assertEqual(delivery.sender, "newsishletter@gmail.com")

    def test_state_persists_issue_and_channel_markers(self):
        raw = json.loads(
            (Path(__file__).parent / "fixtures" / "valid_issue.json").read_text(encoding="utf-8")
        )
        issue = NewsIssue.from_mapping(raw)
        with tempfile.TemporaryDirectory() as directory:
            state = StateStore(directory, issue.issue_id)
            self.assertIsNone(state.load_issue())
            self.assertEqual(state.sent_channels(), set())
            state.save_issue(issue)
            state.mark_sent("telegram")
            self.assertEqual(state.load_issue(), issue)
            self.assertEqual(state.sent_channels(), {"telegram"})


if __name__ == "__main__":
    unittest.main()

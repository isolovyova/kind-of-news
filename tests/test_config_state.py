import json
import tempfile
import unittest
from pathlib import Path

from runner.app import _make_delivery, run
from runner.config import ConfigError, DEFAULT_MODEL, DeliveryConfig, AppConfig, load_config, missing_secret_names
from runner.models import NewsIssue
from runner.state import StateStore


class ConfigAndStateTests(unittest.TestCase):
    def test_empty_model_environment_falls_back_to_config(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "config.yml"
            path.write_text(
                "model: custom-model\ndelivery:\n  channels: [buttondown]\n",
                encoding="utf-8",
            )
            config = load_config(str(path))
            self.assertEqual(config.model, "custom-model")

    def test_default_model_is_available(self):
        self.assertTrue(DEFAULT_MODEL)

    def test_only_buttondown_delivery_is_accepted(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "config.yml"
            path.write_text("delivery:\n  channels: [gmail]\n", encoding="utf-8")
            with self.assertRaises(ConfigError):
                load_config(str(path))

    def test_obsolete_webhook_configuration_is_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "config.yml"
            path.write_text(
                "delivery:\n  channels: [buttondown]\n  webhook_provider: generic\n",
                encoding="utf-8",
            )
            with self.assertRaises(ConfigError):
                load_config(str(path))

    def test_only_openai_and_buttondown_secrets_are_required(self):
        config = AppConfig(delivery=DeliveryConfig(channels=["buttondown"]))
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

    def test_buttondown_delivery_reads_api_key_from_secure_environment(self):
        config = AppConfig(delivery=DeliveryConfig(channels=["buttondown"]))
        delivery = _make_delivery("buttondown", config, {"BUTTONDOWN_API_KEY": "buttondown-secret"})
        self.assertEqual(delivery._api_key, "buttondown-secret")

    def test_state_persists_issue_and_buttondown_marker(self):
        raw = json.loads(
            (Path(__file__).parent / "fixtures" / "valid_issue.json").read_text(encoding="utf-8")
        )
        issue = NewsIssue.from_mapping(raw)
        with tempfile.TemporaryDirectory() as directory:
            state = StateStore(directory, issue.issue_id)
            self.assertIsNone(state.load_issue())
            self.assertEqual(state.sent_channels(), set())
            state.save_issue(issue)
            state.mark_sent("buttondown")
            self.assertEqual(state.load_issue(), issue)
            self.assertEqual(state.sent_channels(), {"buttondown"})

    def test_duplicate_issue_id_skips_a_second_publish(self):
        raw = json.loads(
            (Path(__file__).parent / "fixtures" / "valid_issue.json").read_text(encoding="utf-8")
        )
        issue = NewsIssue.from_mapping(raw)
        with tempfile.TemporaryDirectory() as directory:
            state = StateStore(directory, issue.issue_id)
            state.save_issue(issue)
            state.mark_sent("buttondown")
            self.assertEqual(
                run(
                    config_path="config.yml",
                    requested_date=issue.issue_id,
                    state_dir=directory,
                    environ={"BUTTONDOWN_API_KEY": "not-used"},
                ),
                0,
            )


if __name__ == "__main__":
    unittest.main()
sed: --: No such file or directory

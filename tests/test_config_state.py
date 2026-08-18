import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

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

    def test_retired_delivery_channels_are_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "config.yml"
            path.write_text("delivery:\n  channels: [gmail]\n", encoding="utf-8")
            with self.assertRaises(ConfigError):
                load_config(str(path))

    def test_buttondown_and_site_can_be_configured_together(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "config.yml"
            path.write_text("delivery:\n  channels: [buttondown, site]\n", encoding="utf-8")
            self.assertEqual(load_config(str(path)).delivery.channels, ["buttondown", "site"])

    def test_empty_and_repeated_channel_lists_are_rejected(self):
        for body in ("delivery:\n  channels: []\n", "delivery:\n  channels: [site, site]\n"):
            with tempfile.TemporaryDirectory() as directory:
                path = Path(directory) / "config.yml"
                path.write_text(body, encoding="utf-8")
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

    def test_the_site_channel_needs_no_credential_of_its_own(self):
        config = AppConfig(delivery=DeliveryConfig(channels=["site"]))
        self.assertEqual(missing_secret_names(config, {}), ["OPENAI_API_KEY"])
        self.assertEqual(missing_secret_names(config, {"OPENAI_API_KEY": "openai"}), [])

    def test_buttondown_delivery_reads_api_key_from_secure_environment(self):
        config = AppConfig(delivery=DeliveryConfig(channels=["buttondown"]))
        delivery = _make_delivery("buttondown", config, {"BUTTONDOWN_API_KEY": "buttondown-secret"})
        self.assertEqual(delivery._api_key, "buttondown-secret")

    def test_site_delivery_targets_the_requested_docs_directory(self):
        config = AppConfig(delivery=DeliveryConfig(channels=["site"]))
        delivery = _make_delivery("site", config, {}, "build/docs")
        self.assertEqual(delivery.issues_dir, Path("build/docs") / "issues")

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
            for channel in load_config("config.yml").delivery.channels:
                state.mark_sent(channel)
            self.assertEqual(
                run(
                    config_path="config.yml",
                    requested_date=issue.issue_id,
                    state_dir=directory,
                    environ={"BUTTONDOWN_API_KEY": "not-used"},
                ),
                0,
            )

    def test_site_only_publishes_without_constructing_buttondown(self):
        raw = json.loads(
            (Path(__file__).parent / "fixtures" / "valid_issue.json").read_text(encoding="utf-8")
        )
        issue_id = "2026-08-18"
        raw["issue_id"] = issue_id
        with tempfile.TemporaryDirectory() as directory:
            fixture = Path(directory) / "issue.json"
            fixture.write_text(json.dumps(raw), encoding="utf-8")
            docs_dir = Path(directory) / "docs"
            with patch("runner.app.ButtondownDelivery") as buttondown:
                self.assertEqual(
                    run(
                        config_path="config.yml",
                        requested_date=issue_id,
                        state_dir=str(Path(directory) / "state"),
                        docs_dir=str(docs_dir),
                        site_only=True,
                        fixture_path=str(fixture),
                        environ={},
                    ),
                    0,
                )
                buttondown.assert_not_called()

            self.assertTrue((docs_dir / "issues" / (issue_id + ".json")).is_file())
            self.assertTrue((docs_dir / "issues" / "latest.json").is_file())
            self.assertEqual(
                StateStore(str(Path(directory) / "state"), issue_id).sent_channels(),
                {"site"},
            )


if __name__ == "__main__":
    unittest.main()

import json
import unittest
from pathlib import Path

from runner.models import NewsIssue
from runner.render import render_html, render_markdown, split_text, webhook_payload


FIXTURE = Path(__file__).parent / "fixtures" / "valid_issue.json"


class RenderTests(unittest.TestCase):
    def setUp(self):
        self.issue = NewsIssue.from_mapping(json.loads(FIXTURE.read_text(encoding="utf-8")))

    def test_renders_universal_intro_and_four_blocks(self):
        rendered = render_markdown(self.issue)
        self.assertIn("Kind of News #2026-08-03", rendered)
        self.assertIn("The world is noisy.", rendered)
        self.assertIn("☀️ Good thing", rendered)
        self.assertIn("📅 On this day", rendered)
        self.assertIn("🧠 Tiny fact", rendered)
        self.assertIn("🌱 Thought for the day", rendered)
        self.assertIn(
            "[1] [Example source](https://example.com/kind-of-news/good-thing) — synthetic good-news fixture",
            rendered,
        )
        self.assertIn(
            "[2] [Example archive](https://example.com/kind-of-news/on-this-day) — synthetic historical fixture",
            rendered,
        )
        self.assertIn(
            "[3] [Example reference](https://example.com/kind-of-news/tiny-fact) — synthetic fact fixture",
            rendered,
        )
        self.assertNotIn("Full links (for verification, remove before publishing)", rendered)
        self.assertNotIn("\n—\nSources:", rendered)
        for source_url in (
            "https://example.com/kind-of-news/good-thing",
            "https://example.com/kind-of-news/on-this-day",
            "https://example.com/kind-of-news/tiny-fact",
        ):
            self.assertEqual(rendered.count(source_url), 1)
        self.assertNotIn("TOP LINE", rendered)

    def test_telegram_split_respects_limit(self):
        chunks = split_text("x" * 9000, limit=4096)
        self.assertTrue(all(len(chunk) <= 4096 for chunk in chunks))
        self.assertEqual("".join(chunks), "x" * 9000)

    def test_webhook_presets(self):
        self.assertIn("text", webhook_payload(self.issue, "slack"))
        self.assertIn("content", webhook_payload(self.issue, "discord"))
        self.assertEqual(webhook_payload(self.issue, "ntfy")["title"], "Kind of News #2026-08-03")

    def test_html_renderer_escapes_issue_text_and_keeps_https_links(self):
        raw = self.issue.to_dict()
        raw["good_thing"] = "A <b>small</b> win."
        raw["sources"][0]["name"] = "Example <source>"
        issue = NewsIssue.from_mapping(raw)

        rendered = render_html(issue)

        self.assertIn("A &lt;b&gt;small&lt;/b&gt; win.", rendered)
        self.assertNotIn("<b>small</b>", rendered)
        self.assertIn(
            '<a href="https://example.com/kind-of-news/good-thing">Example &lt;source&gt;</a>',
            rendered,
        )


if __name__ == "__main__":
    unittest.main()

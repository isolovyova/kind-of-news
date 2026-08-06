import re
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
TEMPLATE = ROOT / "templates" / "buttondown-welcome-issue.md"
HANDOFF = ROOT / "docs" / "buttondown-welcome-issue.md"

EXPECTED_HEADINGS = [
    "## ☀️ Good thing",
    "## 📅 On this day",
    "## 🧠 Tiny fact",
    "## 🌱 Thought for the day",
]
EXPECTED_SOURCE_URLS = [
    "https://www.ala.org/aboutala/1833",
    "https://www.nasa.gov/history/55-years-ago-one-month-until-the-moon-landing/",
    "https://www.fisheries.noaa.gov/feature-story/celebrate-holidays-our-ink-blot-and-stumpy-paper-snowflakes",
]


def welcome_body() -> str:
    content = TEMPLATE.read_text(encoding="utf-8")
    return content.split("---\n", 1)[1].strip()


class WelcomeIssueTests(unittest.TestCase):
    def test_welcome_issue_has_four_blocks_and_one_source_link_per_fact(self):
        template = TEMPLATE.read_text(encoding="utf-8")
        body = welcome_body()

        self.assertIn("Subject: Welcome to Kind of News", template)
        headings = [line for line in body.splitlines() if line.startswith("## ")]
        self.assertEqual(headings, EXPECTED_HEADINGS)

        source_lines = [
            line for line in body.splitlines() if re.match(r"^\[\d+\] \[[^]]+\]\(https://", line)
        ]
        self.assertEqual(len(source_lines), 3)
        self.assertEqual([f"[{index}]" in source_lines[index - 1] for index in range(1, 4)], [True] * 3)
        for source_url in EXPECTED_SOURCE_URLS:
            self.assertEqual(body.count(source_url), 1)
        self.assertEqual(body.count("https://"), 3)

        self.assertIn("Sources:", body)
        self.assertIn("Sent with love and verified links.", body)
        self.assertNotIn("Kind of News #", body)
        self.assertNotIn("—", body)

    def test_welcome_issue_is_evergreen_not_a_latest_news_claim(self):
        body = welcome_body().lower()

        for time_sensitive_phrase in ("latest", "current", "today", "right now", "this week"):
            self.assertNotIn(time_sensitive_phrase, body)

    def test_handoff_describes_one_immediate_subscriber_mechanism(self):
        handoff = HANDOFF.read_text(encoding="utf-8")
        normalized = " ".join(handoff.split()).lower()

        self.assertIn("templates/buttondown-welcome-issue.md", handoff)
        self.assertIn("private codex", normalized)
        self.assertIn("subscriber.confirmed", handoff)
        self.assertIn("buttondown standard", normalized)
        self.assertIn("choose exactly one", normalized)
        self.assertIn("do not enable both", normalized)
        self.assertIn("not a broadcast", normalized)
        self.assertIn("existing confirmed subscribers", normalized)
        self.assertIn("new test email address", normalized)
        self.assertIn("m/w/f", normalized)
        self.assertIn("subsequent issues only", normalized)
        self.assertIn("remains paused", normalized)

    def test_public_reader_copy_does_not_claim_welcome_is_active(self):
        readme = (ROOT / "README.md").read_text(encoding="utf-8")
        normalized = " ".join(readme.split()).lower()

        self.assertIn("subscribe to kind of news on buttondown", normalized)
        self.assertIn("evergreen welcome issue", normalized)
        self.assertIn("not active yet", normalized)
        self.assertIn("recurring delivery is currently paused", normalized)


if __name__ == "__main__":
    unittest.main()

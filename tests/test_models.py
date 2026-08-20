import json
import unittest
from pathlib import Path

from runner.models import IssueFormatError, NewsIssue


FIXTURE = Path(__file__).parent / "fixtures" / "valid_issue.json"


class ModelTests(unittest.TestCase):
    def test_fixture_round_trips(self):
        raw = json.loads(FIXTURE.read_text(encoding="utf-8"))
        issue = NewsIssue.from_mapping(raw)
        self.assertEqual(issue.issue_id, "2026-08-03")
        self.assertEqual(issue.to_dict(), raw)

    def test_missing_fields_fail_closed(self):
        with self.assertRaises(IssueFormatError):
            NewsIssue.from_mapping({"issue_id": "2026-08-03"})


    def test_repeated_block_leads_are_removed(self):
        raw = json.loads(FIXTURE.read_text(encoding="utf-8"))
        raw.update(
            {
                "good_thing": "☀️ Good thing\n(Test City): A small win.",
                "current_or_history": "📅 On this day\nA date-specific detail.",
                "tiny_fact": "🧠 Tiny fact\nA curious detail.",
                "thought": "🌱 Thought for the day\nA gentle sentence.",
            }
        )

        issue = NewsIssue.from_mapping(raw)

        self.assertEqual(issue.good_thing, "(Test City): A small win.")
        self.assertEqual(issue.current_or_history, "A date-specific detail.")
        self.assertEqual(issue.tiny_fact, "A curious detail.")
        self.assertEqual(issue.thought, "A gentle sentence.")


if __name__ == "__main__":
    unittest.main()

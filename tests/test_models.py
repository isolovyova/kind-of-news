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


if __name__ == "__main__":
    unittest.main()

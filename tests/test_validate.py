import json
import unittest
from pathlib import Path

from runner.models import NewsIssue
from runner.validate import IssueValidationError, validate_issue


FIXTURE = Path(__file__).parent / "fixtures" / "valid_issue.json"


class ValidationTests(unittest.TestCase):
    def setUp(self):
        self.raw = json.loads(FIXTURE.read_text(encoding="utf-8"))

    def test_valid_issue_passes(self):
        validate_issue(NewsIssue.from_mapping(self.raw), expected_date="2026-08-03")

    def test_wrong_date_fails(self):
        issue = NewsIssue.from_mapping(self.raw)
        with self.assertRaises(IssueValidationError):
            validate_issue(issue, expected_date="2026-08-04")

    def test_missing_source_fails(self):
        raw = dict(self.raw)
        raw["sources"] = raw["sources"][:2]
        with self.assertRaises(IssueValidationError):
            validate_issue(NewsIssue.from_mapping(raw), expected_date="2026-08-03")

    def test_em_dash_in_prose_fails(self):
        raw = dict(self.raw)
        raw["thought"] = "A thought — with a prose dash."
        with self.assertRaises(IssueValidationError):
            validate_issue(NewsIssue.from_mapping(raw), expected_date="2026-08-03")

    def test_citation_mismatch_fails(self):
        issue = NewsIssue.from_mapping(self.raw)
        with self.assertRaises(IssueValidationError):
            validate_issue(issue, expected_date="2026-08-03", citation_urls={"https://example.com/other"})


if __name__ == "__main__":
    unittest.main()

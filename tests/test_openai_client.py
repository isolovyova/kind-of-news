sed: --: No such file or directory
import json
import unittest
from pathlib import Path

from runner.openai_client import ResponsesClient, extract_citation_urls, parse_json_response


FIXTURE = Path(__file__).parent / "fixtures" / "valid_issue.json"


class ResponseHelpersTests(unittest.TestCase):
    def test_extracts_urls_from_nested_annotations_and_sources(self):
        response = {
            "output": [
                {"content": [{"annotations": [{"url": "https://example.com/a"}]}]},
                {"action": {"sources": [{"url": "https://example.com/b"}]}},
            ]
        }
        self.assertEqual(
            extract_citation_urls(response),
            {"https://example.com/a", "https://example.com/b"},
        )

    def test_parses_json_fenced_in_text(self):
        value = parse_json_response({"output_text": "```json\n{\"ok\": true}\n```"})
        self.assertEqual(value, {"ok": True})

    def test_two_stage_client_uses_search_then_compose(self):
        issue = json.loads(FIXTURE.read_text(encoding="utf-8"))
        research = {
            "good_thing": {
                "notes": "Synthetic evidence.",
                "sources": [issue["sources"][0]],
            },
            "current_or_history": {
                "notes": "Synthetic evidence.",
                "sources": [issue["sources"][1]],
            },
            "tiny_fact": {
                "notes": "Synthetic evidence.",
                "sources": [issue["sources"][2]],
            },
        }

        class FakeResponses:
            def __init__(self):
                self.calls = []
                self.responses = [
                    {
                        "output_text": json.dumps(research),
                        "output": [{"action": {"sources": issue["sources"]}}],
                    },
                    {"output_text": json.dumps(issue)},
                ]

            def create(self, **kwargs):
                self.calls.append(kwargs)
                return self.responses.pop(0)

        class FakeSDK:
            def __init__(self):
                self.responses = FakeResponses()

        sdk = FakeSDK()
        generated, urls = ResponsesClient("key", "test-model", sdk_client=sdk).generate_issue(
            "Editorial policy", "2026-08-03", "Monday"
        )
        self.assertEqual(generated.issue_id, "2026-08-03")
        self.assertEqual(len(sdk.responses.calls), 2)
        self.assertEqual(sdk.responses.calls[0]["tools"], [{"type": "web_search"}])
        self.assertNotIn("tools", sdk.responses.calls[1])
        self.assertFalse(sdk.responses.calls[0]["store"])
        self.assertEqual(len(urls), 3)


if __name__ == "__main__":
    unittest.main()

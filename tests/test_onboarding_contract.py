import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]

APPROVED_WELCOME = """Welcome to Kind of News.

I made this because I got tired of opening the news and feeling worse, while still wanting to know what was going on in the world.

I wanted a small, useful dose of things that are interesting, strange, hopeful, or worth learning. So, three times a week, Kind of News brings you one good thing, one curiosity, one tiny fact, and a thought to leave you a little less clenched.

The name is a small nod to kindness. The news can be serious without being cruel to your nervous system.

Where would you like to receive it: Gmail, Telegram, Slack, Discord, ntfy, or another connected channel?"""


class OnboardingContractTests(unittest.TestCase):
    def test_setup_skill_is_a_real_entrypoint(self):
        content = (ROOT / "skills" / "kind-of-news-setup" / "SKILL.md").read_text(
            encoding="utf-8"
        )
        normalized = " ".join(content.split())
        self.assertIn("do not stop at “installed”", normalized)
        self.assertIn("Where would you like to receive it", content)
        self.assertIn("If the user explicitly asks for a “dry run” or “preview only”", content)
        self.assertIn("Ready to start Kind of News?", content)
        self.assertIn("I’ll send your first issue now", content)
        self.assertIn("every [days] at [time] in [timezone] to [channel]", normalized)
        self.assertIn("schedule controls only later issues", normalized)
        self.assertIn("even when today is not", normalized)
        self.assertIn("both schedule activation and the immediate send", normalized)
        self.assertIn("Check your email for Kind of News #YYYY-MM-DD", content)
        self.assertIn("Name the next scheduled delivery", normalized)
        first_response = content.split("```text", 2)[1].split("```", 1)[0].strip()
        self.assertEqual(first_response, APPROVED_WELCOME)
        self.assertEqual(first_response.count("?"), 1)
        self.assertIn("Do not ask about timezone, credentials, or scheduling", content)
        self.assertIn("Do not surface a preview or dry-run choice by default", normalized)
        self.assertIn("preview option is opt-in", normalized)
        self.assertNotIn("regular delivery stays off until you confirm", normalized)
        self.assertNotIn("The test issue was sent successfully", content)
        self.assertNotIn("ask separately", normalized)

    def test_codex_plugin_exposes_setup_and_editorial_skills(self):
        manifest = json.loads(
            (ROOT / ".codex-plugin" / "plugin.json").read_text(encoding="utf-8")
        )
        self.assertEqual(manifest["name"], "kind-of-news")
        self.assertEqual(manifest["skills"], "./skills/")
        self.assertIn("Start the Kind of News setup tutorial", manifest["interface"]["defaultPrompt"])
        self.assertTrue((ROOT / "skills" / "kind-of-news" / "SKILL.md").is_file())
        self.assertTrue((ROOT / "skills" / "kind-of-news-setup" / "SKILL.md").is_file())

    def test_public_onboarding_prompt_does_not_route_to_user_repository(self):
        readme = (ROOT / "README.md").read_text(encoding="utf-8")
        prompt = readme.split("```text", 2)[1]
        self.assertIn("## Start in Codex or Claude Code", readme)
        self.assertIn("### What happens next", readme)
        self.assertIn("## Optional: self-managed GitHub Actions", readme)
        self.assertIn("docs/github-actions-setup.md", readme)
        self.assertLess(
            readme.index("### What happens next"),
            readme.index("## Optional: self-managed GitHub Actions"),
        )
        self.assertNotIn("## Where the schedule lives", readme)
        self.assertNotIn("## Advanced Actions secrets", readme)
        self.assertIn("immediately start its setup tutorial", prompt)
        self.assertIn("Do not ask me to create a GitHub repository", prompt)
        self.assertIn("Use the approved Kind of News welcome from the setup skill exactly", prompt)
        self.assertIn("Ready to start Kind of News?", prompt)
        self.assertIn("I’ll send your first issue now", prompt)
        self.assertIn("activate recurring delivery for subsequent issues", prompt)
        self.assertIn("send issue #1 immediately", prompt)
        self.assertIn("If I explicitly ask for a preview or dry run, send and schedule nothing", prompt)
        self.assertNotIn("send exactly one test issue", prompt)
        self.assertNotIn("ask separately about automatic delivery", prompt)

    def test_repo_runner_preview_is_explicitly_advanced(self):
        runner = (ROOT / "runner" / "app.py").read_text(encoding="utf-8")
        workflow = (ROOT / ".github" / "workflows" / "kind-of-news.yml").read_text(
            encoding="utf-8"
        )
        advanced = (ROOT / "docs" / "github-actions-setup.md").read_text(
            encoding="utf-8"
        )
        self.assertIn("Advanced repo-runner preview", runner)
        self.assertIn("Advanced repo-runner mode", workflow)
        self.assertIn("This preview intentionally sends nothing", advanced)
        self.assertIn("different from the normal guided setup", advanced)


if __name__ == "__main__":
    unittest.main()

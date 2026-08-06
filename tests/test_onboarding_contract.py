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
        self.assertIn("optional delivery", manifest["description"])
        self.assertIn("currently paused", manifest["interface"]["longDescription"])
        self.assertTrue((ROOT / "skills" / "kind-of-news" / "SKILL.md").is_file())
        self.assertTrue((ROOT / "skills" / "kind-of-news-setup" / "SKILL.md").is_file())

    def test_claude_marketplace_exposes_both_skills_from_a_valid_plugin_root(self):
        marketplace = json.loads(
            (ROOT / ".claude-plugin" / "marketplace.json").read_text(encoding="utf-8")
        )
        plugin = marketplace["plugins"][0]
        self.assertEqual(plugin["name"], "kind-of-news")
        self.assertEqual(plugin["source"]["source"], "git-subdir")
        self.assertEqual(plugin["source"]["path"], "skills")
        self.assertEqual(plugin["version"], "1.1.1")

        manifest = json.loads(
            (ROOT / "skills" / ".claude-plugin" / "plugin.json").read_text(encoding="utf-8")
        )
        self.assertEqual(manifest["name"], "kind-of-news")
        self.assertEqual(manifest["version"], "1.1.1")
        self.assertEqual(manifest["skills"], "./")
        self.assertTrue((ROOT / "skills" / "kind-of-news" / "SKILL.md").is_file())
        self.assertTrue((ROOT / "skills" / "kind-of-news-setup" / "SKILL.md").is_file())

        setup_docs = (ROOT / "docs" / "codex-cowork-setup.md").read_text(encoding="utf-8")
        self.assertIn(
            "/plugin marketplace add https://github.com/isolovyova/kind-of-news.git",
            setup_docs,
        )
        self.assertIn("/plugin install kind-of-news@kind-of-news --scope user", setup_docs)
        self.assertIn("/kind-of-news:kind-of-news-setup", setup_docs)

    def test_public_readme_separates_reader_creator_and_author_paths(self):
        readme = (ROOT / "README.md").read_text(encoding="utf-8")
        prompt = readme.split("```text", 2)[1].split("```", 1)[0].strip()
        self.assertIn("## Subscribe to Kind of News newsletter", readme)
        self.assertIn("https://buttondown.com/kindofnews", readme)
        self.assertIn("## Start in Codex or Claude Code", readme)
        self.assertIn("Want your own private digest in a connected channel", readme)
        self.assertIn("You do not need to create or fork a GitHub repository", readme)
        self.assertIn("## How it works", readme)
        self.assertIn("docs/github-actions-setup.md", readme)
        self.assertIn("after final verification", readme)
        self.assertIn("recurring delivery is currently paused", readme.lower())
        self.assertEqual(
            prompt,
            "Install Kind of News from https://github.com/isolovyova/kind-of-news and start the setup tutorial.",
        )
        self.assertNotIn("### What happens next", readme)
        self.assertNotIn("## Optional: self-managed GitHub Actions", readme)

    def test_branded_newsletter_path_is_distinct_and_author_controlled(self):
        setup = (ROOT / "skills" / "kind-of-news-setup" / "SKILL.md").read_text(encoding="utf-8")
        editorial = (ROOT / "skills" / "kind-of-news" / "SKILL.md").read_text(encoding="utf-8")
        assistant = (ROOT / "docs" / "assistant-setup.md").read_text(encoding="utf-8")
        actions = (ROOT / "docs" / "github-actions-setup.md").read_text(encoding="utf-8")
        for content in (setup, editorial, assistant, actions):
            self.assertIn("https://buttondown.com/kindofnews", content)
            self.assertIn("BUTTONDOWN_API_KEY", content)
            self.assertIn("subscriber", content.lower())
        self.assertIn("one author-controlled recurring schedule", assistant)
        self.assertIn("does not create a manual draft", actions)
        self.assertIn("does not use a personal Gmail sender", actions)
        config_example = (ROOT / "config.example.yml").read_text(encoding="utf-8")
        self.assertIn("buttondown", config_example)
        self.assertNotIn("BUTTONDOWN_API_KEY", config_example)

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
        self.assertIn("Automatic branded delivery is intentionally paused", advanced)
        self.assertIn("workflow is currently manual-only", advanced)
        self.assertIn("there is no active `schedule` trigger", advanced)
        self.assertNotIn("checked-in scheduled workflow currently runs", advanced)


if __name__ == "__main__":
    unittest.main()

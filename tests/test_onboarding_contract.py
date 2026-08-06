sed: --: No such file or directory
import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class PublicContractTests(unittest.TestCase):
    def test_readme_has_only_subscribe_and_private_paths(self):
        readme = (ROOT / "README.md").read_text(encoding="utf-8")
        self.assertEqual(readme.count("## Subscribe\n"), 1)
        self.assertEqual(readme.count("## Run privately\n"), 1)
        self.assertIn("https://buttondown.com/kindofnews", readme)
        self.assertIn(
            "Install Kind of News from https://github.com/isolovyova/kind-of-news and generate a personalized issue for me now.",
            readme,
        )
        for phrase in (
            "Collects fresh sources.",
            "Generates the newsletter with AI.",
            "Validates the four content blocks and their source links.",
            "Publishes the validated issue through the Buttondown API.",
            "Buttondown delivers it to subscribers.",
        ):
            self.assertIn(phrase, readme)
        self.assertIn("exactly one native", readme)
        self.assertIn("does not generate a second welcome", readme)
        self.assertNotIn("author path", readme.lower())
        self.assertNotIn("setup wizard", readme.lower())
        self.assertNotIn("personal delivery", readme.lower())
        self.assertNotIn("Gmail", readme)
        self.assertNotIn("Telegram", readme)
        self.assertNotIn("webhook", readme.lower())

    def test_readme_contains_one_four_block_sourced_example(self):
        readme = (ROOT / "README.md").read_text(encoding="utf-8")
        example = readme.split("## Example issue", 1)[1].split("## License", 1)[0]
        headings = [line for line in example.splitlines() if line.startswith("### ")]
        self.assertEqual(len(headings), 4)
        self.assertIn("This is a compact sourced example", example)
        self.assertIn("Sources:", example)
        self.assertEqual(example.count("https://"), 3)
        self.assertNotIn("Welcome Issue", example)

    def test_single_private_skill_and_manifests_are_v01(self):
        skill = (ROOT / "skills" / "kind-of-news" / "SKILL.md").read_text(encoding="utf-8")
        self.assertIn("exactly these four content blocks", skill)
        self.assertIn("display the finished", skill)
        self.assertIn("save a local Markdown copy only when", skill)
        for stale in (
            "kind-of-news-setup",
            "setup wizard",
            "author path",
            "personal delivery",
            "Gmail",
            "Telegram",
            "webhook",
            "LinkedIn",
        ):
            self.assertNotIn(stale.lower(), skill.lower())

        codex = json.loads((ROOT / ".codex-plugin" / "plugin.json").read_text(encoding="utf-8"))
        self.assertEqual(codex["version"], "0.1.0")
        self.assertEqual(codex["skills"], "./skills/")
        self.assertEqual(len(codex["interface"]["defaultPrompt"]), 3)
        self.assertNotIn("setup", codex["description"].lower())

        marketplace = json.loads(
            (ROOT / ".claude-plugin" / "marketplace.json").read_text(encoding="utf-8")
        )
        self.assertEqual(marketplace["metadata"]["version"], "0.1.0")
        self.assertEqual(len(marketplace["plugins"]), 1)
        plugin = marketplace["plugins"][0]
        self.assertEqual(plugin["version"], "0.1.0")
        self.assertEqual(plugin["source"]["source"], "git-subdir")
        self.assertEqual(plugin["source"]["path"], "skills")

        claude = json.loads(
            (ROOT / "skills" / ".claude-plugin" / "plugin.json").read_text(encoding="utf-8")
        )
        self.assertEqual(claude["version"], "0.1.0")
        self.assertEqual(claude["skills"], "./")
        self.assertTrue((ROOT / "skills" / "kind-of-news" / "SKILL.md").is_file())
        self.assertFalse((ROOT / "skills" / "kind-of-news-setup").exists())

    def test_private_install_doc_has_one_skill_path(self):
        docs = (ROOT / "docs" / "codex-cowork-setup.md").read_text(encoding="utf-8")
        self.assertIn("/plugin marketplace add https://github.com/isolovyova/kind-of-news.git", docs)
        self.assertIn("/plugin install kind-of-news@kind-of-news --scope user", docs)
        self.assertIn("/kind-of-news:kind-of-news", docs)
        self.assertNotIn("kind-of-news-setup", docs)
        self.assertNotIn("Gmail", docs)
        self.assertNotIn("Telegram", docs)

    def test_workflow_has_mwf_schedule_and_buttondown_secrets_only(self):
        workflow = (ROOT / ".github" / "workflows" / "kind-of-news.yml").read_text(
            encoding="utf-8"
        )
        self.assertIn("schedule:", workflow)
        self.assertIn('cron: "0 6 * * 1,3,5"', workflow)
        self.assertIn('timezone: "America/Vancouver"', workflow)
        self.assertIn("BUTTONDOWN_API_KEY: ${{ secrets.BUTTONDOWN_API_KEY }}", workflow)
        self.assertIn("OPENAI_API_KEY: ${{ secrets.OPENAI_API_KEY }}", workflow)
        for stale in ("GMAIL_", "TELEGRAM_", "WEBHOOK_URL", "Automatic delivery is paused"):
            self.assertNotIn(stale, workflow)
        self.assertFalse((ROOT / ".github" / "workflows" / "kind-of-news-setup.yml").exists())

    def test_runtime_config_and_public_files_are_buttondown_only(self):
        config_example = (ROOT / "config.example.yml").read_text(encoding="utf-8")
        config = (ROOT / "config.yml").read_text(encoding="utf-8")
        for content in (config_example, config):
            self.assertIn("buttondown", content)
            self.assertNotIn("gmail", content.lower())
            self.assertNotIn("telegram", content.lower())
            self.assertNotIn("webhook", content.lower())
        for obsolete in (
            "docs/assistant-setup.md",
            "docs/github-actions-setup.md",
            "docs/buttondown-welcome-issue.md",
            "templates/buttondown-welcome-issue.md",
        ):
            self.assertFalse((ROOT / obsolete).exists())


if __name__ == "__main__":
    unittest.main()

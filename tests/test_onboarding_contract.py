import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class OnboardingContractTests(unittest.TestCase):
    def test_setup_skill_is_a_real_entrypoint(self):
        content = (ROOT / "skills" / "kind-of-news-setup" / "SKILL.md").read_text(
            encoding="utf-8"
        )
        normalized = " ".join(content.split())
        self.assertIn("do not stop at “installed”", normalized)
        self.assertIn("Where would you like to receive it", content)
        self.assertIn("If the user says “dry run only”", content)
        self.assertIn("Create the host's recurring automation only after the user confirms", content)

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
        self.assertIn("immediately start its setup tutorial", prompt)
        self.assertIn("Do not ask me to create a GitHub repository", prompt)


if __name__ == "__main__":
    unittest.main()

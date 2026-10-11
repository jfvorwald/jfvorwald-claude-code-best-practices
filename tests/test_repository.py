import re
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
AGENTS = ROOT / ".claude" / "agents"
SKILLS = ROOT / ".claude" / "skills"


class RepositoryLayoutTest(unittest.TestCase):
    def test_expected_agents_have_frontmatter_and_local_hooks(self):
        expected = {
            "code-reviewer",
            "cto",
            "debugger",
            "docs-writer",
            "implementer",
            "security-reviewer",
            "test-writer",
        }
        files = {path.stem: path for path in AGENTS.glob("*.md")}
        self.assertEqual(expected, set(files))

        for name, path in files.items():
            text = path.read_text()
            self.assertTrue(text.startswith("---\n"), path)
            self.assertIn(f"\nname: {name}\n", text, path)
            self.assertRegex(text, r"\ndescription: .+\n")
            self.assertIn("\ntools:", text, path)
            if "hooks:" in text:
                self.assertIn("${CLAUDE_PROJECT_DIR}/.claude/hooks/agent-guard.py", text, path)

    def test_readme_local_links_exist(self):
        readme = (ROOT / "README.md").read_text()
        links = re.findall(r"\[[^]]+\]\(([^)]+)\)", readme)
        local_links = [link for link in links if "://" not in link and not link.startswith("#")]
        missing = [link for link in local_links if not (ROOT / link.split("#", 1)[0]).exists()]
        self.assertEqual([], missing)

class SkillLayoutTest(unittest.TestCase):
    def skill_files(self):
        return sorted(SKILLS.glob("*/SKILL.md"))

    def test_setup_skill_exists(self):
        names = {path.parent.name for path in self.skill_files()}
        self.assertIn("bootstrapping-my-workflow", names)

    def test_skills_have_trigger_only_descriptions(self):
        for path in self.skill_files():
            text = path.read_text()
            self.assertTrue(text.startswith("---\n"), path)
            self.assertIn(f"\nname: {path.parent.name}\n", text, path)
            match = re.search(r"\ndescription: (.+)\n", text)
            self.assertIsNotNone(match, path)
            self.assertTrue(match.group(1).startswith("Use when"), path)
            self.assertLess(len(match.group(1)), 500, path)

    def test_skill_files_are_portable_and_follow_the_style_rule(self):
        for path in SKILLS.rglob("*.md"):
            text = path.read_text()
            self.assertNotIn("\u2014", text, f"em dash in {path}")
            self.assertNotRegex(text, r"/Users/|@gmail\.com|rally-wt", f"private detail in {path}")

    def test_skill_local_links_exist(self):
        for path in SKILLS.rglob("*.md"):
            links = re.findall(r"\[[^]]+\]\(([^)]+)\)", path.read_text())
            local = [link for link in links if "://" not in link and not link.startswith("#")]
            missing = [link for link in local if not (path.parent / link.split("#", 1)[0]).exists()]
            self.assertEqual([], missing, path)


if __name__ == "__main__":
    unittest.main()

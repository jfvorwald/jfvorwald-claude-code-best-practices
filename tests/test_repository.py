import re
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
AGENTS = ROOT / ".claude" / "agents"


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


if __name__ == "__main__":
    unittest.main()

import importlib.util
import json
import subprocess
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
GUARD = ROOT / ".claude" / "hooks" / "agent-guard.py"


def load_guard():
    spec = importlib.util.spec_from_file_location("agent_guard", GUARD)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


guard = load_guard()


class AgentGuardTest(unittest.TestCase):
    def invoke(self, mode, tool_name, tool_input):
        return subprocess.run(
            [str(GUARD), mode],
            input=json.dumps({"tool_name": tool_name, "tool_input": tool_input}),
            text=True,
            capture_output=True,
            check=False,
        )

    def test_readonly_git_allows_inspection(self):
        self.assertTrue(guard.readonly_git("git status --short"))
        self.assertTrue(guard.readonly_git("git -C /tmp/example diff --stat"))
        self.assertTrue(guard.readonly_git("git log -5 --oneline"))

    def test_readonly_git_rejects_writes_and_shell_control(self):
        self.assertFalse(guard.readonly_git("git commit -m nope"))
        self.assertFalse(guard.readonly_git("git diff --output=review.txt"))
        self.assertFalse(guard.readonly_git("git status > status.txt"))
        self.assertFalse(guard.readonly_git("git -c alias.x='!touch nope' x"))
        self.assertFalse(guard.readonly_git("git grep -O /tmp/pager needle"))
        self.assertFalse(guard.readonly_git("git grep --open-files-in-pager=evil needle"))

    def test_worker_commands_allow_checks_not_arbitrary_shell(self):
        self.assertTrue(guard.worker_command("python3 -m pytest tests/test_api.py"))
        self.assertTrue(guard.worker_command("pnpm run typecheck"))
        self.assertTrue(guard.worker_command("rg TODO src"))
        self.assertFalse(guard.worker_command("python3 -c 'open(\"x\", \"w\")'"))
        self.assertFalse(guard.worker_command("sed -i '' s/a/b/ tests/test_api.py"))
        self.assertFalse(guard.worker_command("find tests -delete"))

    def test_implementer_cannot_write_tests(self):
        blocked = self.invoke("protect-tests", "Edit", {"file_path": "tests/test_api.py"})
        allowed = self.invoke("protect-tests", "Edit", {"file_path": "src/api.py"})
        self.assertEqual(2, blocked.returncode)
        self.assertEqual(0, allowed.returncode)

    def test_test_writer_cannot_write_source(self):
        blocked = self.invoke("tests-only-write", "Write", {"file_path": "src/api.py"})
        allowed = self.invoke("tests-only-write", "Write", {"file_path": "src/api.test.ts"})
        self.assertEqual(2, blocked.returncode)
        self.assertEqual(0, allowed.returncode)

    def test_docs_writer_is_limited_to_docs(self):
        blocked = self.invoke("docs-only-write", "Edit", {"file_path": "src/api.ts"})
        allowed = self.invoke("docs-only-write", "Edit", {"file_path": "docs/api.md"})
        self.assertEqual(2, blocked.returncode)
        self.assertEqual(0, allowed.returncode)

    def test_cto_cannot_spawn_cto(self):
        blocked = self.invoke("no-cto-spawn", "Agent", {"subagent_type": "cto"})
        allowed = self.invoke("no-cto-spawn", "Agent", {"subagent_type": "implementer"})
        self.assertEqual(2, blocked.returncode)
        self.assertEqual(0, allowed.returncode)

    def test_malformed_input_fails_closed(self):
        result = subprocess.run(
            [str(GUARD), "readonly-bash"],
            input="not json",
            text=True,
            capture_output=True,
            check=False,
        )
        self.assertEqual(2, result.returncode)


if __name__ == "__main__":
    unittest.main()

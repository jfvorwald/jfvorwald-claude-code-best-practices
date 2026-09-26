#!/usr/bin/env python3
"""Fail-closed capability checks for the example Claude Code subagents."""

from __future__ import annotations

import json
import os
import re
import shlex
import sys
from pathlib import PurePath
from typing import Any


TEST_PATH = re.compile(
    r"(^|/)(tests?|__tests__|__snapshots__|testdata|fixtures)(/|$)"
    r"|(^|/)(test_[^/]+\.py|[^/]+_(test|spec)\.[^/]+|[^/]+\.(test|spec)\.[^/]+|[^/]+_test\.go)$",
    re.IGNORECASE,
)
DOC_PATH = re.compile(r"(^|/)(docs?|documentation)(/|$)", re.IGNORECASE)
SHELL_CONTROL = re.compile(r"[\n\r;|&<>`]|\$\(|\$\{")
WRITE_FLAGS = (
    "--output",
    "--ext-diff",
    "--textconv",
    "--exec",
    "--format-patch",
    "--open-files-in-pager",
    "-O",
)
READONLY_GIT = {
    "status",
    "diff",
    "log",
    "show",
    "rev-parse",
    "merge-base",
    "ls-files",
    "grep",
    "describe",
    "name-rev",
}
READ_COMMANDS = {
    "pwd",
    "ls",
    "rg",
    "grep",
    "head",
    "tail",
    "wc",
    "file",
}


def deny(message: str) -> int:
    print(f"Blocked by agent guard: {message}", file=sys.stderr)
    return 2


def normalized_path(value: str) -> str:
    return str(PurePath(value.replace("\\", "/"))).lower()


def is_test_path(value: str) -> bool:
    return bool(TEST_PATH.search(normalized_path(value)))


def is_doc_path(value: str) -> bool:
    path = normalized_path(value)
    name = PurePath(path).name
    return bool(DOC_PATH.search(path)) or name.endswith(".md") or name in {
        "readme",
        "readme.txt",
        "changelog",
        "changelog.txt",
        "license",
        "license.txt",
    }


def input_paths(tool_input: dict[str, Any]) -> list[str]:
    paths: list[str] = []
    for key in ("file_path", "path", "notebook_path"):
        value = tool_input.get(key)
        if isinstance(value, str):
            paths.append(value)
    return paths


def split_command(command: str) -> list[str] | None:
    if not command.strip() or SHELL_CONTROL.search(command):
        return None
    try:
        return shlex.split(command)
    except ValueError:
        return None


def git_subcommand(tokens: list[str]) -> tuple[str, list[str]] | None:
    if not tokens or os.path.basename(tokens[0]) != "git":
        return None
    index = 1
    while index < len(tokens):
        token = tokens[index]
        if token == "-C":
            index += 2
            continue
        if token == "--no-pager":
            index += 1
            continue
        if token.startswith("-"):
            return None
        return token, tokens[index + 1 :]
    return None


def readonly_git(command: str) -> bool:
    tokens = split_command(command)
    if tokens is None:
        return False
    parsed = git_subcommand(tokens)
    if parsed is None:
        return False
    subcommand, arguments = parsed
    if subcommand == "branch":
        return bool(arguments) and all(
            arg in {"--show-current", "--list", "-l", "-r", "-a"}
            or not arg.startswith("-")
            for arg in arguments
        ) and any(arg in {"--show-current", "--list", "-l"} for arg in arguments)
    if subcommand not in READONLY_GIT:
        return False
    return not any(arg.startswith(WRITE_FLAGS) for arg in arguments)


def worker_command(command: str) -> bool:
    if readonly_git(command):
        return True
    tokens = split_command(command)
    if not tokens:
        return False
    executable = os.path.basename(tokens[0])
    arguments = tokens[1:]
    if executable in READ_COMMANDS:
        return True
    if executable in {"pytest", "vitest", "jest", "rspec"}:
        return True
    if executable in {"python", "python3"}:
        return len(arguments) >= 2 and arguments[0] == "-m" and arguments[1] in {"pytest", "unittest"}
    if executable in {"npm", "pnpm", "yarn", "bun"}:
        allowed = {"test", "check", "lint", "typecheck", "build"}
        words = [arg for arg in arguments if not arg.startswith("-")]
        if not words:
            return False
        if words[0] in allowed:
            return True
        return len(words) >= 2 and words[0] in {"run", "exec"} and words[1] in allowed | {"vitest", "jest", "tsc"}
    if executable in {"cargo", "go"}:
        return bool(arguments) and arguments[0] == "test"
    if executable in {"make", "just"}:
        return bool(arguments) and all(arg in {"test", "check", "lint", "typecheck", "build"} for arg in arguments)
    return executable in {"check.sh", "verify.sh"} or command.strip().endswith("/.claude/check.sh")


def find_agent_type(value: Any) -> str | None:
    if isinstance(value, dict):
        for key in ("subagent_type", "agent_type", "agent", "name"):
            candidate = value.get(key)
            if isinstance(candidate, str):
                return candidate
        for nested in value.values():
            found = find_agent_type(nested)
            if found is not None:
                return found
    elif isinstance(value, list):
        for nested in value:
            found = find_agent_type(nested)
            if found is not None:
                return found
    return None


def run(mode: str, payload: dict[str, Any]) -> int:
    tool_name = payload.get("tool_name", "")
    tool_input = payload.get("tool_input", {})
    if not isinstance(tool_input, dict):
        return deny("hook input has no tool_input object")

    if mode == "readonly-bash":
        command = tool_input.get("command", "")
        if tool_name != "Bash" or not isinstance(command, str) or not readonly_git(command):
            return deny("review agents may run only approved read-only Git commands")
        return 0

    if mode == "worker-bash":
        command = tool_input.get("command", "")
        if tool_name != "Bash" or not isinstance(command, str) or not worker_command(command):
            return deny("worker Bash is limited to read, test, lint, typecheck, and build commands")
        return 0

    if mode == "protect-tests":
        paths = input_paths(tool_input)
        if not paths:
            return deny("cannot identify the file targeted by the write")
        if any(is_test_path(path) for path in paths):
            return deny("the implementer cannot modify tests")
        return 0

    if mode == "tests-only-write":
        paths = input_paths(tool_input)
        if not paths or any(not is_test_path(path) for path in paths):
            return deny("the test-writer may modify only test files and test fixtures")
        return 0

    if mode == "docs-only-write":
        paths = input_paths(tool_input)
        if not paths or any(not is_doc_path(path) for path in paths):
            return deny("the docs-writer may modify only Markdown or documentation paths")
        return 0

    if mode == "no-cto-spawn":
        agent_type = find_agent_type(tool_input)
        if agent_type is None:
            return deny("cannot identify the requested subagent type")
        if agent_type == "cto" or agent_type.endswith(":cto"):
            return deny("a CTO may not spawn another CTO")
        return 0

    return deny(f"unknown guard mode {mode!r}")


def main() -> int:
    if len(sys.argv) != 2:
        return deny("expected exactly one guard mode")
    try:
        payload = json.load(sys.stdin)
    except (json.JSONDecodeError, OSError) as error:
        return deny(f"invalid hook JSON: {error}")
    if not isinstance(payload, dict):
        return deny("hook input must be a JSON object")
    return run(sys.argv[1], payload)


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
"""Regenerate .codex/agents/*.toml from .claude/agents/*.md.

The Claude role files are the source. Each Codex mirror carries the role's
name, description, and body as developer_instructions. Model and effort are
not written as TOML keys: whether a Codex agent role file accepts them was not
verified, so the body's "Runtime selection" section carries the mapping and the
launch sets it.

Usage: sync_codex_agents.py [--check]
  --check  exit 1 if any mirror differs from what would be generated.
"""

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / ".claude" / "agents"
TARGET = ROOT / ".codex" / "agents"

HEADER = (
    "# Generated from .claude/agents/{name}.md by scripts/sync_codex_agents.py.\n"
    "# Edit the source file, then rerun the script.\n"
)


def render(path):
    text = path.read_text()
    if not text.startswith("---\n"):
        raise ValueError(f"{path}: missing frontmatter")
    front, body = text[4:].split("\n---\n", 1)
    name = re.search(r"^name: (.+)$", front, re.M).group(1).strip()
    description = re.search(r"^description: (.+)$", front, re.M).group(1).strip()
    body = body.strip("\n")
    for value in (name, description, body):
        if "\\" in value or '"""' in value:
            raise ValueError(f"{path}: text needs TOML escaping; extend the script")
    if '"' in name or '"' in description:
        raise ValueError(f"{path}: quote in name or description; extend the script")
    return (
        HEADER.format(name=name)
        + f'name = "{name}"\n'
        + f'description = "{description}"\n'
        + f'developer_instructions = """\n{body}\n"""\n'
    )


def main(argv):
    check = "--check" in argv
    TARGET.mkdir(parents=True, exist_ok=True)
    stale = []
    sources = sorted(SOURCE.glob("*.md"))
    expected = {path.stem + ".toml" for path in sources}
    for path in sources:
        out = TARGET / (path.stem + ".toml")
        rendered = render(path)
        if not out.exists() or out.read_text() != rendered:
            stale.append(out.name)
            if not check:
                out.write_text(rendered)
    extra = sorted(p.name for p in TARGET.glob("*.toml") if p.name not in expected)
    if check:
        if stale or extra:
            print("Codex mirrors out of date: " + ", ".join(stale + extra))
            return 1
        print(f"Codex mirrors match {len(sources)} role files.")
        return 0
    for name in extra:
        print(f"Not generated from a role file, left in place: {name}")
    print(f"Wrote {len(stale)} of {len(sources)} Codex mirrors.")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))

#!/usr/bin/env sh
set -eu
export PYTHONDONTWRITEBYTECODE=1

repo_root=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
cd "$repo_root"

test -x .claude/hooks/agent-guard.py
python3 -m unittest discover -s tests -p 'test_*.py'

for agent in .claude/agents/*.md; do
  grep -q '^name:' "$agent"
  grep -q '^description:' "$agent"
done

printf 'Verified %s agent definitions.\n' "$(find .claude/agents -name '*.md' | wc -l | tr -d ' ')"
if command -v claude >/dev/null 2>&1; then
  claude --version
fi
